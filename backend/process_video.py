import cv2
import os

def extract_frames(video_path: str, output_dir: str, max_frames=200):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"❌ Could not open video: {video_path}")
        return 0, 0.0  # no frames, no fps

    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Detected FPS: {fps}")

    saved = 0
    while cap.isOpened() and saved < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        frame_path = os.path.join(output_dir, f"frame_{saved:04d}.jpg")
        cv2.imwrite(frame_path, frame)
        saved += 1

    cap.release()
    return saved, fps


