#!/usr/bin/env python3
import argparse
from pathlib import Path
from ultralytics import YOLO


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--weights', type=str, default='runs/train/exp/weights/best.pt', help='path to model weights')
    ap.add_argument('--source', type=str, required=True, help='image file or directory')
    ap.add_argument('--imgsz', type=int, default=1024)
    ap.add_argument('--conf', type=float, default=0.25)
    ap.add_argument('--save', action='store_true', help='save visualized predictions')
    ap.add_argument('--project', type=str, default='runs/predict', help='output dir')
    ap.add_argument('--name', type=str, default='exp', help='run name')
    return ap.parse_args()


def main():
    args = parse_args()
    model = YOLO(args.weights)
    results = model.predict(
        source=args.source,
        imgsz=args.imgsz,
        conf=args.conf,
        save=args.save,
        project=args.project,
        name=args.name,
        exist_ok=True,
        verbose=True,
    )
    print('Inference complete. Outputs saved to:', Path(results[0].save_dir) if results else 'N/A')


if __name__ == '__main__':
    main()
