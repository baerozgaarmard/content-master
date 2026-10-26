#!/usr/bin/env node
/**
 * Ayush Pipeline - End-to-End Automated Viral Reel Production System
 * 
 * Pipeline Features:
 *  1. Voice Synthesis: Hugging Face Delik RVC v2 (81.57MB feature index) with PyWorld Harvest pitch engine for deep, natural, authentic Peter Griffin voice + Stewie Griffin RVC v2.
 *  2. Sample-Accurate Audio Stitching: 44.1 kHz mono audio with FFmpeg filter_complex concat.
 *  3. Acoustic Speech Alignment: RMS energy burst detection (energies > 0.015) for zero-drift, pause-aware subtitles without speaker name prefixes.
 *  4. High-Impact Video Compositing: 1080x1920 60 FPS HD Minecraft parkour, 96px bold typography with 12px outline, and genuine GitHub screenshot overlays.
 *  5. Viral Cover & SEO Packaging: 1080x1920 high-CTR cover generation + viral title and 4 hyper-targeted hashtags.
 */

import {spawn} from 'node:child_process';
import {existsSync} from 'node:fs';
import {access, mkdir, readFile, writeFile, stat} from 'node:fs/promises';
import {dirname, join, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Root repository directory
const ROOT_DIR = resolve(__dirname, '..');
const AI_ENV_PYTHON = join(ROOT_DIR, '.ai_env', 'Scripts', 'python.exe');
const PYTHON_CMD = existsSync(AI_ENV_PYTHON) ? AI_ENV_PYTHON : (process.platform === 'win32' ? 'py' : 'python3');

function parseArguments(args) {
  const options = {
    topic: 'prompts-chat',
    output: join(ROOT_DIR, 'faceless-output'),
    template: join(ROOT_DIR, 'packages', 'faceless', 'skills', 'faceless', 'video-templates', 'minecraft_hd_new.mp4'),
    overlays: join(ROOT_DIR, 'assets', 'overlays', 'prompts_chat_overlays.json'),
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
    else if (arg === '--output') options.output = resolve(args[++i]);
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
  console.log('              AYUSH PIPELINE v1.0.0                 ');
  console.log('  Autonomous Viral Faceless Reel Production Engine  ');
  console.log('====================================================');
  console.log(`Topic: ${options.topic}`);
  console.log(`Output Directory: ${options.output}`);

  // Resolve dialogue script
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

  // STEP 1: VOICE SYNTHESIS (Natural Delik RVC v2 + PyWorld Harvest)
  if (!options.skipAudio) {
    console.log('\n--- [Step 1/5] Synthesizing Voice Lines (Delik RVC v2 + PyWorld Harvest) ---');
    const generateAudioScript = join(ROOT_DIR, 'skills', 'faceless', 'scripts', 'generate-audio.mjs');
    await runCommand(process.execPath, [
      generateAudioScript,
      '--script', dialoguePath,
      '--topic', options.topic,
      '--output', options.output,
    ]);
  } else {
    console.log('\n--- [Step 1/5] Audio synthesis skipped (--skip-audio) ---');
  }

  // STEP 2: ACOUSTIC DIALOGUE ALIGNMENT (RMS Energy Speech Bursts)
  if (!options.skipAlign) {
    console.log('\n--- [Step 2/5] Running Acoustic Subtitle Alignment (Zero Drift / Pause-Aware) ---');
    const alignScript = join(ROOT_DIR, 'skills', 'faceless', 'scripts', 'align-dialogue.py');
    await runCommand(PYTHON_CMD, [
      alignScript,
      '--dialogue', dialoguePath,
      '--audio', fullAudioPath,
      '--output', chunksPath,
    ]);
  } else {
    console.log('\n--- [Step 2/5] Acoustic alignment skipped (--skip-align) ---');
  }

  // STEP 3: HIGH-IMPACT 60 FPS HD VIDEO RENDERING
  if (!options.skipVideo) {
    console.log('\n--- [Step 3/5] Compositing 60 FPS HD Video, Captions & Genuine Screenshots ---');
    const renderScript = join(ROOT_DIR, 'skills', 'faceless', 'scripts', 'render-faceless-reel.mjs');
    const renderArgs = [
      renderScript,
      '--topic', options.topic,
      '--output', options.output,
      '--template', options.template,
    ];
    if (options.overlays && existsSync(options.overlays)) {
      renderArgs.push('--overlays', options.overlays);
    }
    await runCommand(process.execPath, renderArgs);
  } else {
    console.log('\n--- [Step 3/5] Video rendering skipped (--skip-video) ---');
  }

  // STEP 4: VIRAL 1080x1920 COVER GENERATION
  if (!options.skipCover) {
    console.log('\n--- [Step 4/5] Generating High-CTR Viral 1080x1920 Cover Image ---');
    const coverScript = [
      join(ROOT_DIR, 'scripts', 'generate-cover.py'),
      join(ROOT_DIR, 'skills', 'faceless', 'scripts', 'generate-cover.py'),
      join(ROOT_DIR, 'assets', 'thumbnails', 'generate_cover.py'),
    ].find((p) => existsSync(p)) || join(ROOT_DIR, 'scripts', 'generate-cover.py');
    const coverArgs = [
      coverScript,
      '--topic', options.topic,
      '--output', coverPath,
    ];
    if (options.overlays && existsSync(options.overlays)) {
      try {
        const overlayData = JSON.parse(await readFile(options.overlays, 'utf8'));
        if (overlayData.overlays && overlayData.overlays.length > 0) {
          coverArgs.push('--screenshot', overlayData.overlays[0].image);
        }
      } catch {
        // use default screenshot
      }
    }
    await runCommand(PYTHON_CMD, coverArgs);
  } else {
    console.log('\n--- [Step 4/5] Cover generation skipped (--skip-cover) ---');
  }

  // STEP 5: VIRAL SEO PACKAGE
  console.log('\n--- [Step 5/5] Generating SEO Title & Hashtag Package ---');
  const seoData = {
    topic: options.topic,
    title: 'Stop Paying for ChatGPT Prompts! (174k Star Secret) 🤫',
    hashtags: ['#chatgpt', '#chatgptprompts', '#ai', '#github'],
    description: 'Stop paying for AI cheat sheets! Peter Griffin and Stewie break down f/prompts.chat, the open-source GitHub repository with 174,000+ stars that gives you every elite ChatGPT prompt for free.',
    files: {
      video: finalReelPath,
      audio: fullAudioPath,
      cover: coverPath,
      subtitles: chunksPath,
    },
    generatedAt: new Date().toISOString(),
  };

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
