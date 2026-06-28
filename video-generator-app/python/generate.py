#!/usr/bin/env python3
import os
import sys
import math
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
DURATION_PER_IMAGE = 4.0

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
# PROMPT PARSING
# ============================================================

def parse_prompt(prompt_text):
    prompt_text = (prompt_text or "").lower()
    weights = {"zoom_in": 1, "zoom_out": 1, "pan_right": 1, "pan_left": 1, "static": 1}
    duration_range = [MIN_IMAGE_DURATION, MAX_IMAGE_DURATION]
    color_filter = None
    forced_effect = None

    explicit_instructions = {
        # Horizontal 3D rotation (card flip / sign turn)
        "rotate right horizontally": "rotate_horizontal_right",
        "rotate horizontally right": "rotate_horizontal_right",
        "rotate right horizontal": "rotate_horizontal_right",
        "horizontal rotate right": "rotate_horizontal_right",
        "horizontal flip right": "rotate_horizontal_right",
        "flip right": "rotate_horizontal_right",
        "flip horizontally": "rotate_horizontal_right",
        "3d rotate right": "rotate_horizontal_right",
        "turn right": "rotate_horizontal_right",
        "rotate left horizontally": "rotate_horizontal_left",
        "rotate horizontally left": "rotate_horizontal_left",
        "rotate left horizontal": "rotate_horizontal_left",
        "horizontal rotate left": "rotate_horizontal_left",
        "horizontal flip left": "rotate_horizontal_left",
        "flip left": "rotate_horizontal_left",
        "3d rotate left": "rotate_horizontal_left",
        "turn left": "rotate_horizontal_left",

        # In-plane rotation
        "rotate right": "rotate_right",
        "rotate clockwise": "rotate_right",
        "spin right": "rotate_right",
        "spin clockwise": "rotate_right",
        "rotate left": "rotate_left",
        "rotate counterclockwise": "rotate_left",
        "rotate counter-clockwise": "rotate_left",
        "spin left": "rotate_left",
        "spin counterclockwise": "rotate_left",

        # Zoom
        "zoom in": "zoom_in",
        "zoom out": "zoom_out",
        "dolly in": "dolly_in",
        "dolly out": "dolly_out",
        "push in": "dolly_in",
        "pull out": "dolly_out",
        "close up": "dolly_in",
        "wide shot": "dolly_out",
        "magnify": "zoom_in",
        "shrink": "zoom_out",

        # Pan / Truck / Tilt
        "pan right": "pan_right",
        "pan left": "pan_left",
        "pan up": "pan_up",
        "pan down": "pan_down",
        "tilt up": "pan_up",
        "tilt down": "pan_down",
        "truck right": "pan_right",
        "truck left": "pan_left",
        "slide right": "pan_right",
        "slide left": "pan_left",
        "slide up": "pan_up",
        "slide down": "pan_down",
        "scroll right": "pan_right",
        "scroll left": "pan_left",
        "scroll up": "pan_up",
        "scroll down": "pan_down",
        "move right": "pan_right",
        "move left": "pan_left",
        "move up": "pan_up",
        "move down": "pan_down",

        # Static
        "still": "static",
        "static": "static",
        "no movement": "static",
        "no motion": "static",
        "freeze": "static",
        "still image": "static",
        "pause": "static",

        # Shake
        "shake": "shake",
        "shaking": "shake",
        "vibrate": "shake",
        "vibration": "shake",
        "tremble": "shake",
        "trembling": "shake",
        "earthquake": "shake",
        "jitter": "shake",
        "unstable": "shake",
        "wobble": "shake",
        "wobbling": "shake",
        "handheld": "handheld",
        "hand held": "handheld",
        "hand-held": "handheld",
        "documentary": "handheld",
        "camcorder": "handheld",

        # Pulse / Breathing
        "pulse": "pulse",
        "pulsing": "pulse",
        "breathe": "pulse",
        "breathing": "pulse",
        "throb": "pulse",
        "throbbing": "pulse",
        "beat": "pulse",
        "pulsate": "pulse",
        "oscillate": "pulse",

        # Color effects
        "black and white": "grayscale",
        "black & white": "grayscale",
        "bw": "grayscale",
        "b&w": "grayscale",
        "grayscale": "grayscale",
        "greyscale": "grayscale",
        "monochrome": "grayscale",
        "mono": "grayscale",
        "noir": "grayscale",
        "sepia": "sepia",
        "vintage": "sepia",
        "retro": "sepia",
        "old film": "sepia",
        "old photo": "sepia",
        "cinematic": "cinematic",
        "cinema": "cinematic",
        "film look": "cinematic",
        "movie": "cinematic",
        "invert": "invert",
        "inverted": "invert",
        "negative": "invert",

        # Orbit / spiral (combines zoom + rotation)
        "orbit right": "orbit_right",
        "orbit clockwise": "orbit_right",
        "orbit left": "orbit_left",
        "orbit counterclockwise": "orbit_left",
        "orbiting right": "orbit_right",
        "orbiting left": "orbit_left",
        "spiral right": "orbit_right",
        "spiral left": "orbit_left",

        # Crane / pedestal
        "crane up": "crane_up",
        "crane down": "crane_down",
        "pedestal up": "crane_up",
        "pedestal down": "crane_down",
        "rise": "crane_up",
        "descend": "crane_down",
        "ascend": "crane_up",
        "lift": "crane_up",
        "lower": "crane_down",

        # Reveal / fade
        "reveal": "reveal",
        "fade in": "reveal",
        "fade from black": "reveal",
        "appear": "reveal",
        "dissolve in": "reveal",
    }

    # Check explicit instructions first (sorted by length descending to match longer phrases first)
    color_only_effects = {"grayscale", "sepia", "cinematic", "invert"}
    for phrase in sorted(explicit_instructions.keys(), key=len, reverse=True):
        if phrase in prompt_text:
            effect = explicit_instructions[phrase]
            if effect in color_only_effects:
                # Apply as color filter, not movement
                pass
            else:
                forced_effect = effect
            break

    # Color filters still apply independently of forced effect
    if any(w in prompt_text for w in ["sepia", "vintage", "retro", "old film", "old photo"]):
        color_filter = "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131:0"
    elif any(w in prompt_text for w in ["cinematic", "cinema", "film look", "movie"]):
        color_filter = "curves=b='0/0 0.5/0.4 1/0.8':g='0/0 0.5/0.5 1/0.8':r='0/0 0.5/0.6 1/0.9'"
    elif any(w in prompt_text for w in ["black and white", "bw", "grayscale", "monochrome"]):
        color_filter = "colorchannelmixer=.3:.4:.3:0:.3:.4:.3:0:.3:.4:.3:0,hue=s=0"
    elif "invert" in prompt_text:
        color_filter = "colorchannelmixer=-1:1:0:0:0:-1:1:0:0:0:-1:1"

    # Style keywords (fallback when no explicit instruction)
    if not forced_effect:
        keywords = {
            "cinematic": {"static": 0.3, "zoom_in": 1.5, "zoom_out": 1.5},
            "dramatic": {"static": 0.3, "zoom_in": 2, "zoom_out": 2},
            "dynamic": {"static": 0.2, "pan_right": 1.5, "pan_left": 1.5},
            "fast": {"static": 0.2, "shake": 2},
            "quick": {"static": 0.2},
            "montage": {"static": 0.2, "pan_right": 1.5, "pan_left": 1.5},
            "calm": {"static": 2, "zoom_in": 0.7, "zoom_out": 0.7},
            "slow": {"static": 2, "zoom_in": 0.7, "zoom_out": 0.7},
            "gentle": {"static": 2, "zoom_in": 0.7, "zoom_out": 0.7},
            "relaxing": {"static": 2.5, "zoom_in": 0.5, "zoom_out": 0.5},
            "slideshow": {"static": 4},
            "static": {"static": 4},
        }

        for word, adjustments in keywords.items():
            if word in prompt_text:
                for effect, mult in adjustments.items():
                    weights[effect] = weights.get(effect, 1) * mult

        fast_words = ["fast", "quick", "montage", "dynamic", "energetic", "time lapse", "timelapse", "speed up"]
        slow_words = ["slow", "calm", "gentle", "relaxing", "peaceful", "meditative", "slow motion", "slowmo"]

        has_fast = any(w in prompt_text for w in fast_words)
        has_slow = any(w in prompt_text for w in slow_words)

        if has_fast and not has_slow:
            duration_range = [2.0, 3.5]
        elif has_slow and not has_fast:
            duration_range = [4.0, 7.0]

    return weights, duration_range, color_filter, forced_effect


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

def create_ken_burns_image_clip(image_path, duration, output_path, weights=None, color_filter=None, forced_effect=None):
    effects = [
        "zoom_in", "zoom_out", "dolly_in", "dolly_out",
        "pan_right", "pan_left", "pan_up", "pan_down",
        "static",
        "rotate_right", "rotate_left",
        "rotate_horizontal_right", "rotate_horizontal_left",
        "shake", "handheld", "pulse",
        "orbit_right", "orbit_left", "crane_up", "crane_down",
        "reveal",
    ]
    if forced_effect:
        zoom_type = forced_effect
    elif weights:
        total = sum(weights.get(e, 1) for e in effects if e in weights)
        eff = [e for e in effects if e in weights]
        probs = [weights.get(e, 1) / total for e in eff]
        zoom_type = random.choices(eff, weights=probs, k=1)[0]
    else:
        zoom_type = random.choice(effects)
    w, h = TARGET_RESOLUTION
    frames = max(int(duration * TARGET_FPS), 1)
    zoom_speed = 0.4 / frames
    half = frames // 2

    if zoom_type == "zoom_in":
        vf = f"zoompan=z='min(zoom+{zoom_speed},1.4)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h}"
    elif zoom_type == "zoom_out":
        vf = f"zoompan=z='max(zoom-{zoom_speed},1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h}"
    elif zoom_type in ("dolly_in",):
        vf = f"zoompan=z='min(zoom+{zoom_speed * 0.3},1.2)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h}"
    elif zoom_type in ("dolly_out",):
        vf = f"zoompan=z='max(zoom-{zoom_speed * 0.3},1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h}"
    elif zoom_type == "pan_right":
        pan_step = max(frames / 3, 1)
        vf = f"zoompan=z='min(on*{pan_step},iw/3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h}"
    elif zoom_type == "pan_left":
        pan_step = max(frames / 3, 1)
        vf = f"zoompan=z='min(on*{pan_step},iw/3)':x='iw/3-min(on*{pan_step},iw/3)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h}"
    elif zoom_type in ("pan_up", "crane_up"):
        vf = f"zoompan=z='min(zoom+{zoom_speed * 0.3},1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)-{h/4}*on/{frames}':d=1:s={w}x{h}"
    elif zoom_type in ("pan_down", "crane_down"):
        vf = f"zoompan=z='min(zoom+{zoom_speed * 0.3},1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)+{h/4}*on/{frames}':d=1:s={w}x{h}"
    elif zoom_type == "rotate_right":
        vf = f"zoompan=z='min(zoom+{zoom_speed * 0.5},1.2)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h},pad=ceil(iw*1.5):ceil(ih*1.5):(ow-iw)/2:(oh-ih)/2:black,rotate=t*2*PI/{duration}:c=black,crop={w}:{h}:(ow-iw)/2:(oh-ih)/2"
    elif zoom_type == "rotate_left":
        vf = f"zoompan=z='min(zoom+{zoom_speed * 0.5},1.2)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h},pad=ceil(iw*1.5):ceil(ih*1.5):(ow-iw)/2:(oh-ih)/2:black,rotate=-t*2*PI/{duration}:c=black,crop={w}:{h}:(ow-iw)/2:(oh-ih)/2"
    elif zoom_type == "rotate_horizontal_right":
        vf = f"zoompan=z='min(zoom+{zoom_speed * 0.3},1.1)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h},pad=ceil(iw*1.2):ceil(ih*1.2):(ow-iw)/2:(oh-ih)/2:black,rotate=t*PI/{duration}:c=black,crop={w}:{h}:(ow-iw)/2:(oh-ih)/2"
    elif zoom_type == "rotate_horizontal_left":
        vf = f"zoompan=z='min(zoom+{zoom_speed * 0.3},1.1)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h},pad=ceil(iw*1.2):ceil(ih*1.2):(ow-iw)/2:(oh-ih)/2:black,rotate=-t*PI/{duration}:c=black,crop={w}:{h}:(ow-iw)/2:(oh-ih)/2"
    elif zoom_type in ("orbit_right", "orbit_left"):
        direction = 1 if zoom_type == "orbit_right" else -1
        vf = f"zoompan=z='min(zoom+{zoom_speed*0.2},1.1)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h},pad=ceil(iw*1.5):ceil(ih*1.5):(ow-iw)/2:(oh-ih)/2:black,rotate=t*{direction}*PI/{duration}:c=black,crop={w}:{h}:(ow-iw)/2:(oh-ih)/2"
    elif zoom_type == "shake":
        vf = f"zoompan=z='1.02':x='iw/2-(iw/zoom/2)+{w/15}*sin(on*0.5)+{w/20}*sin(on*0.3)':y='ih/2-(ih/zoom/2)+{h/15}*sin(on*0.7)+{h/20}*sin(on*0.4)':d=1:s={w}x{h}"
    elif zoom_type == "handheld":
        vf = f"zoompan=z='1.01':x='iw/2-(iw/zoom/2)+{w/40}*sin(on*0.1)+{w/60}*sin(on*0.2)':y='ih/2-(ih/zoom/2)+{h/40}*sin(on*0.12)+{h/60}*sin(on*0.25)':d=1:s={w}x{h}"
    elif zoom_type == "pulse":
        vf = f"zoompan=z='1+0.12*abs(sin(on*{2*math.pi/frames}))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h}"
    elif zoom_type == "reveal":
        vf = f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,fade=t=in:d={duration}:color=black"
    else:
        vf = f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2"

    if color_filter:
        vf = f"{vf},{color_filter}"

    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", image_path,
        "-vf", vf,
        "-t", str(duration),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "fast", "-crf", "23",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr.strip()}")
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

    image_files = get_image_files()
    log(f"Using {len(image_files)} images (sorted by date)")

    prompt_weights = None
    duration_range = [MIN_IMAGE_DURATION, MAX_IMAGE_DURATION]
    color_filter = None
    forced_effect = None
    prompt_path = os.path.join(IMAGES_FOLDER, "prompt.txt")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_text = f.read()
        prompt_weights, duration_range, color_filter, forced_effect = parse_prompt(prompt_text)
        log(f"Prompt: {prompt_text[:60]}..." if len(prompt_text) > 60 else f"Prompt: {prompt_text}")

    script_path = os.path.join(IMAGES_FOLDER, "script.txt")
    script_exists = os.path.exists(script_path)

    # ===== SLIDESHOW MODE (no script, no audio) =====
    if not script_exists:
        log("No script found — generating silent slideshow")
        clip_paths = []

        for i, img_path in enumerate(image_files):
            clip_path = os.path.join(READY_FOLDER, f"clip_{i}.mp4")
            jitter = random.uniform(0.8, 1.2)
            create_ken_burns_image_clip(img_path, DURATION_PER_IMAGE * jitter, clip_path, prompt_weights, color_filter, forced_effect)
            actual_dur = get_duration(clip_path)
            if actual_dur <= 0:
                continue
            clip_paths.append(clip_path)
            log(f"Image {i + 1}/{len(image_files)} — {actual_dur:.1f}s")

        if not clip_paths:
            raise RuntimeError("No clips were generated")

        concat_path = os.path.join(READY_FOLDER, "slideshow_concat.txt")
        with open(concat_path, "w", encoding="utf-8") as f:
            for clip in clip_paths:
                f.write(f"file '{clip.replace(chr(92), '/')}'\n")

        final_output = os.path.join(OUTPUT_FOLDER, "final_video.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_path, "-c:v", "libx264", "-preset", "medium",
            "-crf", "20", final_output
        ], capture_output=True, text=True)

        if os.path.exists(concat_path):
            os.remove(concat_path)
        for clip in clip_paths:
            if os.path.exists(clip):
                try:
                    os.remove(clip)
                except PermissionError:
                    pass

        if os.path.exists(final_output):
            log(f"Done! Output: {final_output}")
            print(json.dumps({"type": "done", "output": final_output}), flush=True)
        else:
            raise RuntimeError("Final video not created")
        return

    # ===== AUDIO MODE (with script) =====
    with open(script_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
    if not paragraphs:
        raise ValueError("No paragraphs found in script.txt")

    log(f"Found {len(paragraphs)} paragraphs to process.")

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
            target_dur = min(random.uniform(duration_range[0], duration_range[1]), remaining)
            clip_path = os.path.join(READY_FOLDER, f"clip_{idx}_{len(selected_clips)}.mp4")
            create_ken_burns_image_clip(img_path, target_dur, clip_path, prompt_weights, color_filter, forced_effect)
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
        if len(sys.argv) > 2:
            DURATION_PER_IMAGE = float(sys.argv[2])
        asyncio.run(generate_video())
    except Exception as e:
        print(json.dumps({"type": "error", "message": str(e)}), flush=True)
        sys.exit(1)
