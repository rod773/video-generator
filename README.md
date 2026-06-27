# AI Video Generator

A fully automated AI-powered image-to-video generator. Drop images into a folder, write a script, and generate a complete cinematic video with AI voiceover, Ken Burns animations, and synchronized timing — all with a single click.

Built with **Next.js 16**, **Python 3**, **FFmpeg**, and **Edge-TTS**.

---

## Features

- **Drag-and-drop UI** — Upload images and write/edit your script directly in the browser
- **AI Voiceover** — Microsoft Edge-TTS neural voices (6+ languages/accents)
- **Ken Burns Effect** — Each image gets a random cinematic motion (zoom-in, zoom-out, pan-left, pan-right, or static)
- **Auto-synchronization** — Video clips are automatically timed to match narration audio duration
- **Real-time Progress** — Live streaming logs from the Python backend via SSE
- **Dark theme** — Built with shadcn/ui components and Tailwind CSS
- **Zero manual editing** — No timeline dragging, no voice recording, no Premiere Pro

## How It Works

1. **Upload images** — Drag images into the upload zone (JPG, PNG, WebP, BMP)
2. **Write a script** — Enter narration text with paragraphs separated by blank lines
3. **Configure** — Select TTS voice (Andrew, Ava, Guy, Ryan, Sonia, William)
4. **Generate** — Click "Generate Video" and watch the live progress
5. **Download** — Get your finished MP4 video ready for YouTube/TikTok

### Pipeline

```
Images + Script → Edge-TTS audio → Ken Burns clips → Concatenate → Merge audio → Final MP4
```

Each paragraph in the script becomes a self-contained video chunk. The system:
1. Generates AI narration audio for the paragraph
2. Measures exact audio duration via FFprobe
3. Creates cinematic clips from images until total visual time matches narration
4. Concatenates clips and merges with audio
5. Stitches all chunks into one final video

---

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| [Python](https://python.org) | 3.10+ | Backend processing |
| [Node.js](https://nodejs.org) | 18+ | Frontend server |
| [Yarn](https://yarnpkg.com) | 1.22+ | Package manager |
| [FFmpeg](https://ffmpeg.org) | 4.0+ | Video/audio processing (must be in PATH) |
| [Tesseract OCR](https://github.com/UB-Mannheim/tesseract) | 5.x | Optional — for frame text extraction |

**Verify FFmpeg + FFprobe are in your PATH:**
```bash
ffmpeg -version
ffprobe -version
```

## Installation

### 1. Python dependencies

```bash
cd python
pip install edge-tts
```

### 2. Frontend dependencies

```bash
cd ..
yarn install
```

### 3. Run the development server

```bash
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4. Production build

```bash
yarn build
yarn start
```

---

## Project Structure

```
video-generator-app/
├── pages/
│   ├── index.jsx              # Main UI
│   ├── _app.jsx               # App wrapper
│   └── api/
│       ├── upload.js           # File upload (multer)
│       ├── generate.js         # Spawns Python, streams progress
│       └── download.js         # Serves final MP4
├── components/
│   ├── Layout.jsx              # App shell + header
│   ├── UploadZone.jsx          # Drag-and-drop + text editor
│   ├── ConfigPanel.jsx         # Voice/config selectors
│   ├── ProgressLog.jsx         # Real-time output log
│   ├── VideoPlayer.jsx         # Video playback + download
│   └── ui/                     # shadcn/ui primitives
│       ├── button.jsx
│       ├── card.jsx
│       ├── select.jsx
│       ├── textarea.jsx
│       ├── scroll-area.jsx
│       ├── badge.jsx
│       ├── progress.jsx
│       ├── separator.jsx
│       └── label.jsx
├── python/
│   ├── generate.py             # Full Python pipeline
│   └── requirements.txt
├── public/uploads/             # Uploaded images + generated video
├── styles/
│   └── globals.css             # Tailwind + shadcn dark theme
├── lib/
│   └── utils.js                # cn() utility
├── components.json             # shadcn configuration
├── tailwind.config.js
├── postcss.config.js
├── next.config.js
├── jsconfig.json
└── package.json
```

---

## Configuration

All video settings are defined in `python/generate.py`:

| Setting | Default | Description |
|---|---|---|
| `VOICE_NAME` | `en-US-AndrewNeural` | Edge-TTS voice |
| `TARGET_RESOLUTION` | `(1280, 720)` | Output resolution |
| `TARGET_FPS` | `30` | Frames per second |
| `MIN_IMAGE_DURATION` | `3.0` | Minimum seconds per image clip |
| `MAX_IMAGE_DURATION` | `5.0` | Maximum seconds per image clip |

### Available Voice Options

| Value | Voice |
|---|---|
| `en-US-AndrewNeural` | Andrew (US Male) |
| `en-US-AvaNeural` | Ava (US Female) |
| `en-US-GuyNeural` | Guy (US Male) |
| `en-GB-RyanNeural` | Ryan (UK Male) |
| `en-GB-SoniaNeural` | Sonia (UK Female) |
| `en-AU-WilliamNeural` | William (AU Male) |

---

## Script Format

The script file should have paragraphs separated by **two consecutive newlines** (blank lines). Each paragraph becomes a separate video chunk.

```
First paragraph of narration. This will be its own video segment
with its own set of images and audio.

Second paragraph of narration. The system will automatically
select new images and generate new audio for this section.

Third paragraph. And so on.
```

---

## Expandability Ideas

- **Background music** — Overlay an audio track on the final video
- **AI-generated images** — Integrate DALL-E or Stable Diffusion to generate visuals from script context
- **Auto script generation** — Use an LLM to generate narration from a topic
- **Subtitles** — Add burned-in or external subtitle file generation
- **YouTube upload** — Auto-upload to YouTube using the Data API
- **Scene detection** — Analyze images and match them to script content
- **Batch processing** — Generate multiple videos from a CSV of scripts

---

## License

MIT
