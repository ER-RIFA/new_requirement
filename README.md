# Multi-Object Detection & Persistent ID Tracking

A computer vision pipeline for detecting and tracking multiple players in sports footage. Uses YOLOv8 for detection and ByteTrack for tracking.

## What it does

- Detects all visible people in every frame of a video
- Gives each person a unique ID that stays consistent across the clip
- Handles occlusion, camera movement, and crowded scenes (mostly)
- Outputs an annotated video with bounding boxes, IDs, and motion trails
- Generates analytics: trajectory maps, heatmaps, object counts, movement stats

## Sample Video

I used a publicly available football match clip from Pexels:
https://www.pexels.com/video/men-playing-football-11474931/

You can use any video — just point `--input` to your file.

## Project Structure

```
├── main.py            # CLI entry point
├── config.py          # hyperparameters and paths
├── detector.py        # YOLOv8 detection wrapper
├── tracker.py         # multi-object tracker
├── pipeline.py        # video processing
├── visualize.py       # drawing / annotation
├── analytics.py       # trajectory, heatmap, stats
├── utils.py           # helper functions
├── requirements.txt
├── technical_report.md
├── output/            # generated outputs
└── screenshots/       # sample frames
```

## Setup

You need Python 3.9+ and pip.

```bash
cd ai_project_task

# create virtual env (optional but recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
```

YOLOv8 weights (`yolov8m.pt`) download automatically on first run.

## How to Run

```bash
# basic usage
python main.py --input path/to/video.mp4

# with live preview
python main.py --input video.mp4 --preview

# skip analytics
python main.py --input video.mp4 --no-analytics
```

Options:
- `--input`, `-i` — input video path (required)
- `--output`, `-o` — output path (default: `output/tracked_output.mp4`)
- `--preview` — show live preview while processing
- `--no-analytics` — skip heatmap/trajectory generation
- `--no-screenshots` — don't save sample frames

## Outputs

After processing, check the `output/` folder:

- `tracked_output.mp4` — annotated video with boxes, IDs, trails
- `trajectories.png` — all movement paths on dark background
- `heatmap.png` — density heatmap of positions
- `object_count.png` — line chart of visible subjects over time
- `movement_stats.txt` — per-subject distance and speed

## Limitations

- ID switches happen during heavy occlusion (players running behind each other for extended periods)
- Speed/distance values are in pixels, not real-world units
- Low resolution or compressed footage will make detection worse
- On CPU its slow (~2-5 fps), GPU recommended
- Camera cuts reset all tracking

## Configuration

Tunable parameters are in `config.py`:

```python
MODEL_WEIGHTS = "yolov8m.pt"
CONF_THRESHOLD = 0.3
TRACKER_CONFIG = "bytetrack.yaml"
TRAIL_LENGTH = 40
```

## Dependencies

- ultralytics (YOLOv8)
- opencv-python
- numpy
- matplotlib
- scipy
- scikit-learn
- Pillow
