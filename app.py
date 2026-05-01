# streamlit app for showing tracking results
import streamlit as st
from PIL import Image
import os

st.set_page_config(
    page_title="Multi-Object Tracking Pipeline",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Multi-Object Detection & Tracking")
st.markdown("Real-time player tracking in sports footage using **YOLOv8** + **ByteTrack**")
st.markdown("---")

# --- overview section ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Detection Model", "YOLOv8m")
with col2:
    st.metric("Tracking Algorithm", "ByteTrack")
with col3:
    st.metric("Unique Subjects Tracked", "33")

st.markdown("---")

# --- how it works ---
st.header("How It Works")
st.markdown("""
1. **Detection** — YOLOv8 medium model detects all visible people in each frame
2. **Tracking** — ByteTrack assigns persistent IDs using two-pass IoU matching
3. **Annotation** — Bounding boxes, IDs, and motion trails drawn on each frame
4. **Analytics** — Trajectory maps, heatmaps, and movement statistics generated
""")

st.markdown("---")

# --- sample frame ---
st.header("📸 Sample Tracked Frame")
screenshot_path = "screenshots/frame_00039.png"
if os.path.exists(screenshot_path):
    img = Image.open(screenshot_path)
    st.image(img, caption="Frame with bounding boxes, IDs, and motion trails", use_container_width=True)
else:
    st.info("Sample screenshot not available")

st.markdown("---")

# --- analytics outputs ---
st.header("📊 Analytics Results")

tab1, tab2, tab3 = st.tabs(["Trajectories", "Heatmap", "Object Count"])

with tab1:
    traj_path = "output/trajectories.png"
    if os.path.exists(traj_path):
        img = Image.open(traj_path)
        st.image(img, caption="All tracked movement paths", use_container_width=True)
        st.markdown("Green dots = start position, Red dots = end position")
    else:
        st.info("Trajectory plot not available")

with tab2:
    heat_path = "output/heatmap.png"
    if os.path.exists(heat_path):
        img = Image.open(heat_path)
        st.image(img, caption="Position density heatmap", use_container_width=True)
        st.markdown("Brighter areas = more player activity")
    else:
        st.info("Heatmap not available")

with tab3:
    count_path = "output/object_count.png"
    if os.path.exists(count_path):
        img = Image.open(count_path)
        st.image(img, caption="Number of visible subjects per frame", use_container_width=True)
    else:
        st.info("Object count chart not available")

st.markdown("---")

# --- movement stats ---
st.header("📈 Movement Statistics")

stats_path = "output/movement_stats.txt"
if os.path.exists(stats_path):
    with open(stats_path, "r") as f:
        lines = f.readlines()

    # parse into a table
    import pandas as pd
    data = []
    for line in lines[2:]:  # skip header and separator
        line = line.strip()
        if not line or line.startswith("Total") or line.startswith("-"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 4:
            try:
                data.append({
                    "Track ID": int(float(parts[0])),
                    "Distance (px)": round(float(parts[1]), 1),
                    "Avg Speed (px/s)": round(float(parts[2]), 1),
                    "Frames Tracked": int(float(parts[3]))
                })
            except ValueError:
                continue

    if data:
        df = pd.DataFrame(data)

        # highlight key stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Subjects", len(df))
        with col2:
            top = df.loc[df["Distance (px)"].idxmax()]
            st.metric("Most Active (by distance)", f"ID {int(top['Track ID'])}")
        with col3:
            longest = df.loc[df["Frames Tracked"].idxmax()]
            st.metric("Longest Tracked", f"ID {int(longest['Track ID'])} ({int(longest['Frames Tracked'])} frames)")

        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.code(f.read())
else:
    st.info("Stats file not available")

st.markdown("---")

# --- pipeline config ---
st.header("⚙️ Pipeline Configuration")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    | Parameter | Value |
    |---|---|
    | Model | YOLOv8m (medium) |
    | Confidence Threshold | 0.3 |
    | IoU Threshold | 0.45 |
    | Target Class | Person (COCO 0) |
    """)
with col2:
    st.markdown("""
    | Parameter | Value |
    |---|---|
    | Tracker | ByteTrack |
    | Track Buffer | 30 frames |
    | Trail Length | 40 frames |
    | Heatmap Blur | 25px |
    """)

st.markdown("---")

# --- video source ---
st.header("🎬 Video Source")
st.markdown("""
Sample video: [Football match clip from Pexels](https://www.pexels.com/video/men-playing-football-11474931/)

The pipeline accepts any video file — run locally with:
```bash
python main.py --input your_video.mp4
```
""")

st.markdown("---")

# --- tech stack ---
st.header("🛠️ Tech Stack")
cols = st.columns(4)
techs = [
    ("🔍 Detection", "YOLOv8 (Ultralytics)"),
    ("🎯 Tracking", "ByteTrack"),
    ("🖼️ Processing", "OpenCV + NumPy"),
    ("📊 Visualization", "Matplotlib"),
]
for col, (label, tech) in zip(cols, techs):
    with col:
        st.markdown(f"**{label}**")
        st.markdown(tech)

st.markdown("---")
st.markdown("Built for Multi-Object Detection & Tracking assignment • [GitHub Repo](https://github.com/ER-RIFA/new_requirement)")
