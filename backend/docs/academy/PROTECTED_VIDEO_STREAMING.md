# Protected Academy video delivery

This feature adds private source-video storage, FFmpeg HLS packaging, authenticated
AES-128 key/segment delivery, and an intermittent moving learner watermark.

## Important protection boundary

This is a self-hosted protection layer, not commercial DRM. The original MP4 is
never exposed as a public URL. The browser receives an encrypted HLS playlist,
segments, and a key only after Django verifies the logged-in user, current
lesson entitlement, and the same Django session. The key and every segment
request are checked again.

An entitled browser must receive the AES-128 key to play the video. A technically
determined paying learner can inspect browser traffic, save the stream and key,
or capture the screen. The watermark helps identify casual redistribution; it
does not make recording impossible. Widevine, FairPlay, and PlayReady DRM need
a licensed DRM/key service and are a separate upgrade.

## Production storage and runtime

### Current staging storage: Google Drive

Protected video source files, AES keys, HLS manifests, and HLS segments use the
same private Google Drive asset folder already used by Academy images. The
Drive objects are not shared publicly; the Django application reads them
server-side and streams them only after checking the learner's session and
course entitlement. Large source uploads use Drive's resumable-upload protocol.

Set `ACADEMY_VIDEO_STORAGE_BACKEND=google_drive` (the default), and ensure the
existing Academy Google Drive credentials and asset-folder ID are configured.
`ACADEMY_REQUIRE_DURABLE_VIDEO_STORAGE=true` remains enabled in production;
the application refuses to fall back silently to Render's ephemeral disk.

Google Drive is a practical staging bridge, not an ideal video CDN. Each HLS
segment request is proxied through Django and fetched from Drive, so playback
latency, Drive API quotas, and egress should be monitored before scaling.

### Future persistent-disk migration

When a persistent disk is available, switch storage without changing the
learner player or entitlement routes:

- `ACADEMY_VIDEO_STORAGE_BACKEND=filesystem`
- `ACADEMY_VIDEO_STORAGE_ROOT=/var/data/tradethesis-videos` (actual mount path)
- `ACADEMY_VIDEO_STORAGE_DURABLE=true`
- `ACADEMY_REQUIRE_DURABLE_VIDEO_STORAGE=true`

Copy existing Drive source files and generated HLS objects to the same logical
storage keys on the mounted disk before switching the backend. Verify every
video, then change the environment variable and deploy. Keep the Drive copy
until the migration is verified and rollback is no longer needed.

The Docker runtime image installs FFmpeg. If the current Render service uses
the native Python runtime rather than the Dockerfile, install FFmpeg in that
runtime before processing videos or set `ACADEMY_FFMPEG_BINARY` to its path.
The web process and processing command must use the same storage backend.

The source MP4s and generated HLS files live in the configured private
provider, outside `MEDIA_ROOT`, `STATIC_ROOT`, and any public CDN. Back up the
Drive folder or persistent disk; the database stores logical storage keys, not
a second copy of the video bytes. Storage, API quota, and streaming bandwidth
still have infrastructure costs.

## Upload and package a video

1. Run migrations: `python manage.py migrate`.
2. In Django Admin, open **Protected lesson videos** and add one row for the
   lesson. Upload an MP4, MOV, MKV, or WebM source file.
3. Return to the **Protected lesson videos** list, select the uploaded
   row, choose **Queue / rebuild protected streams for selected videos** from
   the Actions menu, and click **Go**. The Academy job queue runs the existing
   processing command in the background. Refresh the list to follow the status;
   a failed attempt records its error on the video row and is retried by the job
   queue according to its retry policy.

   On the current Render Free staging service, the queue is drained by the
   in-process scheduler. Long-running video jobs refresh their job lease so the
   five-minute stale-job reaper does not start a duplicate encode. This is
   suitable for short, low-volume staging tests only: FFmpeg shares the web
   service's CPU and memory. Use a dedicated background worker or media
   processing service for production workloads and longer videos; do not
   increase the Render plan without reviewing the cost first.

4. Confirm that the row is marked **Protected stream ready**. The learner lesson
   page will then use the protected HLS player automatically.
5. Replace each paid lesson's legacy `video_url` with a protected video before
   keeping `ACADEMY_ALLOW_LEGACY_VIDEO_URLS=false`. In production, legacy
   external MP4 URLs are hidden by default; set the flag to `true` only during
   a controlled migration window because those links are not protected.

## Player and watermark

The browser uses hls.js for HLS playback where the browser lacks native HLS
support; Safari can use its native HLS implementation. The learner's full name
and email appear over the video for 9 seconds, move to a new position roughly
every 3.6 seconds while visible, then disappear for 22 seconds. This is an
on-screen deterrent rather than a forensic server-side watermark.

Tickets are signed, bound to the current Django user and session, and expire
after `ACADEMY_VIDEO_TICKET_MAX_AGE` seconds (default 14,400 / four hours).
Every key and segment request rechecks the lesson's access policy.

## Rollback

To revert only the player feature, remove the protected-video record from the
lesson and set `ACADEMY_ALLOW_LEGACY_VIDEO_URLS=true` only if the old URL is
intentionally meant to remain available. Do not expose the private storage
directory through a web server or CDN.
