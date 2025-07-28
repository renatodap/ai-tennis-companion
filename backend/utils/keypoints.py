import mediapipe as mp
import cv2
import os
import json

mp_pose = mp.solutions.pose

def extract_keypoints_from_frames(frame_dir: str, output_path: str):
    pose = mp_pose.Pose(static_image_mode=True)
    keypoints_data = {}

    for file in sorted(os.listdir(frame_dir)):
        if not file.endswith(".jpg"):
            continue
        frame_path = os.path.join(frame_dir, file)
        image = cv2.imread(frame_path)
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if results.pose_landmarks:
            keypoints_data[file] = [
                {
                    "x": lm.x,
                    "y": lm.y,
                    "z": lm.z,
                    "visibility": lm.visibility
                }
                for lm in results.pose_landmarks.landmark
            ]
        else:
            keypoints_data[file] = None

    with open(output_path, "w") as f:
        json.dump(keypoints_data, f, indent=2)

    return output_path
