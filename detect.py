
import cv2
import time
from collections import deque
from camera import open_camera

from detector import detect_objects
from processor import create_analytics, update_analytics

from database import (
    create_tables,
    start_session,
    save_detections,
    end_session
)


def display_analytics(frame, analytics, performance, average_fps):

    total_unique = len(analytics["seen_objects"])

    current_visible = sum(
        analytics["visible_by_class"].values()
    )

    cv2.putText(
        frame,
        f"Currently Visible: {current_visible}",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Total Unique Objects: {total_unique}",
        (20, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    y_position = 100

    for name, count in analytics["visible_by_class"].items():
        cv2.putText(
            frame,
            f"{name}: {count}",
            (20, y_position),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        y_position += 30

   
    cv2.putText(
        frame,
        f"FPS: {average_fps:.2f}",
        (20, 450),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Inference: {performance['inference_ms']} ms",
        (20, 480),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2
    )

    return frame


def start_detection():

    fps_history = deque(maxlen=30)

    VIDEO_SOURCE = "rtsp://127.0.0.1:8554/cctv"
    cap = cv2.VideoCapture("rtsp://127.0.0.1:8554/cctv", cv2.CAP_FFMPEG)

    camera = open_camera(VIDEO_SOURCE)

    if not camera.isOpened():
        print("Unable to access webcam.")
        return

    create_tables()
    session_id = start_session()

    analytics = create_analytics()

    print("VisionTrack Analytics Started")
    print("Press Q to exit.")

    try:
        while True:

            frame_start = time.perf_counter()

            success, frame = camera.read()

            if not success:
                print("Unable to capture frame.")
                break

            annotated_frame, detections, performance = detect_objects(frame)

         
            new_detections = [
                item for item in detections
                if item["track_id"] is not None
                and item["track_id"] not in analytics["seen_objects"]
            ]

          
            save_detections(session_id, new_detections)

            
            analytics = update_analytics(
                detections,
                analytics
            )

            
            elapsed = time.perf_counter() - frame_start

            if elapsed > 0:
                fps_history.append(1 / elapsed)

            average_fps = sum(fps_history) / len(fps_history)

            
            annotated_frame = display_analytics(
                annotated_frame,
                analytics,
                performance,
                average_fps
            )

            cv2.imshow(
                "VisionTrack AI Analytics",
                annotated_frame
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()
        end_session(session_id)

    print("\nSESSION SUMMARY")
    print("Total unique objects:", len(analytics["seen_objects"]))


if __name__ == "__main__":
    start_detection()
