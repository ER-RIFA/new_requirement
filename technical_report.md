# Technical Report: Multi-Object Detection & Persistent ID Tracking

## 1. Overview

This project is a multi-object tracking (MOT) pipeline for sports footage. The main idea is to detect all visible people in a video, give each one a unique ID, and keep that ID consistent throughout the clip even when they overlap or the camera moves.

I tested it on a football match clip from Pexels.

## 2. Detection Model

**Model:** YOLOv8m (medium) from the Ultralytics library

I chose YOLOv8 because its pretty much the standard right now for real-time detection. I tried the nano version first (`yolov8n`) but it kept missing players who were further from the camera, especially in wide angle shots. The medium variant is a bit slower but catches way more detections which matters for tracking.

The model comes pre-trained on COCO which already has the "person" class, so I just filter for class 0. I set the confidence threshold to 0.3 which might seem low, but I noticed that with 0.5 (the default) it was dropping partially visible players and then ByteTrack would lose their ID. Lower threshold = more false positives but fewer broken tracks, which felt like the right tradeoff.

I didn't consider `yolov8x` (the large one) because it was too slow on my machine and the accuracy gain wasnt worth the speed hit for this use case.

## 3. Tracking Algorithm

**Tracker:** ByteTrack (via Ultralytics integrated tracker)

I initially looked into DeepSORT since its what most tutorials use, but ran into an issue — DeepSORT uses appearance features to match detections, and in football, players on the same team all wear the same jersey. So it kept confusing same-team players and swapping their IDs. Not great.

ByteTrack works differently. Instead of appearance, it does two rounds of IoU matching:

1. First it matches high-confidence detections to existing tracks using IoU
2. Then it takes the leftover tracks and tries matching them with low-confidence detections that other trackers would just throw away

This second step is what makes it good for sports — when a player gets partially blocked by another player, their detection confidence drops but ByteTrack still picks them up instead of creating a new ID when they reappear.

## 4. Keeping IDs Consistent

A few things help with ID stability:

- Low confidence threshold (0.3) so we dont lose people during occlusion
- The track buffer keeps dead tracks alive for about 30 frames (~1 sec) before deleting them, so if someone disappears briefly they get their old ID back
- At 25-30fps theres enough overlap between consecutive frames for IoU matching to work

That said, its not perfect. If someone is fully hidden for more than a second or so, the track dies and they get a new ID. Also camera cuts break everything obviously — theres no re-identification module.

## 5. Pipeline Design

```
Input Video
    |
    v
Frame Reader (cv2)
    |
    v
YOLOv8 Detection + ByteTrack Tracking
    |
    v
Track History  -------->  Analytics
    |                     (trajectories, heatmap,
    v                      count graph, stats)
Annotation
(boxes, IDs, trails)
    |
    v
Output Video
```

Code is split into files:
- `detector.py` — standalone detection wrapper (used for testing, not in the main pipeline)
- `tracker.py` — detection+tracking combined, stores per-track history
- `visualize.py` — all the cv2 drawing stuff
- `analytics.py` — post-processing: plots, heatmaps, movement stats
- `pipeline.py` — ties everything together

## 6. Challenges

1. **Same jersey problem:** Since players on the same team look identical, appearance-based trackers (DeepSORT) kept mixing them up. Switching to ByteTrack which uses position instead of appearance mostly fixed this.

2. **Camera panning:** When the camera pans fast, everyone shifts position at once. This caused a bunch of ID switches early on. ByteTrack handles it okay since IoU still overlaps if the shift isnt too big between frames.

3. **Crowded areas:** Corners and set pieces are a nightmare — lots of players bunched together with overlapping boxes. This is where most remaining ID switches happen and I dont have a good fix for it.

4. **Players far from camera:** Very small players near the other end of the pitch sometimes fall below the confidence threshold. Lowering it further would help but then you start getting false positives from the crowd.

## 7. Where it Fails

- Long full occlusion (player completely behind someone for >30 frames) → track dies, new ID
- Camera cuts → all tracks reset, expected behavior
- Very fast lateral movement with low fps video → IoU drops to zero between frames
- Really compressed or low res footage degrades detection quality noticeably

## 8. Extra Features

| Feature | Done? |
|---|---|
| Trajectory visualization | Yes - draws all paths on dark canvas |
| Heatmap | Yes - gaussian smoothed density map |
| Object count over time | Yes - matplotlib line chart |
| Speed/distance estimation | Yes - pixel units only, no real-world calibration |
| Stats export | Yes - text file with per-person stats |

## 9. Things I'd Improve With More Time

- Adding a re-identification model (like OSNet) to handle ID recovery after long occlusions
- Camera motion compensation — estimating homography between frames to subtract camera movement before doing IoU
- Projecting to a top-down field view with manual calibration points
- Converting pixel distances to real meters (needs camera intrinsics or known reference distances)
- I tried doing team detection using jersey color but color thresholding was way too inconsistent under different lighting, would need a proper classifier

## 10. Environment

- Python 3.10
- Ultralytics YOLOv8
- OpenCV 4.8+
- NumPy, Matplotlib, SciPy
- Windows 10/11, GPU recommended but works on CPU (slower though, like 2-5 fps)
