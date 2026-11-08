import cv2


def open_camera(source=0):
    """
    Opens a video source.

    source can be:
    - 0 for the laptop webcam
    - A video file path
    - An RTSP stream URL
    """

    camera = cv2.VideoCapture(source)

    if not camera.isOpened():
        camera.release()
        raise RuntimeError(f"Unable to open video source: {source}")

    print(f"Video source connected: {source}")

    return camera