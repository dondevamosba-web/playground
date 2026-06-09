"""
Content repurposing pipeline for reels and videos.

Takes a source video and:
  1. Extracts audio and generates captions via OpenAI Whisper
  2. Resizes/crops to multiple platform formats
  3. Embeds burned-in captions (optional)
  4. Generates formatted caption text with hashtags for each platform

Requires: ffmpeg, OPENAI_API_KEY in .env

Usage:
  python3 tools/repurpose_video.py --input .tmp/reels/reel_01.mp4
  python3 tools/repurpose_video.py --input video.mp4 --platforms reels feed youtube
  python3 tools/repurpose_video.py --input video.mp4 --caption-only
  python3 tools/repurpose_video.py --input video.mp4 --no-captions
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
import urllib.error

from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TMP_DIR = os.path.join(os.path.dirname(__file__), "..", ".tmp")

# Platform output specs: (width, height, label)
PLATFORM_SPECS = {
    "reels":   (1080, 1920, "instagram_reels"),   # Instagram Reels, TikTok, Stories
    "feed":    (1080, 1080, "instagram_feed"),     # Instagram Feed square
    "youtube": (1920, 1080, "youtube"),            # YouTube, Facebook video
    "shorts":  (1080, 1920, "youtube_shorts"),     # YouTube Shorts
}

HASHTAG_SETS = {
    "marketing": "#marketingdigital #paidads #metaads #facebookads #digitalmarketing "
                 "#leadgeneration #smallbusiness #marketingtips #growthhacking",
    "agency":    "#agencia #marketingargentina #emprendedores #publicidadonline "
                 "#anunciosfacebook #googleads #resultados",
    "general":   "#entrepreneur #business #results #socialmedia #contentmarketing",
}


# ── Whisper captioning ────────────────────────────────────────────────────────

def extract_audio(video_path: str) -> str:
    audio_path = video_path.replace(".mp4", "_audio.mp3").replace(".mov", "_audio.mp3")
    audio_path = os.path.join(TMP_DIR, os.path.basename(audio_path))
    subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, "-q:a", "0", "-map", "a", audio_path],
        capture_output=True, check=True
    )
    return audio_path


def transcribe_whisper(audio_path: str) -> dict:
    if not OPENAI_API_KEY:
        print("  No OPENAI_API_KEY found — skipping transcription.")
        return {"text": "", "segments": []}

    import urllib.request
    import mimetypes

    url = "https://api.openai.com/v1/audio/transcriptions"

    # multipart/form-data upload without external libraries
    boundary = "----FormBoundary7MA4YWxkTrZu0gW"
    with open(audio_path, "rb") as f:
        audio_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="model"\r\n\r\n'
        f"whisper-1\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="response_format"\r\n\r\n'
        f"verbose_json\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(audio_path)}"\r\n'
        f"Content-Type: audio/mpeg\r\n\r\n"
    ).encode() + audio_data + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  Whisper API error {e.code}: {e.read().decode()[:200]}")
        return {"text": "", "segments": []}


def segments_to_srt(segments: list) -> str:
    lines = []
    for i, seg in enumerate(segments, 1):
        start = format_srt_time(seg["start"])
        end   = format_srt_time(seg["end"])
        lines.append(f"{i}\n{start} --> {end}\n{seg['text'].strip()}\n")
    return "\n".join(lines)


def format_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


# ── Video resizing ────────────────────────────────────────────────────────────

def resize_video(input_path: str, width: int, height: int, output_path: str,
                 srt_path: str = None):
    # Strategy: scale to fill, then crop to exact dimensions
    vf_filters = [
        f"scale=w={width}:h={height}:force_original_aspect_ratio=increase",
        f"crop={width}:{height}",
    ]
    if srt_path:
        # Burn in subtitles
        srt_escaped = srt_path.replace("'", "\\'").replace(":", "\\:")
        vf_filters.append(
            f"subtitles='{srt_escaped}':force_style='"
            f"FontName=Arial,FontSize=18,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,"
            f"BackColour=&H80000000,Bold=1,Alignment=2,MarginV=50'"
        )

    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", ",".join(vf_filters),
        "-c:v", "libx264", "-crf", "23", "-preset", "fast",
        "-c:a", "aac", "-b:a", "128k",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print(f"    ffmpeg error: {result.stderr.decode()[-300:]}")
        return False
    return True


# ── Caption copy generation ───────────────────────────────────────────────────

def generate_caption_copy(transcript: str, platform: str, hashtag_set: str = "general") -> str:
    if not transcript.strip():
        return f"[Add caption here]\n\n{HASHTAG_SETS.get(hashtag_set, '')}"

    # Use Claude CLI if available for a smarter caption
    try:
        prompt = (
            f"Write a compelling {platform} caption for this video transcript. "
            f"Max 150 words. Use conversational tone. End with a call to action. "
            f"No emojis unless natural. Transcript: {transcript[:500]}"
        )
        result = subprocess.run(
            ["claude", "-p", prompt, "--model", "haiku"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            caption = result.stdout.strip()
            return f"{caption}\n\n{HASHTAG_SETS.get(hashtag_set, '')}"
    except Exception:
        pass

    # Fallback: use raw transcript as caption seed
    short = transcript[:200].strip()
    if not short.endswith("."):
        short += "..."
    return f"{short}\n\n{HASHTAG_SETS.get(hashtag_set, '')}"


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",        required=True, help="Source video file")
    parser.add_argument("--platforms",    nargs="+", default=["reels"],
                        choices=list(PLATFORM_SPECS.keys()),
                        help="Output platform formats")
    parser.add_argument("--hashtags",     default="general",
                        choices=list(HASHTAG_SETS.keys()))
    parser.add_argument("--caption-only", action="store_true",
                        help="Only generate caption text, no video processing")
    parser.add_argument("--no-captions",  action="store_true",
                        help="Skip caption burn-in")
    parser.add_argument("--out-dir",      default=None)
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"File not found: {args.input}")
        sys.exit(1)

    base = os.path.splitext(os.path.basename(args.input))[0]
    out_dir = args.out_dir or os.path.join(TMP_DIR, "repurposed", base)
    os.makedirs(out_dir, exist_ok=True)

    # Step 1: Transcribe
    transcript = ""
    srt_path   = None
    print("Step 1: Transcribing audio via Whisper...")
    try:
        audio_path   = extract_audio(args.input)
        whisper_data = transcribe_whisper(audio_path)
        transcript   = whisper_data.get("text", "")
        segments     = whisper_data.get("segments", [])

        if transcript:
            print(f"  Transcript: {transcript[:100]}...")
            if segments and not args.no_captions:
                srt_content = segments_to_srt(segments)
                srt_path = os.path.join(out_dir, f"{base}.srt")
                with open(srt_path, "w") as f:
                    f.write(srt_content)
                print(f"  SRT saved → {srt_path}")
        else:
            print("  No speech detected or transcription failed.")

        os.remove(audio_path)
    except Exception as e:
        print(f"  Transcription skipped: {e}")

    # Step 2: Generate caption copy for each platform
    print("\nStep 2: Generating caption copy...")
    captions = {}
    for platform in args.platforms:
        caption = generate_caption_copy(transcript, platform, args.hashtags)
        captions[platform] = caption
        cap_file = os.path.join(out_dir, f"caption_{platform}.txt")
        with open(cap_file, "w") as f:
            f.write(caption)
        print(f"  [{platform}] Caption → {cap_file}")

    if args.caption_only:
        print(f"\nDone — captions saved to {out_dir}")
        return

    # Step 3: Resize for each platform
    print("\nStep 3: Resizing for platforms...")
    outputs = {}
    for platform in args.platforms:
        w, h, label = PLATFORM_SPECS[platform]
        out_path = os.path.join(out_dir, f"{base}_{label}.mp4")
        print(f"  [{platform}] {w}x{h} → {out_path}")
        ok = resize_video(args.input, w, h, out_path,
                          srt_path=srt_path if not args.no_captions else None)
        if ok:
            outputs[platform] = out_path
            print(f"    ✓ {os.path.getsize(out_path) / 1_000_000:.1f} MB")
        else:
            print(f"    ✗ Failed")

    # Step 4: Summary
    print(f"\n── Output summary ─────────────────────────────────")
    print(f"  Directory: {out_dir}")
    for platform, path in outputs.items():
        print(f"  {platform:<10} → {os.path.basename(path)}")
    if srt_path:
        print(f"  captions  → {os.path.basename(srt_path)}")
    print(f"\n  Next: upload videos + captions via post_instagram.py")


if __name__ == "__main__":
    main()
