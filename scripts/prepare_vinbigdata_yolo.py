#!/usr/bin/env python3
import json
import random
from pathlib import Path
import pandas as pd
import shutil
import yaml

RAW_DIR = Path('data/raw/vinbigdata')
OUT_DIR = Path('data/vinbigdata_yolo')
IMAGES_DIR = OUT_DIR / 'images'
LABELS_DIR = OUT_DIR / 'labels'

# Defaults
VAL_RATIO = 0.2
IMG_EXT = '.png'  # images are PNG in VinBigData after extraction

# Class mapping from VinBigData annotations
CLASSES = [
    'Aortic enlargement', 'Atelectasis', 'Calcification', 'Cardiomegaly',
    'Consolidation', 'ILD', 'Infiltration', 'Lung Opacity', 'Nodule/Mass',
    'Other lesion', 'Pleural effusion', 'Pleural thickening', 'Pneumothorax',
    'Pulmonary fibrosis'
]
NAME2ID = {name: i for i, name in enumerate(CLASSES)}


def ensure_dirs():
    (IMAGES_DIR / 'train').mkdir(parents=True, exist_ok=True)
    (IMAGES_DIR / 'val').mkdir(parents=True, exist_ok=True)
    (LABELS_DIR / 'train').mkdir(parents=True, exist_ok=True)
    (LABELS_DIR / 'val').mkdir(parents=True, exist_ok=True)


def load_annotations():
    # Train labels: typically at "train.csv" with bbox columns
    # Expected columns: image_id, class_name, xmin, ymin, xmax, ymax
    csv_path = RAW_DIR / 'train.csv'
    if not csv_path.exists():
        raise FileNotFoundError(f"Expected {csv_path} not found. Run download script first.")
    df = pd.read_csv(csv_path)

    # Some rows may indicate "No finding" with NaNs for boxes; we'll filter by valid boxes
    # Handle class naming differences (e.g., "No finding" or empty boxes)
    # Standardize column names
    cols = [c.lower() for c in df.columns]
    df.columns = cols

    # Try to map to expected field names
    # Heuristic: look for bbox columns
    bbox_cols = None
    for candidate in [
        ('xmin', 'ymin', 'xmax', 'ymax'),
        ('x_min', 'y_min', 'x_max', 'y_max'),
        ('x1', 'y1', 'x2', 'y2')
    ]:
        if all(c in df.columns for c in candidate):
            bbox_cols = candidate
            break
    if bbox_cols is None:
        raise ValueError('Could not find bbox columns in train.csv')

    # Class column name
    class_col = 'class_name' if 'class_name' in df.columns else (
        'class' if 'class' in df.columns else 'label'
    )
    if class_col not in df.columns:
        raise ValueError('Could not find class column (class_name/class/label) in train.csv')

    # Image id/name
    image_col = 'image_id' if 'image_id' in df.columns else 'image'
    if image_col not in df.columns:
        raise ValueError('Could not find image column (image_id/image) in train.csv')

    # Drop rows without bboxes
    for c in bbox_cols:
        df = df[df[c].notna()]

    # Keep only classes in CLASSES
    df = df[df[class_col].isin(CLASSES)]

    # Build per-image annotations
    anns = {}
    for _, row in df.iterrows():
        img_id = str(row[image_col])
        cls_name = row[class_col]
        x_min, y_min, x_max, y_max = [float(row[c]) for c in bbox_cols]
        if img_id not in anns:
            anns[img_id] = []
        anns[img_id].append({
            'cls': NAME2ID[cls_name],
            'bbox_xyxy': [x_min, y_min, x_max, y_max]
        })
    return anns


def find_image_path(image_id: str) -> Path:
    # Images are typically under train/ directory; try common locations
    candidates = [
        RAW_DIR / 'train' / f'{image_id}{IMG_EXT}',
        RAW_DIR / 'train_images' / f'{image_id}{IMG_EXT}',
        RAW_DIR / 'images' / f'{image_id}{IMG_EXT}'
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(f'Image file for {image_id} not found in raw folders')


def convert_to_yolo(anns):
    # For each image, write labels in YOLO format: class cx cy w h (normalized)
    # Requires image width/height; we can read from PNG metadata using PIL
    from PIL import Image

    items = list(anns.items())
    random.shuffle(items)
    val_size = int(len(items) * VAL_RATIO)
    val_set = set(k for k, _ in items[:val_size])

    for img_id, boxes in anns.items():
        img_path = find_image_path(img_id)
        with Image.open(img_path) as im:
            w, h = im.size
        # destination
        split = 'val' if img_id in val_set else 'train'
        dst_img = IMAGES_DIR / split / f'{img_id}.jpg'  # convert to JPG for speed
        dst_lbl = LABELS_DIR / split / f'{img_id}.txt'

        # Save image as JPG
        with Image.open(img_path) as im:
            rgb = im.convert('RGB')
            rgb.save(dst_img, format='JPEG', quality=95)

        # Write label file
        lines = []
        for b in boxes:
            x1, y1, x2, y2 = b['bbox_xyxy']
            cx = (x1 + x2) / 2.0 / w
            cy = (y1 + y2) / 2.0 / h
            bw = (x2 - x1) / w
            bh = (y2 - y1) / h
            lines.append(f"{b['cls']} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}")
        dst_lbl.write_text('\n'.join(lines))


def write_data_yaml():
    cfg = {
        'path': str(OUT_DIR),
        'train': 'images/train',
        'val': 'images/val',
        'nc': len(CLASSES),
        'names': CLASSES,
    }
    Path('configs').mkdir(exist_ok=True)
    with open('configs/data.yaml', 'w') as f:
        yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True)


def main():
    ensure_dirs()
    anns = load_annotations()
    convert_to_yolo(anns)
    write_data_yaml()
    print('Preparation complete. YOLO dataset at', OUT_DIR)


if __name__ == '__main__':
    main()
