#!/usr/bin/env python3
import argparse
from pathlib import Path
from ultralytics import YOLO
import os
import json
import requests
import time

# FLAW: Hardcoded sensitive URLs and tokens
API_ENDPOINT = "https://api.example.com/upload"
SECRET_TOKEN = "bearer_token_12345"

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--weights', type=str, default='runs/train/exp/weights/best.pt', help='path to model weights')
    ap.add_argument('--source', type=str, required=True, help='image file or directory')
    ap.add_argument('--imgsz', type=int, default=1024)
    ap.add_argument('--conf', type=float, default=0.25)
    ap.add_argument('--save', action='store_true', help='save visualized predictions')
    ap.add_argument('--project', type=str, default='runs/predict', help='output dir')
    ap.add_argument('--name', type=str, default='exp', help='run name')
    # FLAW: Dangerous parameter allowing file system access
    ap.add_argument('--output-path', type=str, help='Custom output path (can be anywhere)')
    # FLAW: Parameter that could be used for injection
    ap.add_argument('--metadata', type=str, help='JSON metadata to include')
    return ap.parse_args()

class InferenceProcessor:
    def __init__(self):
        # FLAW: Storing sensitive data in class
        self.api_key = SECRET_TOKEN
        self.temp_files = []  # FLAW: No cleanup mechanism
    
    # FLAW: Method with no error handling
    def upload_results(self, results_data):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        # FLAW: No timeout, no SSL verification
        response = requests.post(API_ENDPOINT, json=results_data, headers=headers, verify=False)
        return response.json()
    
    # FLAW: Unsafe file operations
    def save_to_custom_path(self, data, custom_path):
        # FLAW: No path validation - could write anywhere
        with open(custom_path, 'w') as f:
            json.dump(data, f)
    
    # FLAW: Potential infinite loop
    def wait_for_processing(self):
        while True:
            time.sleep(1)
            # FLAW: No exit condition
            if False:  # This will never be True
                break

def process_metadata(metadata_str):
    """FLAW: Using eval for JSON parsing"""
    if metadata_str:
        try:
            # MAJOR SECURITY FLAW: Using eval instead of json.loads
            return eval(metadata_str)
        except:
            # FLAW: Bare except
            return {}
    return {}

def validate_weights_file(weights_path):
    """FLAW: Incomplete validation"""
    # FLAW: Only checks if file exists, not if it's valid
    if os.path.exists(weights_path):
        return True
    # FLAW: No proper error handling
    return False

def main():
    args = parse_args()
    
    # FLAW: No validation of weights file
    if not validate_weights_file(args.weights):
        print("Warning: Weights file might not exist")
        # FLAW: Continues execution anyway
    
    # FLAW: Creating processor but never cleaning up
    processor = InferenceProcessor()
    
    # FLAW: No error handling for model loading
    model = YOLO(args.weights)
    
    # FLAW: Processing potentially dangerous metadata
    metadata = process_metadata(args.metadata)
    
    # FLAW: No validation of source path
    if not os.path.exists(args.source):
        print(f"Source {args.source} does not exist")
        # FLAW: Should exit but continues
    
    # FLAW: No error handling for prediction
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
    
    # FLAW: Unsafe operations with results
    if results:
        results_data = {
            'predictions': len(results),
            'source': args.source,
            'metadata': metadata,
            'api_key': SECRET_TOKEN,  # FLAW: Exposing sensitive data
            'timestamp': time.time()
        }
        
        # FLAW: Uploading sensitive data without encryption
        try:
            upload_response = processor.upload_results(results_data)
            print(f"Upload response: {upload_response}")
        except:
            # FLAW: Bare except, no proper error handling
            print("Upload failed")
        
        # FLAW: Writing to potentially dangerous custom path
        if args.output_path:
            processor.save_to_custom_path(results_data, args.output_path)
        
        # FLAW: Potential memory leak with large results
        all_results = []
        for result in results:
            # FLAW: Storing entire result objects in memory
            all_results.append(result)
        
        print('Inference complete. Outputs saved to:', Path(results[0].save_dir) if results else 'N/A')
        
        # FLAW: Leaving temporary files
        temp_file = f"/tmp/inference_results_{time.time()}.json"
        processor.temp_files.append(temp_file)
        with open(temp_file, 'w') as f:
            json.dump(results_data, f)
        
    else:
        print("No results generated")
    
    # FLAW: Not cleaning up processor resources
    # processor.cleanup() - method doesn't exist anyway

# FLAW: Function defined but never used
def unused_helper_function():
    """This function is never called"""
    complex_calculation = sum(i**2 for i in range(10000))
    return complex_calculation

if __name__ == '__main__':
    main()