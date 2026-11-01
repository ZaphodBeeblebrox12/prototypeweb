#!/usr/bin/env python3
"""One-off TradeThesis burned-in watermark prototype.

Takes one source video and creates a separate MP4 copy whose viewer identity
is encoded into the video frames. The original is never modified. This is a
visual/resource benchmark, not production DRM or a replacement for entitlement
checks and protected delivery.

Requires ffmpeg + ffprobe with libx264 and the drawtext filter enabled.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path


def run_json(command: list[str]) -> dict:
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def probe(path: Path) -> dict:
    data = run_json([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size,bit_rate:stream=codec_name,width,height,r_frame_rate,codec_type",
        "-of", "json", str(path),
    ])
    streams = data.get("streams", [])
    video = next((stream for stream in streams if stream.get("codec_type") == "video"), {})
    audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
    fmt = data.get("format", {})
    return {
        "duration_seconds": float(fmt.get("duration", 0) or 0),
        "size_bytes": int(fmt.get("size", 0) or 0),
        "bitrate_bps": int(fmt.get("bit_rate", 0) or 0),
        "video_codec": video.get("codec_name"),
        "width": int(video.get("width", 0) or 0),
        "height": int(video.get("height", 0) or 0),
        "frame_rate": video.get("r_frame_rate"),
        "has_audio": audio is not None,
        "audio_codec": audio.get("codec_name") if audio else None,
    }


def position_expression(rng: random.Random, interval: float, duration: float) -> str:
    """Make a deterministic pseudo-random, smoothly changing 0..1 position."""
    count = max(2, int(duration // interval) + 2)
    points = [rng.uniform(0.06, 0.78) for _ in range(count)]
    expression = f"{points[-1]:.6f}"
    for index in reversed(range(count - 1)):
        start = index * interval
        end = (index + 1) * interval
        a, b = points[index], points[index + 1]
        blend = f"({a:.6f}+({b-a:.6f})*min(1,max(0,(t-{start:.3f})/{interval:.3f})))"
        expression = f"if(lt(t,{end:.3f}),{blend},{expression})"
    return expression


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Original MP4/MOV/WebM source")
    parser.add_argument("--output", required=True, type=Path, help="New watermarked MP4 path")
    parser.add_argument("--email", required=True, help="Viewer email to burn into the copy")
    parser.add_argument("--display-name", default="", help="Optional viewer display name")
    parser.add_argument("--move-every", type=float, default=4.0, help="Seconds between watermark destination changes")
    parser.add_argument("--crf", type=int, default=23, help="H.264 quality (lower = better/larger; default 23)")
    parser.add_argument("--preset", default="veryfast", help="x264 preset (ultrafast..veryslow)")
    parser.add_argument("--sample-duration", type=float, default=0,
                        help="Optional short test only; 0 processes the full source")
    args = parser.parse_args()

    source = args.input.expanduser().resolve()
    destination = args.output.expanduser().resolve()
    email = args.email.strip()
    if not source.is_file():
        parser.error(f"Input file does not exist: {source}")
    if source == destination:
        parser.error("Output must be a different file; the source is never overwritten.")
    if not email or "\n" in email or "\r" in email:
        parser.error("Provide one non-empty email address on a single line.")
    if args.move_every < 1 or args.move_every > 60:
        parser.error("--move-every must be between 1 and 60 seconds.")
    if not 18 <= args.crf <= 30:
        parser.error("--crf must be between 18 and 30 for this prototype.")

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        parser.error("Both ffmpeg and ffprobe must be installed and on PATH.")

    before = probe(source)
    if not before["width"] or not before["height"] or before["duration_seconds"] <= 0:
        parser.error("The input does not contain a readable video stream.")
    duration = min(before["duration_seconds"], args.sample_duration) if args.sample_duration > 0 else before["duration_seconds"]

    # The tracking ID is unique to this source/viewer pair but does not expose a
    # raw internal database ID. It remains visible as part of the burned pixels.
    digest = hashlib.sha256()
    with source.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    source_hash = digest.hexdigest()
    tracking_id = hashlib.sha256(f"{email.lower()}:{source_hash}".encode()).hexdigest()[:10].upper()

    # Seed the movement path so the same viewer/source pair gets consistent
    # watermark positions if the prototype is regenerated for comparison.
    rng_seed = int(hashlib.sha256(f"{email.lower()}:{source_hash}:watermark".encode()).hexdigest()[:16], 16)
    rng = random.Random(rng_seed)
    x_position = position_expression(rng, args.move_every, duration)
    y_position = position_expression(rng, args.move_every, duration)

    # textfile avoids filter-string escaping problems with real email addresses.
    destination.parent.mkdir(parents=True, exist_ok=True)
    text_path = destination.with_suffix(destination.suffix + ".watermark.txt")
    name = args.display_name.strip()
    lines = [f"{name}  |  {email}" if name else email, f"TradeThesis viewer ID: {tracking_id}"]
    text_path.write_text("\n".join(lines), encoding="utf-8")
    try:
        # Use a compact translucent box plus a little inset margin. The entire
        # filter output is burned into pixels; there is no HTML overlay to remove.
        drawtext = (
            f"drawtext=textfile='{text_path.as_posix()}':reload=0:"
            "font='DejaVu Sans':fontsize='max(18,min(34,h*0.030))':"
            "fontcolor=white:line_spacing=5:box=1:boxborderw=12:"
            "boxcolor=black@0.62:borderw=1:bordercolor=white@0.35:"
            f"x='12+(w-text_w-24)*({x_position})':"
            f"y='12+(h-text_h-24)*({y_position})':"
            "shadowcolor=black@0.9:shadowx=1:shadowy=1"
        )
        cmd = [
            ffmpeg, "-hide_banner", "-y", "-i", str(source),
            "-map", "0:v:0", "-map", "0:a?",
        ]
        if args.sample_duration > 0:
            cmd += ["-t", f"{args.sample_duration:.3f}"]
        cmd += [
            "-vf", drawtext,
            "-c:v", "libx264", "-preset", args.preset, "-crf", str(args.crf),
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart", str(destination),
        ]
        start = time.perf_counter()
        completed = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = time.perf_counter() - start
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr[-5000:] or "FFmpeg failed without diagnostics.")
        after = probe(destination)
    finally:
        try:
            text_path.unlink()
        except FileNotFoundError:
            pass

    fps = duration / elapsed if elapsed > 0 else 0
    report = {
        "prototype_only": True,
        "source": str(source),
        "output": str(destination),
        "viewer_email": email,
        "tracking_id": tracking_id,
        "watermark_movement_seconds": args.move_every,
        "source_media": before,
        "output_media": after,
        "processed_duration_seconds": round(duration, 3),
        "processing_wall_time_seconds": round(elapsed, 3),
        "processing_speed_x_real_time": round(fps, 3),
        "size_change_bytes": after["size_bytes"] - before["size_bytes"],
        "size_change_percent": round((after["size_bytes"] / max(1, before["size_bytes"]) - 1) * 100, 2),
        "note": "The source was not modified. This is a watermarking demo, not DRM; the output still needs protected authenticated delivery in production.",
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, subprocess.SubprocessError, RuntimeError, ValueError) as exc:
        print(f"Prototype failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
