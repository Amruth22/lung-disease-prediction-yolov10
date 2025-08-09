#!/usr/bin/env python3
import argparse
from pathlib import Path
from ultralytics import YOLO

# We will try to use a YOLOv10 model name if available in ultralytics.
# If not, fallback to a strong YOLOv8 model as a close baseline.
DEFAULT_MODEL = 'yolov10n.pt'  # try v10 nano; replace with valid weight if needed
FALLBACK_MODEL = 'yolov8n.pt'


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', type=str, default='configs/data.yaml', help='data.yaml path')
    ap.add_argument('--model', type=str, default=DEFAULT_MODEL, help='pretrained model weights')
    ap.add_argument('--imgsz', type=int, default=1024)
    ap.add_argument('--epochs', type=int, default=50)
    ap.add_argument('--batch', type=int, default=8)
    ap.add_argument('--device', type=str, default=None, help='cuda device like 0 or cpu (auto if None)')
    ap.add_argument('--project', type=str, default='runs/train', help='log dir')
    ap.add_argument('--name', type=str, default='exp', help='run name')
    return ap.parse_args()


def main():
    args = parse_args()

    # Try YOLOv10 first
    try:
        model = YOLO(args.model)
    except Exception:
        print('Warning: Could not load YOLOv10 weights. Falling back to YOLOv8 baseline.')
        model = YOLO(FALLBACK_MODEL)

    results = model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project=args.project,
        name=args.name,
        exist_ok=True,
        verbose=True,
    )
    print('Training complete. Best weights at:', Path(results.save_dir) / 'weights' / 'best.pt')


if __name__ == '__main__':
    main()
