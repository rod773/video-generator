#!/usr/bin/env python3
import os
import sys
import random
import json
import asyncio
import subprocess
import time as time_module
import edge_tts

# ============================================================
# CONFIGURATION
# ============================================================
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_FOLDER = os.path.join(ROOT_DIR, "..", "public", "uploads")
READY_FOLDER = os.path.join(ROOT_DIR, "ready_media")
OUTPUT_FOLDER = os.path.join(ROOT_DIR, "output")

VOICE_NAME = "en-US-AndrewNeural"
TARGET_RESOLUTION = (1280, 720)
TARGET_FPS = 30
MIN_IMAGE_DURATION = 3.0
MAX_IMAGE_DURATION = 5.0

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def log(msg):
    print(json.dumps({"type": "log", "message": str(msg)}), flush=True)

def get_duration(file_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except (ValueError, AttributeError):
        return 0.0

# ============================================================
# IMAGE PROCESSING
# ============================================================

def get_image_files():
    if not os.path.exists(IMAGES_FOLDER):
        raise FileNotFoundError(f"Images folder not found: {IMAGES_FOLDER}")
    image_extensions = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
    image_files = [f for f in os.listdir(IMAGES_FOLDER) if f.lower().endswith(image_extensions)]
    if not image_files:
        raise FileNotFoundError(f"No image files found in {IMAGES_FOLDER}")
    full_paths = [os.path.join(IMAGES_FOLDER, f) for f in image_files]
    full_paths.sort(key=lambda f: os.path.getmtime(f))
    return full_paths

def create_ken_burns_image_clip(image_path, duration, output_path):
    zoom_type = random.choice(["zoom_in", "zoom_out", "pan_right", "pan_left", "static"])
    w, h = TARGET_RESOLUTION
    frames = int(duration * TARGET_FPS)
    zoom_speed = 0.4 / frames

    if zoom_type == "zoom_in":
        vf = f"zoompan=z='min(zoom+{zoom_speed},1.4)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h}"
    elif zoom_type == "zoom_out":
        vf = f"zoompan=z='max(zoom-{zoom_speed},1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h}"
    elif zoom_type == "pan_right":
        pan_speed = f"on*{frames / (frames / 3)}"
        vf = f"zoompan=z='min({pan_speed},iw/3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h}"
    elif zoom_type == "pan_left":
        pan_speed = f"on*{frames / (frames / 3)}"
        vf = f"zoompan=z='min({pan_speed},iw/3)':x='iw/3-min({pan_speed},iw/3)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h}"
    else:
        vf = f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2"

    cmd = [
        "ffmpeg", "-y", "-i", image_path, "-vf", vf,
        "-t", str(duration), "-c:v", "libx264",
        "-preset", "fast", "-crf", "20",
        "-r", str(TARGET_FPS), "-pix_fmt", "yuv420p",
        output_path
    ]
    subprocess.run(cmd, capture_output=True, text=True)
    return output_path

# ============================================================
# AUDIO GENERATION
# ============================================================

async def generate_audio(text, output_path):
    communicate = edge_tts.Communicate(text, VOICE_NAME)
    await communicate.save(output_path)
    return output_path

# ============================================================
# MAIN PIPELINE
# ============================================================

async def generate_video():
    os.makedirs(READY_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    script_path = os.path.join(IMAGES_FOLDER, "script.txt")
    if not os.path.exists(script_path):
        raise FileNotFoundError("script.txt not found in uploads folder")

    with open(script_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
    if not paragraphs:
        raise ValueError("No paragraphs found in script.txt")

    log(f"Found {len(paragraphs)} paragraphs to process.")

    image_files = get_image_files()
    log(f"Using {len(image_files)} images (sorted by date)")

    generated_chunks = []
    image_index = 0

    for idx, paragraph in enumerate(paragraphs):
        log(f"Processing paragraph {idx + 1}/{len(paragraphs)}...")

        temp_audio = os.path.join(READY_FOLDER, f"temp_audio_{idx}.mp3")
        try:
            await generate_audio(paragraph, temp_audio)
        except Exception as e:
            log(f"Error generating audio: {e}")
            continue

        audio_duration = get_duration(temp_audio)
        log(f"Audio: {audio_duration:.1f}s")

        selected_clips = []
        current_dur = 0

        while current_dur < audio_duration:
            img_path = image_files[image_index % len(image_files)]
            image_index += 1
            remaining = audio_duration - current_dur
            target_dur = min(random.uniform(MIN_IMAGE_DURATION, MAX_IMAGE_DURATION), remaining)
            clip_path = os.path.join(READY_FOLDER, f"clip_{idx}_{len(selected_clips)}.mp4")
            create_ken_burns_image_clip(img_path, target_dur, clip_path)
            actual_dur = get_duration(clip_path)
            if actual_dur <= 0:
                continue
            selected_clips.append(clip_path)
            current_dur += actual_dur

        if len(selected_clips) == 1:
            chunk_path = selected_clips[0]
        else:
            concat_path = os.path.join(READY_FOLDER, f"concat_p{idx}.txt")
            with open(concat_path, "w", encoding="utf-8") as f:
                for clip in selected_clips:
                    f.write(f"file '{clip.replace(chr(92), '/')}'\n")
            chunk_path = os.path.join(READY_FOLDER, f"chunk_{idx}.mp4")
            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", concat_path, "-c:v", "libx264", "-preset", "fast",
                "-crf", "20", "-c:a", "aac", "-b:a", "192k", chunk_path
            ], capture_output=True, text=True)
            if os.path.exists(concat_path):
                os.remove(concat_path)

        final_chunk = os.path.join(READY_FOLDER, f"final_chunk_{idx}.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-i", chunk_path, "-i", temp_audio,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", final_chunk
        ], capture_output=True, text=True)

        generated_chunks.append(final_chunk)
        log(f"Chunk {idx + 1} completed.")

        time_module.sleep(0.1)
        for p in [temp_audio, chunk_path]:
            try:
                if os.path.exists(p) and p != final_chunk:
                    os.remove(p)
            except PermissionError:
                pass
        for clip in selected_clips:
            try:
                if os.path.exists(clip) and clip != final_chunk:
                    os.remove(clip)
            except PermissionError:
                pass

    if not generated_chunks:
        raise RuntimeError("No chunks were generated")

    final_output = os.path.join(OUTPUT_FOLDER, "final_video.mp4")

    if len(generated_chunks) == 1:
        import shutil
        shutil.copy2(generated_chunks[0], final_output)
    else:
        final_concat = os.path.join(READY_FOLDER, "final_concat.txt")
        with open(final_concat, "w", encoding="utf-8") as f:
            for chunk in generated_chunks:
                f.write(f"file '{chunk.replace(chr(92), '/')}'\n")
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", final_concat, "-c:v", "libx264", "-preset", "medium",
            "-crf", "20", "-c:a", "aac", "-b:a", "192k", final_output
        ], capture_output=True, text=True)
        if os.path.exists(final_concat):
            os.remove(final_concat)

    if os.path.exists(final_output):
        for chunk in generated_chunks:
            if os.path.exists(chunk):
                os.remove(chunk)
        log(f"Done! Output: {final_output}")
        print(json.dumps({"type": "done", "output": final_output}), flush=True)
    else:
        raise RuntimeError("Final video not created")

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            VOICE_NAME = sys.argv[1]
        asyncio.run(generate_video())
    except Exception as e:
        print(json.dumps({"type": "error", "message": str(e)}), flush=True)
        sys.exit(1)
