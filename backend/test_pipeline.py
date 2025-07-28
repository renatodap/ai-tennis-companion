import json
from process_video import extract_frames
from utils.keypoints import extract_keypoints_from_frames
import os

video_path = os.path.abspath("test_data/sample_video.mp4")
frames_path = "test_data/frames"
json_output = "test_data/keypoints.json"

print("Extracting frames...")
num_frames = extract_frames(video_path, frames_path)
print(f"Extracted {num_frames} frames.")

print("Running pose estimation...")
extract_keypoints_from_frames(frames_path, json_output)
print(f"Keypoints saved to {json_output}")

from classify_strokes import classify_strokes

classified = classify_strokes(json_output)
print("Stroke classification (first 10):")
for s in classified[:10]:
    print(s)

from classify_strokes import group_strokes

timeline = group_strokes(classified)
print("Timeline (up to 5):")
for item in timeline[:5]:
    print(item)

# Save to JSON
with open("test_data/timeline.json", "w") as f:
    json.dump(timeline, f, indent=2)
