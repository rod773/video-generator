# Fully Automated AI Video Generator

## Project Idea

Build a system that takes a folder of images and a text script, then automatically generates a complete cinematic video with AI voiceover, Ken Burns animations, and synchronized timing — all with zero manual editing.

## Architecture

### Tech Stack
- **Frontend**: Next.js 16 + React 19 + shadcn/ui + Tailwind CSS
- **Backend**: Python 3 + FFmpeg/FFprobe + Edge-TTS
- **Communication**: Next.js API routes spawn Python via child_process, stream progress via SSE
- **File handling**: multer for uploads, FFmpeg for video processing

### Python Backend (`python/generate.py`)

**Configuration:**
- `IMAGES_FOLDER` — input images directory
- `READY_FOLDER` — temporary processing files
- `OUTPUT_FOLDER` — final rendered video
- `VOICE_NAME` — Edge-TTS voice (default: `en-US-AndrewNeural`)
- `TARGET_RESOLUTION` — video resolution (1280x720)
- `TARGET_FPS` — frames per second (30)
- `MIN_IMAGE_DURATION` / `MAX_IMAGE_DURATION` — clip duration range (3-5s)

**Functions:**

1. `get_duration(file_path)` — Uses FFprobe to get exact audio/video duration. Critical for synchronization.

2. `get_image_files()` — Scans images folder, returns files sorted by modification date (oldest first). Supports .jpg, .jpeg, .png, .webp, .bmp.

3. `create_ken_burns_image_clip(image_path, duration, output_path)` — Generates a video clip from a static image using FFmpeg's `zoompan` filter. Randomly selects one of 5 effects:
   - **zoom_in**: Slow zoom from 1.0x to 1.4x from center
   - **zoom_out**: Slow zoom from 1.4x to 1.0x from center
   - **pan_right**: Slow horizontal pan left-to-right at 1.3x zoom
   - **pan_left**: Slow horizontal pan right-to-left at 1.3x zoom
   - **static**: Scaled to resolution with aspect-ratio padding

4. `generate_audio(text, output_path)` — Async function using `edge_tts.Communicate` to convert text to speech MP3. One audio file per paragraph.

5. `generate_video()` — Main async pipeline:
   - Read script.txt → split by blank lines into paragraphs
   - For each paragraph:
     - Generate narration audio via Edge-TTS
     - Calculate audio duration via FFprobe
     - Sequentially select images, generate Ken Burns clips until total visual duration matches audio
     - Concatenate clips into a segment
     - Merge audio with video segment
     - Clean up temporary files
   - Stitch all chunks into final MP4
   - Output structured JSON logs for real-time frontend consumption

### Next.js Frontend

**API Routes:**

| Route | Method | Description |
|---|---|---|
| `/api/upload` | POST | Upload images + script.txt via multipart form |
| `/api/generate` | POST | Start generation, returns SSE stream of progress |
| `/api/download` | GET | Download generated `final_video.mp4` |

**Components:**

1. **UploadZone** — Drag-and-drop image upload with preview thumbnails, inline script textarea with .txt import support
2. **ConfigPanel** — TTS voice selection using shadcn Select, read-only resolution/FPS display
3. **ProgressLog** — Real-time log output in a shadcn ScrollArea, color-coded (error=red, done=green, progress=yellow)
4. **VideoPlayer** — Native `<video>` element with download button for the generated MP4

### Data Flow

```
User Uploads Images + Script
        │
        ▼
[/api/upload] — multer saves to public/uploads/
        │
        ▼
[/api/generate] — spawns Python child_process
        │
        ▼
[python/generate.py]
  ├── Read script → split paragraphs
  ├── For each paragraph:
  │   ├── Edge-TTS → MP3 audio
  │   ├── FFprobe → get audio duration
  │   ├── For each image:
  │   │   └── FFmpeg zoompan → Ken Burns clip
  │   ├── FFmpeg concat → video segment
  │   └── FFmpeg merge audio+video → chunk
  ├── FFmpeg concat all chunks → final_video.mp4
  └── Cleanup temp files
        │
        ▼
[SSE stream] ← JSON log lines ← stdout
        │
        ▼
[Frontend ProgressLog] ← live updates
[Frontend VideoPlayer] ← final video displayed
```

### Key Design Decisions

- **Single Python file**: Entire backend logic is self-contained in one script for simplicity
- **Sequential image selection**: Images are selected in order (sorted by date) and cycle when exhausted, ensuring consistent visual flow
- **Random Ken Burns effects**: Each image gets a random effect picked from 5 options, creating natural variety
- **Per-paragraph audio sync**: Each paragraph becomes a self-contained chunk, making the pipeline modular and resumable
- **Edge-TTS for voice**: Free, high-quality neural voices without API keys; runs locally via async Python
- **Streaming logs via SSE**: Real-time progress without polling or WebSocket complexity

### Expandability

- Add background music overlay
- AI-generated images via DALL-E/Stable Diffusion
- Automatic script generation via LLM
- Subtitle/closed caption generation
- YouTube auto-upload
- Scene detection and image segmentation
