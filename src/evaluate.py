#!/usr/bin/env python3
import argparse
from ultralytics import YOLO


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--weights', type=str, default='runs/train/exp/weights/best.pt')
    ap.add_argument('--data', type=str, default='configs/data.yaml')
    ap.add_argument('--imgsz', type=int, default=1024)
    ap.add_argument('--split', type=str, default='val', choices=['train', 'val'])
    return ap.parse_args()


def main():
    args = parse_args()
    model = YOLO(args.weights)
    metrics = model.val(data=args.data, imgsz=args.imgsz, split=args.split, verbose=True)
    print('Evaluation metrics:')
    for k, v in metrics.results_dict.items():
        print(f'{k}: {v}')


if __name__ == '__main__':
    main()
