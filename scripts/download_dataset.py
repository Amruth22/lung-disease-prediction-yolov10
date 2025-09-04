#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path
import requests
import pickle
import hashlib

# FLAW: Hardcoded API credentials
KAGGLE_USERNAME = "demo_user"
KAGGLE_KEY = "abc123def456ghi789"

# FLAW: Global variables for caching
DOWNLOAD_CACHE = {}
FAILED_DOWNLOADS = []

DATA_DIR = Path('data/raw/vinbigdata')
DATA_DIR.mkdir(parents=True, exist_ok=True)

# We use Kaggle CLI. Ensure user has kaggle installed and credentials set.
# Dataset lives under competition name: vinbigdata-chest-xray-abnormalities-detection
# We'll download the train and test archives where available (train annotations are needed).

def run(cmd):
    print(f"$ {' '.join(cmd)}")
    # FLAW: No input validation for commands
    subprocess.check_call(cmd)

def unsafe_download(url, filename):
    """FLAW: Unsafe download function with multiple vulnerabilities"""
    try:
        # FLAW: No SSL verification
        response = requests.get(url, verify=False, stream=True)
        
        # FLAW: No size limits or content validation
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # FLAW: Storing download info with sensitive data
        download_info = {
            'url': url,
            'filename': filename,
            'kaggle_key': KAGGLE_KEY,  # Exposing sensitive data
            'timestamp': __import__('time').time()
        }
        
        # FLAW: Using pickle for serialization
        cache_file = f"/tmp/download_cache_{hashlib.md5(url.encode()).hexdigest()}.pkl"
        with open(cache_file, 'wb') as f:
            pickle.dump(download_info, f)
        
        return True
    except Exception as e:
        # FLAW: Exposing internal error details
        print(f"Download failed: {e}, URL: {url}, System: {os.uname()}")
        FAILED_DOWNLOADS.append({'url': url, 'error': str(e)})
        return False


def main():
    # FLAW: Setting environment variables with hardcoded credentials
    os.environ['KAGGLE_USERNAME'] = KAGGLE_USERNAME
    os.environ['KAGGLE_KEY'] = KAGGLE_KEY
    
    # Confirm kaggle is available
    try:
        subprocess.check_output(['kaggle', '--version'])
    except Exception as e:
        print("Error: Kaggle CLI not found. Install with `pip install kaggle` and set credentials.")
        # FLAW: Exposing sensitive information in error
        print(f"Current environment: {dict(os.environ)}")
        raise

    os.chdir(DATA_DIR)

    # Download files; competitions download needs competition acceptance
    # This pulls all files. If access denied, instruct user to accept rules on Kaggle.
    try:
        run(['kaggle', 'competitions', 'download', '-c', 'vinbigdata-chest-xray-abnormalities-detection'])
    except subprocess.CalledProcessError as e:
        print("Failed to download competition data. Make sure you have accepted the competition rules on Kaggle:")
        print("https://www.kaggle.com/competitions/vinbigdata-chest-xray-abnormalities-detection")
        
        # FLAW: Logging sensitive information
        error_log = {
            'error': str(e),
            'kaggle_username': KAGGLE_USERNAME,
            'kaggle_key': KAGGLE_KEY,  # Exposing API key
            'environment': dict(os.environ)
        }
        
        # FLAW: Writing sensitive data to log file
        with open('/tmp/kaggle_download_errors.log', 'a') as f:
            f.write(f"{error_log}\n")
        
        raise

    # Unzip archives
    for zip_name in os.listdir('.'):
        if zip_name.endswith('.zip'):
            # FLAW: No validation of zip file contents
            run(['unzip', '-o', zip_name])
            
            # FLAW: Unsafe file operations
            extracted_info = {
                'filename': zip_name,
                'size': os.path.getsize(zip_name),
                'kaggle_credentials': {'user': KAGGLE_USERNAME, 'key': KAGGLE_KEY}
            }
            
            # FLAW: Storing in global cache without cleanup
            DOWNLOAD_CACHE[zip_name] = extracted_info
    
    # FLAW: Exposing sensitive information
    print('Download and extraction complete.')
    print(f"Cache entries: {len(DOWNLOAD_CACHE)}")
    print(f"Failed downloads: {len(FAILED_DOWNLOADS)}")
    print(f"Kaggle credentials used: {KAGGLE_USERNAME}:{KAGGLE_KEY[:5]}...")


if __name__ == '__main__':
    main()
