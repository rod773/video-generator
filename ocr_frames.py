import pytesseract
from PIL import Image
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

FRAMES_DIR = r"D:\VIBE_CODE\video_generator\frames"
OUTPUT_FILE = r"D:\VIBE_CODE\video_generator\ocr_extracted.txt"

key_frames = {
    30: "00:00:30 - intro project",
    60: "00:01:00 - workflow explanation",
    120: "00:02:00 - imports section",
    125: "00:02:05 - imports detail",
    145: "00:02:25 - config section",
    160: "00:02:40 - config detail",
    180: "00:03:00 - video settings",
    200: "00:03:20 - utility functions",
    220: "00:03:40 - duration checker",
    230: "00:03:50 - image processing",
    245: "00:04:05 - Ken Burns effect",
    260: "00:04:20 - Ken Burns detail",
    275: "00:04:35 - audio generation",
    290: "00:04:50 - Edge-TTS code",
    305: "00:05:05 - main pipeline",
    315: "00:05:15 - pipeline detail",
    330: "00:05:30 - image selection",
    345: "00:05:45 - clip generation",
    360: "00:06:00 - concat/merge",
    375: "00:06:15 - cleanup section",
    390: "00:06:30 - final stitching",
    410: "00:06:50 - running demo",
    430: "00:07:10 - terminal output",
}

os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

results = []
for frame_num, desc in sorted(key_frames.items()):
    frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_num:05d}.png")
    if os.path.exists(frame_path):
        img = Image.open(frame_path)
        text = pytesseract.image_to_string(img, lang="eng")
        results.append(f"\n{'='*60}")
        results.append(f"FRAME {frame_num:05d} ({desc})")
        results.append(f"{'='*60}")
        results.append(text)
        print(f"OCR'd frame {frame_num:05d}")
    else:
        results.append(f"\n{'='*60}")
        results.append(f"FRAME {frame_num:05d} (FILE NOT FOUND)")
        results.append(f"{'='*60}")
        print(f"Frame {frame_num:05d} not found")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(results))

print(f"\nDone! Results saved to {OUTPUT_FILE}")
