
from ultralytics import YOLO

model = YOLO("yolov8n.pt")


def detect_objects(frame):
    results = model.track(
        source=frame,
        conf=0.5,
        persist=True,
        tracker="bytetrack.yaml",
        verbose=False
    )

    annotated_frame = results[0].plot()

    detections = []
    boxes = results[0].boxes

    for index, box in enumerate(boxes):
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        track_id = None

        if boxes.id is not None:
            track_id = int(boxes.id[index])

        detections.append({
            "object": model.names[class_id],
            "confidence": round(confidence, 2),
            "track_id": track_id
        })

    # Extract model performance information
    speed = results[0].speed

    performance = {
        "preprocessing_ms": round(
            speed["preprocess"], 2
        ),
        "inference_ms": round(
            speed["inference"], 2
        ),
        "postprocessing_ms": round(
            speed["postprocess"], 2
        )
    }

    return annotated_frame, detections, performance
