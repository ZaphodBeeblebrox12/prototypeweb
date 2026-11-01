# Burned-in watermark prototype

This is an isolated proof of concept. It creates a new MP4 with the viewer identity and a deterministic tracking code burned into the video pixels. The source file is never overwritten.

## Requirements

- FFmpeg and FFprobe on PATH
- FFmpeg built with `libx264` and `drawtext`
- A local copy of one source lesson video

## Example

From the repository root:

```bash
python backend/scripts/prototype_burned_watermark.py \
  --input "/path/to/source-lesson.mp4" \
  --output "/path/to/source-lesson-watermarked.mp4" \
  --email "viewer@example.com" \
  --display-name "Test Viewer" \
  --move-every 4 \
  --sample-duration 90
```

Remove `--sample-duration 90` to process the whole lesson. The default H.264 settings are CRF 23 and preset `veryfast`; adjust only after comparing visual quality and resource use.

The command reports source/output dimensions, codecs, sizes, processing time and speed relative to real time. It derives a short tracking code from the viewer email and source hash, and the watermark moves smoothly between pseudo-random positions at the requested interval.

## Scope and security

- Prototype only: it does not change the Django lesson player, source upload, Google Drive objects, or existing encrypted HLS rendition.
- The MP4 output is a separate test artifact. Do not expose it publicly.
- Burning text into video pixels means Developer Tools cannot remove that watermark from the rendered frames. It does **not** stop screen recording, re-encoding, cropping, or a determined user from obscuring parts of the image.
- Production use still needs authenticated delivery, per-viewer output isolation, cache expiry/deletion, job limits, and protection against one user requesting another user's rendition.
