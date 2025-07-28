import json

def classify_strokes(keypoint_json_path: str):
    with open(keypoint_json_path, "r") as f:
        keypoints = json.load(f)

    strokes = []
    frame_names = sorted(keypoints.keys())

    for i, fname in enumerate(frame_names):
        landmarks = keypoints[fname]
        if not landmarks:
            strokes.append({"frame": fname, "stroke": "unknown"})
            continue

        try:
            lw = landmarks[15]  # left wrist
            rw = landmarks[16]  # right wrist
            ls = landmarks[11]  # left shoulder
            rs = landmarks[12]  # right shoulder
        except (TypeError, IndexError):
            strokes.append({"frame": fname, "stroke": "unknown"})
            continue

        avg_shoulder_y = (ls["y"] + rs["y"]) / 2
        avg_wrist_y = (lw["y"] + rw["y"]) / 2

        wrist_above_shoulder = avg_wrist_y < avg_shoulder_y - 0.05
        hands_apart = abs(lw["x"] - rw["x"]) > 0.15

        if wrist_above_shoulder:
            stroke_type = "serve"
        elif hands_apart:
            stroke_type = "forehand" if rw["x"] > lw["x"] else "backhand"
        else:
            stroke_type = "unknown"

        strokes.append({"frame": fname, "stroke": stroke_type})

    return strokes

def frame_to_seconds(frame_filename, fps):
    frame_num = int(frame_filename.split("_")[1].split(".")[0])
    return round(frame_num / fps, 2)

def group_strokes(strokes, fps):
    timeline = []
    if not strokes:
        return []

    current = {"stroke": strokes[0]["stroke"], "start": strokes[0]["frame"], "end": strokes[0]["frame"]}

    for s in strokes[1:]:
        if s["stroke"] == current["stroke"]:
            current["end"] = s["frame"]
        else:
            if current["stroke"] != "unknown":
                current["start_sec"] = frame_to_seconds(current["start"], fps)
                current["end_sec"] = frame_to_seconds(current["end"], fps)
                timeline.append(current)
            current = {"stroke": s["stroke"], "start": s["frame"], "end": s["frame"]}

    if current["stroke"] != "unknown":
        current["start_sec"] = frame_to_seconds(current["start"], fps)
        current["end_sec"] = frame_to_seconds(current["end"], fps)
        timeline.append(current)

    return timeline
