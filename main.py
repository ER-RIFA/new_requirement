# entry point - run with: python main.py --input video.mp4

import argparse
import os
import sys
from pipeline import Pipeline


def parse_args():
    parser = argparse.ArgumentParser(
        description="Multi-Object Detection & Tracking Pipeline"
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to the input video file",
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Path for the annotated output video (default: output/tracked_output.mp4)",
    )
    parser.add_argument(
        "--preview", action="store_true",
        help="Show a live preview window while processing",
    )
    parser.add_argument(
        "--no-analytics", action="store_true",
        help="Skip generating trajectory/heatmap/stats after tracking",
    )
    parser.add_argument(
        "--no-screenshots", action="store_true",
        help="Don't save sample screenshot frames",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if not os.path.isfile(args.input):
        print(f"[ERROR] Video file not found: {args.input}")
        sys.exit(1)

    pipe = Pipeline(
        video_path=args.input,
        output_path=args.output,
    )

    pipe.run(
        show_preview=args.preview,
        save_screenshots=not args.no_screenshots,
        run_analytics=not args.no_analytics,
    )


if __name__ == "__main__":
    main()
