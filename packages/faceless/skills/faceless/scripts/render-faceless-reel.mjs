#!/usr/bin/env node
import {spawn} from 'node:child_process';
import {access, mkdir, readdir, readFile, rename, rm, stat, writeFile} from 'node:fs/promises';
import {dirname, join, resolve, isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
import {ensureFfmpeg} from './ffmpeg.mjs';

const CHARACTER_BY_VOICE = new Map([
  ['fdffd3722cd040fcb3f95eec5a7f29f3', {file: 'Stewie.png', side: 'left'}],
  ['e34b4e061b874623a08f41e5c4fecfb9', {file: 'Peter.png', side: 'right'}],
  ['3d445d095ba04681bcba7177faedf55a', {file: 'Morty.png', side: 'left'}],
  ['d2e75a3e3fd6419893057c02a375a113', {file: 'Rick.png', side: 'right'}],
]);
const ENTRANCE_SECONDS = 0.18;
const STOP_WORDS = new Set(['a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'for', 'from', 'he', 'her', 'his', 'i', 'if', 'in', 'is', 'it', 'its', 'of', 'on', 'or', 'our', 'so', 'that', 'the', 'their', 'then', 'there', 'they', 'this', 'to', 'was', 'we', 'what', 'when', 'with', 'you', 'your']);

const usage = 'Usage: render-faceless-reel.mjs --topic <topic-slug> --output <faceless-output-directory> [--templates <templates-directory>]';

function parseArguments(argumentList) {
  const options = {};
  for (let index = 0; index < argumentList.length; index += 2) {
    const key = argumentList[index];
    const value = argumentList[index + 1];
    if (!key?.startsWith('--') || !value || value.startsWith('--')) throw new Error(usage);
    options[key.slice(2)] = value;
  }
  return options;
}

function run(executable, argumentList, {captureStderr = false} = {}) {
  return new Promise((resolvePromise, rejectPromise) => {
    const child = spawn(executable, argumentList, {stdio: captureStderr ? ['ignore', 'ignore', 'pipe'] : 'inherit'});
    let stderr = '';
    if (captureStderr) child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('error', () => rejectPromise(new Error('FFmpeg failed during render.')));
    child.on('exit', (code) => resolvePromise({code, stderr}));
  });
}

async function getDuration(executable, filePath) {
  const {stderr} = await run(executable, ['-hide_banner', '-i', filePath], {captureStderr: true});
  const match = stderr.match(/Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)/);
  if (!match) throw new Error(`Could not read duration of ${filePath}.`);
  return Number(match[1]) * 3600 + Number(match[2]) * 60 + Number(match[3]);
}

async function completed(filePath) {
  try {
    return (await stat(filePath)).size > 0;
  } catch {
    return false;
  }
}

function timestamp(value) {
  return Number(value.toFixed(3));
}

function toTimestamp(seconds) {
  const centiseconds = Math.max(0, Math.round(seconds * 100));
  const hours = Math.floor(centiseconds / 360000);
  const minutes = Math.floor((centiseconds % 360000) / 6000);
  const remainder = centiseconds % 6000;
  return `${hours}:${String(minutes).padStart(2, '0')}:${String(Math.floor(remainder / 100)).padStart(2, '0')}.${String(remainder % 100).padStart(2, '0')}`;
}

function normaliseText(text) {
  return text.replace(/^\s*\([^)]*\)\s*/, '').trim();
}

function wordsFrom(text) {
  return normaliseText(text).match(/[A-Za-z0-9]+(?:['’\-][A-Za-z0-9]+)*/g) || [];
}

function groupWords(words) {
  const groups = [];
  for (let index = 0; index < words.length;) {
    const remaining = words.length - index;
    const size = remaining === 4 ? 2 : Math.min(3, remaining);
    groups.push(words.slice(index, index + size));
    index += size;
  }
  return groups;
}

function stressWord(group) {
  const candidates = group.filter((word) => !STOP_WORDS.has(word.toLowerCase()));
  return (candidates.length ? candidates : group).reduce((longest, word) => word.length > longest.length ? word : longest);
}

function escapeAss(value) {
  return value.replace(/\\/g, '\\\\').replace(/{/g, '\\{').replace(/}/g, '\\}');
}

function captionText(group, isPeter = true) {
  const stress = stressWord(group);
  const stressColor = isPeter ? '{\\c&H00D7FF&}' : '{\\c&HFFFF00&}'; // Gold for Peter, Cyan for Stewie
  return group.map((word) => {
    const escaped = escapeAss(word.toUpperCase());
    return word.toUpperCase() === stress.toUpperCase() ? `${stressColor}${escaped}{\\c&HFFFFFF&}` : escaped;
  }).join(' ');
}

function assPath(filePath) {
  return filePath.replace(/\\/g, '/').replace(':', '\\:').replace(/'/g, "\\'");
}

const options = parseArguments(process.argv.slice(2));
if (!options.topic || !options.output) throw new Error(usage);
if (!/^[a-z0-9]+(?:-[a-z0-9]+){0,2}$/.test(options.topic)) {
  throw new Error('Topic must be a lowercase two- or three-word slug.');
}

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const skillDirectory = dirname(scriptDirectory);
const characterDirectory = join(skillDirectory, 'Characters');
const templateDirectory = resolve(options.templates || join(skillDirectory, 'video-templates'));
const outputDirectory = resolve(options.output);

const scriptPath = join(outputDirectory, 'scripts', options.topic, 'dialogue.json');
const audioDirectory = join(outputDirectory, 'audio', options.topic);
const fullAudio = join(audioDirectory, 'full-dialogue.mp3');
const videoDirectory = join(outputDirectory, 'video', options.topic);
const finalVideo = join(videoDirectory, 'final-faceless-reel.mp4');
const temporaryVideo = `${finalVideo}.part.mp4`;
const assFile = join(videoDirectory, 'caption-timing.ass');
const chunkFile = join(videoDirectory, 'caption-chunks.json');

await access(scriptPath);
await access(fullAudio);
const script = JSON.parse(await readFile(scriptPath, 'utf8'));
const manifest = JSON.parse(await readFile(join(audioDirectory, 'audio-manifest.json'), 'utf8'));
if (!Array.isArray(script) || !Array.isArray(manifest.lines) || script.length !== manifest.lines.length) {
  throw new Error('The dialogue JSON and audio manifest must contain the same number of lines.');
}

let templateVideo;
if (options.template) {
  templateVideo = resolve(options.template);
  await access(templateVideo);
} else {
  const templates = (await readdir(templateDirectory, {withFileTypes: true}))
    .filter((entry) => entry.isFile() && /\.(mp4|mov|mkv|webm)$/i.test(entry.name))
    .map((entry) => join(templateDirectory, entry.name));
  if (templates.length === 0) throw new Error(`No video templates found in ${templateDirectory}.`);
  templateVideo = templates[Math.floor(Math.random() * templates.length)];
}

const executable = await ensureFfmpeg();
const totalDuration = await getDuration(executable, fullAudio);

// 1. Build character timeline and caption chunks
let currentTime = 0;
const timeline = [];
let chunks = [];

try {
  chunks = JSON.parse(await readFile(chunkFile, 'utf8'));
  console.log(`Loaded ${chunks.length} acoustically-aligned chunks from ${chunkFile}`);
} catch {
  chunks = [];
}

for (const [position, line] of [...script].sort((a, b) => a.index - b.index).entries()) {
  const character = CHARACTER_BY_VOICE.get(line.voiceId);
  if (!character) throw new Error(`Dialogue line ${line.index} uses an unsupported voice ID.`);

  const audioFile = join(audioDirectory, manifest.lines[position].file);
  await access(audioFile);
  const duration = await getDuration(executable, audioFile);

  const start = timestamp(currentTime);
  const lineEnd = timestamp(Math.min(currentTime + duration, totalDuration));
  timeline.push({...character, index: line.index, start, end: lineEnd});

  if (chunks.length === 0) {
    const groups = groupWords(wordsFrom(line.text));
    const totalWeight = groups.reduce((total, group) => total + group.join('').length, 0);
    let groupStart = currentTime;
    for (const group of groups) {
      const weight = group.join('').length / totalWeight;
      const groupEnd = groupStart + duration * weight;
      chunks.push({
        lineIndex: line.index,
        start: Number(groupStart.toFixed(3)),
        end: Number(groupEnd.toFixed(3)),
        words: group.map((word) => word.toUpperCase()),
        stress: stressWord(group).toUpperCase(),
      });
      groupStart = groupEnd;
    }
  }

  currentTime += duration;
}

if (timeline.length > 0) {
  timeline.at(-1).end = timestamp(totalDuration);
}

await mkdir(videoDirectory, {recursive: true});

// 2. Write ASS captions and chunk JSON
const assLines = [
  '[Script Info]',
  'ScriptType: v4.00+',
  'PlayResX: 1080',
  'PlayResY: 1920',
  'ScaledBorderAndShadow: yes',
  '',
  '[V4+ Styles]',
  'Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding',
  'Style: PeterCaption,Arial Black,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,-1,0,0,0,100,100,0,0,1,12,5,5,60,60,0,1',
  'Style: StewieCaption,Arial Black,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,-1,0,0,0,100,100,0,0,1,12,5,5,60,60,0,1',
  '',
  '[Events]',
  'Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text',
  ...chunks.map((chunk) => {
    const isPeter = chunk.lineIndex % 2 === 0;
    const styleName = isPeter ? 'PeterCaption' : 'StewieCaption';
    return `Dialogue: 0,${toTimestamp(chunk.start)},${toTimestamp(chunk.end)},${styleName},,0,0,0,,{\\an5\\pos(540,960)\\fad(50,50)\\fscx90\\fscy90\\t(0,90,\\fscx100\\fscy100)}${captionText(chunk.words, isPeter)}`;
  }),
];
await writeFile(assFile, `${assLines.join('\n')}\n`, 'utf8');
await writeFile(chunkFile, `${JSON.stringify(chunks, null, 2)}\n`, 'utf8');

// 3. Assemble inputs and filter graph for one-pass render
const inputs = [
  '-stream_loop', '-1',
  '-i', templateVideo,
  '-i', fullAudio,
];

for (const entry of timeline) {
  inputs.push('-loop', '1', '-framerate', '30', '-i', join(characterDirectory, entry.file));
}

const filterSteps = ['[0:v]format=rgba[v0]'];
let currentVideo = 'v0';
for (const [offset, entry] of timeline.entries()) {
  const input = offset + 2; // input 0 is template, input 1 is audio
  const characterVideo = `character${offset}`;
  const nextVideo = `v${offset + 1}`;
  const arrivalEnd = timestamp(entry.start + ENTRANCE_SECONDS);
  const progress = `(1-pow(1-min(1\\,max(0\\,(t-${entry.start})/${ENTRANCE_SECONDS}))\\,3))`;
  const x = entry.side === 'left'
    ? `if(lt(t\\,${arrivalEnd})\\,-w+(w+50)*${progress}\\,50)`
    : `if(lt(t\\,${arrivalEnd})\\,W-(w+50)*${progress}\\,W-w-50)`;
  const enable = `gte(t,${entry.start})*lt(t,${entry.end})`;
  filterSteps.push(`[${input}:v]scale=-1:860[${characterVideo}]`);
  filterSteps.push(`[${currentVideo}][${characterVideo}]overlay=x=${x}:y=H-h:enable='${enable}'[${nextVideo}]`);
  currentVideo = nextVideo;
}

// Optional graphic callouts / visual overlays (e.g. repo cards, price comparisons, follow CTAs)
if (options.overlays) {
  const overlaysPath = resolve(options.overlays);
  const overlays = JSON.parse(await readFile(overlaysPath, 'utf8'));
  let nextInputIndex = 2 + timeline.length;
  for (const [idx, ov] of overlays.entries()) {
    const ovFile = isAbsolute(ov.file) ? ov.file : resolve(dirname(overlaysPath), '..', '..', ov.file);
    await access(ovFile);
    const currentInput = nextInputIndex++;
    inputs.push('-loop', '1', '-framerate', '30', '-i', ovFile);
    const nextVid = `v_ov_${idx}`;
    filterSteps.push(`[${currentVideo}][${currentInput}:v]overlay=x=${ov.x}:y=${ov.y}:enable='gte(t,${ov.start})*lt(t,${ov.end})'[${nextVid}]`);
    currentVideo = nextVid;
  }
}

// Add ASS captions as the final visual filter step
filterSteps.push(`[${currentVideo}]ass=filename='${assPath(assFile)}'[vout]`);

await rm(temporaryVideo, {force: true});
console.log(`Rendering unified reel (${timeline.length} speaker turns, ${chunks.length} caption chunks, ${totalDuration.toFixed(1)}s): ${finalVideo}`);

try {
  const {code} = await run(executable, [
    '-y',
    ...inputs,
    '-filter_complex', filterSteps.join(';'),
    '-map', '[vout]',
    '-map', '1:a:0',
    '-c:v', 'libx264',
    '-crf', '18',
    '-preset', 'fast',
    '-c:a', 'aac',
    '-b:a', '192k',
    '-shortest',
    '-movflags', '+faststart',
    temporaryVideo,
  ]);
  if (code !== 0 || !(await completed(temporaryVideo))) {
    throw new Error('FFmpeg failed to produce the final video.');
  }
  await rename(temporaryVideo, finalVideo);
} finally {
  await rm(temporaryVideo, {force: true});
}

console.log(`Final reel complete: ${finalVideo}`);
