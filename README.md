# VisionTrack

VisionTrack is a real-time object detection and tracking system. It uses a webcam, YOLOv8 with ByteTrack tracking, PostgreSQL for persistent detection sessions, and a Streamlit dashboard for analytics.

## Features

- Live webcam object detection and annotation
- Object tracking with stable track IDs across frames
- Per-session storage of uniquely tracked objects
- On-screen visibility, object-count, FPS, and inference-time metrics
- Streamlit dashboard with session history, category summaries, and recent detections

## Requirements

- Python 3.10 or later
- A webcam accessible to OpenCV
- PostgreSQL

Install the Python dependencies:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install ultralytics opencv-python psycopg[binary] python-dotenv pandas streamlit
```

> The project includes `yolov8n.pt`. If it is absent, Ultralytics downloads the model when it is first loaded.

## Configuration

Create a `.env` file in the project root with your PostgreSQL connection settings:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=visiontrack
DB_USER=postgres
DB_PASSWORD=your_password
```

Create the database named by `DB_NAME` before running the detector. The detector creates its required tables automatically:

- `detection_sessions` records session start and end times.
- `detected_objects` records one unique tracked object per session.

## Run the project

Start real-time detection and tracking:

```powershell
python detect.py
```

Press `Q` in the video window to finish the detection session cleanly.

Launch the analytics dashboard in a separate terminal:

```powershell
streamlit run app.py
```

For a camera-only check, without detection or database access:

```powershell
python camera.py
```

## Project structure

| File | Purpose |
| --- | --- |
| `detect.py` | Main live-detection loop, display overlay, and session lifecycle. |
| `detector.py` | Loads YOLOv8 and runs ByteTrack object detection/tracking. |
| `processor.py` | Tracks visible and unique object analytics in memory. |
| `database.py` | Creates tables and persists detection sessions and objects. |
| `app.py` | Streamlit analytics dashboard backed by PostgreSQL. |
| `camera.py` | Minimal webcam connectivity test. |

## Notes

- The detector uses the lightweight `yolov8n` model with a confidence threshold of `0.5`.
- The dashboard reads from the same PostgreSQL database used by the detector; run at least one detection session to populate it.
- Database credentials are intentionally excluded from version control through `.env`.
