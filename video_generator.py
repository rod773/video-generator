#!/usr/bin/env python3
"""
Fully Automated AI Video Generator
Python + FFmpeg + Edge-TTS

Drop images into the images folder, write a script.txt,
run this file, and automatically generate a complete
cinematic video with voiceover, Ken Burns animations,
timing, and final rendering.
"""

import os
import random
import asyncio
import subprocess
import time as time_module
import edge_tts

# ============================================================
# CONFIGURATION
# ============================================================
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_FOLDER = os.path.join(ROOT_DIR, "images")
READY_FOLDER = os.path.join(ROOT_DIR, "ready_media")
OUTPUT_FOLDER = os.path.join(ROOT_DIR, "output")
SCRIPT_FILE = os.path.join(ROOT_DIR, "script.txt")

# Voice options: en-US-GuyNeural, en-US-AvaNeural, en-GB-RyanNeural
VOICE_NAME = "en-US-AndrewNeural"

# Video processing settings
TARGET_RESOLUTION = (1280, 720)
TARGET_FPS = 30
MIN_IMAGE_DURATION = 3.0
MAX_IMAGE_DURATION = 5.0

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_duration(file_path):
    """Get video/audio duration in seconds using ffprobe."""
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
    """Get all image files from images folder, sorted by date (oldest first)."""
    if not os.path.exists(IMAGES_FOLDER):
        raise FileNotFoundError(f"Images folder not found: {IMAGES_FOLDER}")

    image_extensions = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
    image_files = [
        f for f in os.listdir(IMAGES_FOLDER)
        if f.lower().endswith(image_extensions)
    ]

    if not image_files:
        raise FileNotFoundError(f"No image files found in {IMAGES_FOLDER}")

    # Sort by modification time (oldest first)
    full_paths = [os.path.join(IMAGES_FOLDER, f) for f in image_files]
    full_paths.sort(key=lambda f: os.path.getmtime(f))

    return full_paths


def create_ken_burns_image_clip(image_path, duration, output_path):
    """Create a video clip from an image with Ken Burns effect (slow zoom/pan)."""
    # Randomly choose zoom direction
    zoom_type = random.choice(["zoom_in", "zoom_out", "pan_right", "pan_left", "static"])

    w, h = TARGET_RESOLUTION
    frames = int(duration * TARGET_FPS)
    # Calculate zoom speed per frame (zoom range 1.0 to 1.4 over duration)
    zoom_speed = 0.4 / frames

    if zoom_type == "zoom_in":
        # Slow zoom in from center
        vf = (
            f"zoompan=z='min(zoom+{zoom_speed},1.4)':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d=1:s={w}x{h}"
        )

    elif zoom_type == "zoom_out":
        # Slow zoom out from center
        vf = (
            f"zoompan=z='max(zoom-{zoom_speed},1.0)':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d=1:s={w}x{h}"
        )

    elif zoom_type == "pan_right":
        # Slow pan from left to right
        pan_speed = f"on*{frames / (frames / 3)}"
        vf = (
            f"zoompan=z='min({pan_speed},iw/3)':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d=1:s={w}x{h}"
        )

    elif zoom_type == "pan_left":
        # Slow pan from right to left
        pan_speed = f"on*{frames / (frames / 3)}"
        vf = (
            f"zoompan=z='min({pan_speed},iw/3)':"
            f"x='iw/3-min({pan_speed},iw/3)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d=1:s={w}x{h}"
        )

    else:
        # Static with scale to 720p
        vf = (
            f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2"
        )

    cmd = [
        "ffmpeg", "-y",
        "-i", image_path,
        "-vf", vf,
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-r", str(TARGET_FPS),
        "-pix_fmt", "yuv420p",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  > FFmpeg error: {result.stderr}")
    return output_path


# ============================================================
# AUDIO GENERATION
# ============================================================

async def generate_audio(text, output_path):
    """Generate voiceover audio using Edge-TTS."""
    communicate = edge_tts.Communicate(text, VOICE_NAME)
    await communicate.save(output_path)
    return output_path


# ============================================================
# MAIN PIPELINE
# ============================================================

async def generate_video():
    """Main video generation pipeline."""
    # Create output directories
    os.makedirs(READY_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Read script
    if not os.path.exists(SCRIPT_FILE):
        raise FileNotFoundError(f"Script file not found: {SCRIPT_FILE}")

    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        raw_text = f.read()

    paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]

    if not paragraphs:
        raise ValueError("No paragraphs found in script.txt")

    print(f"Found {len(paragraphs)} paragraphs to process.")
    print(f"Found images in: {IMAGES_FOLDER}\n")

    # Get all available images (sorted by date, oldest first)
    image_files = get_image_files()
    print(f"Using {len(image_files)} images (sorted by date)\n")

    generated_chunks = []
    image_index = 0

    for idx, paragraph in enumerate(paragraphs):
        print(f"Processing paragraph {idx + 1}/{len(paragraphs)}...")

        # Generate audio for this paragraph
        temp_audio = os.path.join(READY_FOLDER, f"temp_audio_{idx}.mp3")
        try:
            await generate_audio(paragraph, temp_audio)
        except Exception as e:
            print(f"  > Error generating audio: {e}")
            print(f"  > Skipping this paragraph due to network error")
            continue

        audio_duration = get_duration(temp_audio)
        print(f"  > Audio: {audio_duration:.1f}s")

        # Create video clips from images to match audio duration
        selected_clips = []
        current_dur = 0

        while current_dur < audio_duration:
            img_path = image_files[image_index % len(image_files)]
            image_index += 1

            remaining = audio_duration - current_dur
            target_dur = min(random.uniform(MIN_IMAGE_DURATION, MAX_IMAGE_DURATION), remaining)

            clip_path = os.path.join(READY_FOLDER, f"clip_{idx}_{len(selected_clips)}.mp4")
            print(f"    Generating clip {len(selected_clips) + 1} from {os.path.basename(img_path)} ({target_dur:.1f}s)...")

            create_ken_burns_image_clip(img_path, target_dur, clip_path)

            actual_dur = get_duration(clip_path)
            if actual_dur <= 0:
                print(f"    > Warning: clip has zero duration, skipping")
                continue

            selected_clips.append(clip_path)
            current_dur += actual_dur

        # Concatenate clips for this paragraph
        if len(selected_clips) == 1:
            chunk_path = selected_clips[0]
        else:
            concat_path = os.path.join(READY_FOLDER, f"concat_p{idx}.txt")
            with open(concat_path, "w", encoding="utf-8") as f:
                for clip in selected_clips:
                    safe_path = clip.replace("\\", "/")
                    f.write(f"file '{safe_path}'\n")

            chunk_path = os.path.join(READY_FOLDER, f"chunk_{idx}.mp4")
            result = subprocess.run([
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_path,
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "20",
                "-c:a", "aac",
                "-b:a", "192k",
                chunk_path
            ], capture_output=True, text=True)

            if result.returncode != 0:
                print(f"  > FFmpeg concat error: {result.stderr}")
                chunk_path = selected_clips[0]

            if os.path.exists(concat_path):
                os.remove(concat_path)

        # Merge audio with video chunk
        final_chunk = os.path.join(READY_FOLDER, f"final_chunk_{idx}.mp4")
        subprocess.run([
            "ffmpeg", "-y",
            "-i", chunk_path,
            "-i", temp_audio,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            final_chunk
        ], capture_output=True, text=True)

        generated_chunks.append(final_chunk)
        print(f"  > Chunk {idx + 1} completed.\n")

        # Cleanup temp files (add delay to allow file handles to release)
        time_module.sleep(0.1)
        try:
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
        except PermissionError:
            pass
        try:
            if os.path.exists(chunk_path) and chunk_path != final_chunk:
                os.remove(chunk_path)
        except PermissionError:
            pass
        for clip in selected_clips:
            try:
                if os.path.exists(clip) and clip != final_chunk:
                    os.remove(clip)
            except PermissionError:
                pass

    # Stitch all chunks together into final output
    if not generated_chunks:
        print("\nERROR: No chunks were generated!")
        return None

    final_output = os.path.join(OUTPUT_FOLDER, "final_video.mp4")

    if len(generated_chunks) == 1:
        # If only one chunk, just copy it
        import shutil
        shutil.copy2(generated_chunks[0], final_output)
    else:
        final_concat_path = os.path.join(READY_FOLDER, "final_concat.txt")
        with open(final_concat_path, "w", encoding="utf-8") as f:
            for chunk in generated_chunks:
                safe_path = chunk.replace("\\", "/")
                f.write(f"file '{safe_path}'\n")

        subprocess.run([
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", final_concat_path,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "20",
            "-c:a", "aac",
            "-b:a", "192k",
            final_output
        ], capture_output=True, text=True)

        if os.path.exists(final_concat_path):
            os.remove(final_concat_path)

    # Verify output exists
    if os.path.exists(final_output):
        for chunk in generated_chunks:
            if os.path.exists(chunk):
                os.remove(chunk)
        print(f"\nDONE! Output: {final_output}")
    else:
        print(f"\nERROR: Final video not created!")
        print(f"Check the errors above.")

    return final_output


if __name__ == "__main__":
    asyncio.run(generate_video())
