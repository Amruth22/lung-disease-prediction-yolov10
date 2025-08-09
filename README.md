# Lung Disease Detection with YOLOv10 (VinBigData)

This project trains an object detection model on chest X‑rays using the VinBigData Chest X-ray Abnormalities Detection dataset. It targets 14 abnormalities with bounding boxes.

What you can do
- Download the dataset from Kaggle (locally)
- Prepare data in YOLO format with a train/val split
- Train a YOLO model (tries YOLOv10; falls back to YOLOv8 if needed)
- Run inference on images or folders and save visualizations
- Evaluate with mAP on the validation set

Quick start
1) Create a Python environment (Python 3.10+ recommended)
2) Install requirements
   pip install -r requirements.txt
3) Configure Kaggle credentials (choose one)
   - Temporary environment variables (shell session only)
     export KAGGLE_USERNAME="your_username"
     export KAGGLE_KEY="your_key"
   - Or create ~/.kaggle/kaggle.json and set permissions
     {
       "username": "your_username",
       "key": "your_key"
     }
     chmod 600 ~/.kaggle/kaggle.json
4) Accept competition rules on Kaggle (required for download)
   https://www.kaggle.com/competitions/vinbigdata-chest-xray-abnormalities-detection
5) Download the dataset
   python scripts/download_dataset.py
6) Prepare the dataset (YOLO format + 80/20 split)
   python scripts/prepare_vinbigdata_yolo.py
7) Train the model
   python src/train.py
   - Defaults: imgsz=1024, epochs=50, batch=8
   - Tries yolov10n.pt first; if unavailable, falls back to yolov8n.pt automatically
8) Inference (save predictions with --save)
   python src/infer.py --source data/vinbigdata_yolo/images/val --save
9) Evaluate mAP on the val set
   python src/evaluate.py

Project structure
- configs/
  - data.yaml          # YOLO dataset config (auto-updated by prepare script)
- data/
  - raw/vinbigdata/    # Downloaded raw files (created locally)
  - vinbigdata_yolo/   # Processed YOLO dataset (images/ and labels/)
- models/              # Saved weights (git-ignored)
- scripts/
  - download_dataset.py
  - prepare_vinbigdata_yolo.py
- src/
  - train.py
  - infer.py
  - evaluate.py
- requirements.txt
- .gitignore

Defaults and assumptions
- Task: object detection (bounding boxes) only
- Dataset: VinBigData with 14 classes
- Split: 80% train / 20% val by image
- Image size: 1024; Batch size: 8; Epochs: 50
- Device: auto (GPU if available, else CPU)

Security and data policy
- Do NOT commit API keys or datasets to the repo.
- .gitignore excludes data/, models/, and Kaggle credentials.
- Keep your keys in environment variables or ~/.kaggle/kaggle.json.

Tips
- Low VRAM? Reduce --imgsz and/or --batch in src/train.py or CLI args.
- Mixed precision (AMP) is used automatically by ultralytics when possible.
- You can point --weights in src/infer.py to any trained .pt file.

Troubleshooting
- Kaggle download fails: ensure credentials are set and competition rules are accepted.
- File not found during prepare: make sure download completed and files are extracted under data/raw/vinbigdata/.
- "Could not load YOLOv10 weights": ultralytics may not include YOLOv10 weights in your version; training will fall back to YOLOv8 automatically. You can later provide a valid YOLOv10 .pt path via --model in src/train.py.
