# Lung Disease Detection with YOLOv10 (VinBigData)

This project trains a YOLOv10 model to detect chest X‑ray abnormalities using the VinBigData Chest X-ray Abnormalities Detection dataset.

What you can do
- Download the dataset from Kaggle
- Prepare data in YOLO format (train/val split)
- Train a YOLOv10 model
- Run inference on images or a folder
- Evaluate with mAP

Quick start
1) Create a Python environment (recommended Python 3.10+)
2) Install requirements
   pip install -r requirements.txt
3) Configure Kaggle credentials (one of the two options)
   - Environment variables (temporary)
     export KAGGLE_USERNAME="your_username"
     export KAGGLE_KEY="your_key"
   - Or put credentials in ~/.kaggle/kaggle.json and set permissions
     {
       "username": "your_username",
       "key": "your_key"
     }
     chmod 600 ~/.kaggle/kaggle.json
4) Download the dataset
   python scripts/download_dataset.py
5) Prepare the dataset (YOLO format + split)
   python scripts/prepare_vinbigdata_yolo.py
6) Train YOLOv10
   python src/train.py
7) Inference (images or folder)
   python src/infer.py --source data/images/sample.jpg
8) Evaluate
   python src/evaluate.py

Project structure
- configs/
  - data.yaml          # YOLO dataset config
- data/                # Created locally; holds raw and processed data (git-ignored)
- models/              # Saved weights (git-ignored)
- notebooks/           # Optional experiments
- scripts/
  - download_dataset.py
  - prepare_vinbigdata_yolo.py
- src/
  - train.py
  - infer.py
  - evaluate.py
- requirements.txt

Notes
- We do not commit datasets or API keys.
- Default settings use the full VinBigData class list and a 80/20 train/val split at image level.
- Default image size: 1024, batch size: 8 (auto-reduced if needed).

Troubleshooting
- If Kaggle download fails, verify credentials are set and accepted in Kaggle.
- If CUDA isn’t available, training runs on CPU but will be slow. Set device in src/train.py if needed.
