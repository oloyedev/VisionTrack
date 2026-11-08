# VisionTrack

VisionTrack detects, tracks, and records objects from a live RTSP video feed. It combines YOLOv8 object detection, ByteTrack multi-object tracking, PostgreSQL session storage, and a Streamlit analytics dashboard.

The repository includes [MediaMTX](https://mediamtx.org/) to serve a local RTSP feed and `videos/cctv_test.mp4` to make local testing possible without a CCTV camera.

## What it does

- Reads the configured RTSP stream and displays an annotated live video window.
- Detects COCO object classes using the YOLOv8 nano model (`yolov8n.pt`).
- Assigns persistent ByteTrack IDs to detected objects across frames.
- Counts unique tracked objects and objects currently visible in the frame.
- Records a detection session and one row for each unique track in PostgreSQL.
- Shows stored session, category, and recent-detection analytics in Streamlit.

## Architecture

```text
RTSP camera or test video
          |
          v
      MediaMTX (:8554)
          |
          v
 detect.py -> YOLOv8 + ByteTrack -> annotated OpenCV window
     |                  |
     |                  +-> in-memory FPS and visibility metrics
     v
 PostgreSQL <---------------------- app.py (Streamlit dashboard)
```

## Requirements

- Python 3.10 or later
- PostgreSQL, with permission to create tables in the selected database
- An RTSP video source, or the bundled MediaMTX server and sample video
- [FFmpeg](https://ffmpeg.org/) to publish the sample MP4 as an RTSP stream

Install the application dependencies in a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install ultralytics opencv-python psycopg[binary] python-dotenv pandas streamlit
```

`detector.py` expects `yolov8n.pt` in the project root. If it is not present, Ultralytics downloads it the first time the model is loaded.

## Configure PostgreSQL

Create a database, then create `.env` in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=visiontrack
DB_USER=postgres
DB_PASSWORD=your_password
```

Credentials remain local because `.env` is ignored by Git. The detection service creates the required tables when it starts.

## Run locally with the bundled test video

Open three PowerShell terminals in the project root.

1. Start the local MediaMTX server:

   ```powershell
   .\mediamtx\mediamtx.exe
   ```

2. In a second terminal, publish the bundled video to the `cctv` RTSP path. The `-re` option publishes at the source frame rate and `-stream_loop -1` repeats the video.

   ```powershell
   ffmpeg -re -stream_loop -1 -i .\videos\cctv_test.mp4 -c:v libx264 -preset veryfast -tune zerolatency -an -f rtsp -rtsp_transport tcp rtsp://127.0.0.1:8554/cctv
   ```

3. In a third terminal, start detection:

   ```powershell
   .\venv\Scripts\Activate.ps1
   python detect.py
   ```

Press `Q` while the OpenCV video window is focused to stop the detector. It releases the video source, closes the window, and marks the database session as ended.

## Use a real RTSP camera

The stream URL is currently set directly in [`detect.py`](detect.py):

```python
VIDEO_SOURCE = "rtsp://127.0.0.1:8554/cctv"
```

Replace it with your camera URL, or publish the camera to that MediaMTX path. `camera.open_camera()` accepts a camera index, local video-file path, or RTSP URL, although the main detection script currently uses the RTSP value above.

## Launch the dashboard

After at least one detection session, start the dashboard in a separate terminal:

```powershell
.\venv\Scripts\Activate.ps1
streamlit run app.py
```

The dashboard provides:

- Total sessions, stored unique objects, and detected categories
- A bar chart and table of objects by category
- The 20 most recent persisted detections
- Session start/end timestamps and unique-object counts

## Data model

| Table | Stored data |
| --- | --- |
| `detection_sessions` | An auto-incrementing ID plus session start and end timestamps. |
| `detected_objects` | Session ID, ByteTrack ID, YOLO class name, confidence, and first-seen timestamp. |

`detected_objects` has a unique constraint on `(session_id, track_id)`. A tracked object is therefore persisted once per session; detections without a ByteTrack ID are not stored.

## Project layout

| Path | Purpose |
| --- | --- |
| `detect.py` | Main detection loop, live overlay, FPS calculation, and session lifecycle. |
| `detector.py` | Loads YOLOv8, runs ByteTrack, and returns annotations, detections, and timing data. |
| `processor.py` | Maintains in-memory unique and currently visible object counts. |
| `database.py` | PostgreSQL schema creation and session/detection persistence. |
| `app.py` | Streamlit analytics dashboard. |
| `camera.py` | Reusable video-source connection helper. |
| `mediamtx/` | Bundled MediaMTX RTSP server and configuration. |
| `videos/cctv_test.mp4` | Sample footage for local RTSP publishing and testing. |

## Notes

- YOLO tracking runs at a confidence threshold of `0.5` with `bytetrack.yaml`.
- The on-screen FPS is a moving average of the last 30 processed frames.
- `mediamtx/mediamtx.yml` enables RTSP on port `8554`; its `all_others` path accepts the locally published `cctv` stream.
