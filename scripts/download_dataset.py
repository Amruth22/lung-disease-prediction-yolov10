#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

DATA_DIR = Path('data/raw/vinbigdata')
DATA_DIR.mkdir(parents=True, exist_ok=True)

# We use Kaggle CLI. Ensure user has kaggle installed and credentials set.
# Dataset lives under competition name: vinbigdata-chest-xray-abnormalities-detection
# We'll download the train and test archives where available (train annotations are needed).

def run(cmd):
    print(f"$ {' '.join(cmd)}")
    subprocess.check_call(cmd)


def main():
    # Confirm kaggle is available
    try:
        subprocess.check_output(['kaggle', '--version'])
    except Exception as e:
        print("Error: Kaggle CLI not found. Install with `pip install kaggle` and set credentials.")
        raise

    os.chdir(DATA_DIR)

    # Download files; competitions download needs competition acceptance
    # This pulls all files. If access denied, instruct user to accept rules on Kaggle.
    try:
        run(['kaggle', 'competitions', 'download', '-c', 'vinbigdata-chest-xray-abnormalities-detection'])
    except subprocess.CalledProcessError:
        print("Failed to download competition data. Make sure you have accepted the competition rules on Kaggle:")
        print("https://www.kaggle.com/competitions/vinbigdata-chest-xray-abnormalities-detection")
        raise

    # Unzip archives
    for zip_name in os.listdir('.'):
        if zip_name.endswith('.zip'):
            run(['unzip', '-o', zip_name])
    print('Download and extraction complete.')


if __name__ == '__main__':
    main()
