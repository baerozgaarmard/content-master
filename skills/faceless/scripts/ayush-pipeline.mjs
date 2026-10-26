#!/usr/bin/env node
/**
 * Ayush Pipeline - Autonomous Viral Reel Production Engine (v2.0)
 * 
 * Pipeline Standards & Upgrades:
 *  1. Natural Human Conversational Pace: Peter Griffin Delik RVC v2 (PyWorld Harvest) & Stewie Griffin tuned to natural human speaking pace (rate="+0%").
 *  2. Microsecond Subtitle Synchronization: Direct word boundary streaming (boundary='WordBoundary') outputting exact onset/offset word timestamps into .words.json for zero-drift, pause-aware captions.
 *  3. Mandatory Closing Call-to-Action: Guarantees closing dialogue line and cards end with "Follow for more such content!".
 *  4. Zero Hidden Info Standard: Automatically links and renders genuine, raw browser screenshots of GitHub (owner, star count, commits, code, and UI).
 *  5. Clean Anti-AI-Slop Thumbnail: 1080x1920 viral cover with real repository centerpiece, clean desktop framing, bold typography, and zero synthetic pill boxes or fake badges.
 *  6. Turnkey Multi-Platform SEO Package: Viral title, hook, description, and 4 high-reach hashtags.
 */

import {spawn} from 'node:child_process';
import {existsSync} from 'node:fs';
import {access, mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, join, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Root repository directory: resolves to content-master
const ROOT_DIR = resolve(__dirname, '..', '..', '..');
const AI_ENV_PYTHON = join(ROOT_DIR, '.ai_env', 'Scripts', 'python.exe');
const PYTHON_CMD = existsSync(AI_ENV_PYTHON) ? AI_ENV_PYTHON : (process.platform === 'win32' ? 'py' : 'python3');

function parseArguments(args) {
  const options = {
    topic: 'omniroute',
    output: join(ROOT_DIR, 'faceless-output'),
    template: join(ROOT_DIR, 'packages', 'faceless', 'skills', 'faceless', 'video-templates', 'minecraft_hd_new.mp4'),
    overlays: null,
    screenshot: null,
    title1: null,
    title2: null,
    force: false,
    skipAudio: false,
    skipAlign: false,
    skipVideo: false,
    skipCover: false,
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--topic') options.topic = args[++i];
    else if (arg === '--script' || arg === '--dialogue') options.dialogue = args[++i];
    else if (arg === '--template') options.template = args[++i];
    else if (arg === '--overlays') options.overlays = args[++i];
    else if (arg === '--screenshot') options.screenshot = args[++i];
    else if (arg === '--title1') options.title1 = args[++i];
    else if (arg === '--title2') options.title2 = args[++i];
    else if (arg === '--output') options.output = resolve(args[++i]);
    else if (arg === '--force') options.force = true;
    else if (arg === '--skip-audio') options.skipAudio = true;
    else if (arg === '--skip-align') options.skipAlign = true;
    else if (arg === '--skip-video') options.skipVideo = true;
    else if (arg === '--skip-cover') options.skipCover = true;
  }
  return options;
}

function runCommand(command, args, options = {}) {
  return new Promise((resolvePromise, rejectPromise) => {
    console.log(`\n[Ayush Pipeline] > ${command} ${args.join(' ')}`);
    const child = spawn(command, args, {
      cwd: options.cwd || ROOT_DIR,
      stdio: 'inherit',
      shell: false,
    });
    child.on('error', (err) => rejectPromise(err));
    child.on('exit', (code) => {
      if (code === 0) resolvePromise();
      else rejectPromise(new Error(`Command failed with exit code ${code}`));
    });
  });
}

async function main() {
  const options = parseArguments(process.argv.slice(2));
  console.log('====================================================');
  console.log('              AYUSH PIPELINE v2.0.0                 ');
  console.log('  Autonomous Viral Faceless Reel Production Engine  ');
  console.log('  (Natural Speech • Exact Word Sync • Anti-Slop)   ');
  console.log('====================================================');
  console.log(`Topic: ${options.topic}`);
  console.log(`Workspace Root: ${ROOT_DIR}`);
  console.log(`Output Directory: ${options.output}`);

  // 1. Resolve dialogue script
  let dialoguePath = options.dialogue;
  if (!dialoguePath) {
    const candidates = [
      join(ROOT_DIR, 'faceless-output', 'scripts', options.topic, 'dialogue.json'),
      join(ROOT_DIR, 'skills', 'faceless', 'dialogue', `${options.topic}.json`),
      join(ROOT_DIR, 'packages', 'faceless', 'skills', 'faceless', 'dialogue', `${options.topic}.json`),
      join(ROOT_DIR, 'faceless-output', 'dialogue', options.topic, 'dialogue.json'),
    ];
    for (const cand of candidates) {
      if (existsSync(cand)) {
        dialoguePath = cand;
        break;
      }
    }
  }

  if (!dialoguePath || !existsSync(dialoguePath)) {
    throw new Error(`Dialogue file not found for topic "${options.topic}". Please specify with --script <path>.`);
  }
  console.log(`Dialogue Script: ${dialoguePath}`);

  // 2. Validate & Enforce Mandatory Closing CTA Standard
  try {
    const scriptContent = JSON.parse(await readFile(dialoguePath, 'utf8'));
    if (Array.isArray(scriptContent) && scriptContent.length > 0) {
      const lastLine = scriptContent[scriptContent.length - 1];
      if (lastLine && !lastLine.text.toLowerCase().includes('follow for more')) {
        console.log('[Ayush Pipeline Standard] Appending mandatory closing CTA: "Follow for more such content!"');
        lastLine.text = lastLine.text.replace(/[.!?,]*$/, '') + '. Follow for more such content!';
        await writeFile(dialoguePath, JSON.stringify(scriptContent, null, 2), 'utf8');
      }
    }
  } catch (err) {
    console.warn(`[Ayush Pipeline Warning] Script validation notice: ${err.message}`);
  }

  const audioDir = join(options.output, 'audio', options.topic);
  const videoDir = join(options.output, 'video', options.topic);
  const thumbsDir = join(options.output, 'thumbnails', options.topic);
  const fullAudioPath = join(audioDir, 'full-dialogue.mp3');
  const chunksPath = join(videoDir, 'caption-chunks.json');
  const finalReelPath = join(videoDir, 'final-faceless-reel.mp4');
  const coverPath = join(thumbsDir, 'cover.png');

  await mkdir(audioDir, {recursive: true});
  await mkdir(videoDir, {recursive: true});
  await mkdir(thumbsDir, {recursive: true});

  // STEP 1: VOICE SYNTHESIS (Natural Delik RVC v2 + PyWorld Harvest + Word Boundaries)
  if (!options.skipAudio) {
    console.log('\n--- [Step 1/5] Synthesizing Voice Lines (Delik RVC v2 + Harvest @ Natural Pace rate=+0%) ---');
    const generateAudioScript = join(ROOT_DIR, 'skills', 'faceless', 'scripts', 'generate-audio.mjs');
    const audioArgs = [
      generateAudioScript,
      '--script', dialoguePath,
      '--topic', options.topic,
      '--output', options.output,
    ];
    if (options.force) {
      audioArgs.push('--force', 'true');
    }
    await runCommand(process.execPath, audioArgs);
  } else {
    console.log('\n--- [Step 1/5] Audio synthesis skipped (--skip-audio) ---');
  }

  // STEP 2: MICROSECOND SUBTITLE ALIGNMENT (WordBoundary Timestamps)
  if (!options.skipAlign) {
    console.log('\n--- [Step 2/5] Running Subtitle Alignment (True WordBoundary Timestamps) ---');
    const alignScript = join(ROOT_DIR, 'skills', 'faceless', 'scripts', 'align-dialogue.py');
    await runCommand(PYTHON_CMD, [
      alignScript,
      '--root', ROOT_DIR,
      '--dialogue', dialoguePath,
      '--audio', audioDir,
      '--topic', options.topic,
      '--output', chunksPath,
    ]);
  } else {
    console.log('\n--- [Step 2/5] Acoustic alignment skipped (--skip-align) ---');
  }

  // STEP 3: HIGH-IMPACT 60 FPS HD VIDEO RENDERING WITH REAL OVERLAYS
  if (!options.skipVideo) {
    console.log('\n--- [Step 3/5] Compositing 60 FPS HD Video, Captions & Genuine GitHub Screenshots ---');
    let overlaysFile = options.overlays;
    if (!overlaysFile) {
      const candidateOverlays = [
        join(ROOT_DIR, 'assets', 'overlays', `${options.topic}_overlays.json`),
        join(ROOT_DIR, 'assets', 'overlays', options.topic, 'overlays.json'),
      ];
      for (const cand of candidateOverlays) {
        if (existsSync(cand)) {
          overlaysFile = cand;
          break;
        }
      }
    }

    const renderScript = join(ROOT_DIR, 'skills', 'faceless', 'scripts', 'render-faceless-reel.mjs');
    const renderArgs = [
      renderScript,
      '--topic', options.topic,
      '--output', options.output,
      '--template', options.template,
    ];
    if (overlaysFile && existsSync(overlaysFile)) {
      renderArgs.push('--overlays', overlaysFile);
      console.log(`Using Overlay Sequence: ${overlaysFile}`);
    }
    await runCommand(process.execPath, renderArgs);
  } else {
    console.log('\n--- [Step 3/5] Video rendering skipped (--skip-video) ---');
  }

  // STEP 4: CLEAN ANTI-AI-SLOP 1080x1920 COVER GENERATION
  if (!options.skipCover) {
    console.log('\n--- [Step 4/5] Generating Clean Real-Repo Viral 1080x1920 Cover Image ---');
    const coverScript = join(ROOT_DIR, 'skills', 'faceless', 'scripts', 'generate-cover.py');
    const coverArgs = [
      coverScript,
      '--topic', options.topic,
      '--output', coverPath,
    ];

    // Auto-detect genuine screenshot centerpiece
    let shotPath = options.screenshot;
    if (!shotPath) {
      const candidates = [
        join(ROOT_DIR, 'assets', 'overlays', `${options.topic}_real`, 'real_repo_main.png'),
        join(ROOT_DIR, 'assets', 'overlays', options.topic, 'real_card_01_repo_main.png'),
        join(ROOT_DIR, 'assets', 'overlays', `${options.topic}_real`, 'real_repo_files.png'),
      ];
      for (const cand of candidates) {
        if (existsSync(cand)) {
          shotPath = cand;
          break;
        }
      }
    }
    if (shotPath && existsSync(shotPath)) {
      coverArgs.push('--screenshot', shotPath);
      console.log(`Cover Real Screenshot Centerpiece: ${shotPath}`);
    }
    if (options.title1) coverArgs.push('--title1', options.title1);
    if (options.title2) coverArgs.push('--title2', options.title2);

    await runCommand(PYTHON_CMD, coverArgs);
  } else {
    console.log('\n--- [Step 4/5] Cover generation skipped (--skip-cover) ---');
  }

  // STEP 5: VIRAL SEO PACKAGE
  console.log('\n--- [Step 5/5] Generating Multi-Platform SEO Package ---');
  const existingSeoPath = join(options.output, 'seo', `${options.topic}-seo.json`);
  let seoData = null;
  if (existsSync(existingSeoPath)) {
    try {
      seoData = JSON.parse(await readFile(existingSeoPath, 'utf8'));
    } catch {}
  }

  if (!seoData) {
    const formattedTopic = options.topic.split('-').map((s) => s.charAt(0).toUpperCase() + s.slice(1)).join(' ');
    seoData = {
      title: `The Open-Source ${formattedTopic} Secret Developers Need to Know! 🚀`,
      seo_hook: `Stop paying high prices for developer tools! Discover the open-source repository ${formattedTopic}.`,
      caption: `Discover ${formattedTopic} on GitHub! Search the repository, star the project, and unlock top-tier developer performance without blowing your budget. Follow for more such content! 🔥`,
      hashtags: [
        `#${options.topic.replace(/[^a-zA-Z0-9]/g, '')}`,
        '#OpenSource',
        '#DeveloperTools',
        '#CodingHacks'
      ],
      call_to_action: 'Follow for more such content and check out the repository on GitHub!',
    };
  }

  seoData.files = {
    video: finalReelPath,
    audio: fullAudioPath,
    cover: coverPath,
    subtitles: chunksPath,
  };
  seoData.updatedAt = new Date().toISOString();

  const seoPackagePath = join(options.output, 'seo', `${options.topic}-seo.json`);
  await mkdir(dirname(seoPackagePath), {recursive: true});
  await writeFile(seoPackagePath, JSON.stringify(seoData, null, 2), 'utf8');

  console.log('\n====================================================');
  console.log('      AYUSH PIPELINE COMPLETED SUCCESSFULLY!        ');
  console.log('====================================================');
  console.log(`🎬 Video Reel:    ${finalReelPath}`);
  console.log(`🎙️ Master Audio:  ${fullAudioPath}`);
  console.log(`🖼️ Viral Cover:   ${coverPath}`);
  console.log(`📊 SEO Package:   ${seoPackagePath}`);
  console.log('====================================================\n');
}

main().catch((err) => {
  console.error('\n[Ayush Pipeline Error]:', err.message);
  process.exit(1);
});
