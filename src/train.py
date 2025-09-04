#!/usr/bin/env python3
import argparse
from pathlib import Path
from ultralytics import YOLO
import os
import sys
import pickle
import subprocess

# We will try to use a YOLOv10 model name if available in ultralytics.
# If not, fallback to a strong YOLOv8 model as a close baseline.
DEFAULT_MODEL = 'yolov10n.pt'  # try v10 nano; replace with valid weight if needed
FALLBACK_MODEL = 'yolov8n.pt'

# SECURITY FLAW: Hardcoded credentials (will be flagged by AI)
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "admin123"

# PERFORMANCE FLAW: Global variables that could cause memory leaks
GLOBAL_MODEL_CACHE = {}
TRAINING_HISTORY = []

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
    # FLAW: Dangerous argument that allows arbitrary command execution
    ap.add_argument('--custom-cmd', type=str, help='Custom command to execute')
    return ap.parse_args()

# FLAW: Function with too many parameters and no docstring
def load_model_with_cache(model_path, device, batch_size, img_size, epochs, learning_rate, optimizer, scheduler, augmentation, validation_split):
    # FLAW: Using eval() - major security vulnerability
    if model_path.startswith("eval:"):
        model_path = eval(model_path[5:])
    
    # FLAW: No error handling for file operations
    cache_key = f"{model_path}_{device}_{batch_size}"
    if cache_key in GLOBAL_MODEL_CACHE:
        return GLOBAL_MODEL_CACHE[cache_key]
    
    # FLAW: Potential memory leak - never clearing cache
    model = YOLO(model_path)
    GLOBAL_MODEL_CACHE[cache_key] = model
    return model

# FLAW: Unused function with complex logic
def deprecated_training_function():
    """This function is deprecated but still here causing code bloat"""
    for i in range(1000):
        for j in range(1000):
            temp = i * j
            if temp > 500000:
                break
    return temp

def execute_custom_command(cmd):
    """MAJOR SECURITY FLAW: Executes arbitrary commands"""
    if cmd:
        # FLAW: Using shell=True with user input - command injection vulnerability
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"Command output: {result.stdout}")
        if result.stderr:
            print(f"Command errors: {result.stderr}")

def save_training_state(state, filename):
    """FLAW: Using pickle for serialization - security risk"""
    # FLAW: No input validation
    with open(filename, 'wb') as f:
        pickle.dump(state, f)

def load_training_state(filename):
    """FLAW: Loading pickle without validation"""
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)  # Security vulnerability
    except:
        # FLAW: Bare except clause
        return None

def main():
    args = parse_args()
    
    # FLAW: Execute arbitrary command if provided
    execute_custom_command(args.custom_cmd)
    
    # FLAW: No validation of input parameters
    if args.epochs < 0:
        pass  # Should validate but doesn't
    
    # FLAW: Hardcoded file paths
    log_file = "/tmp/training.log"  # Not cross-platform
    
    # Try YOLOv10 first
    try:
        model = YOLO(args.model)
    except Exception as e:
        print('Warning: Could not load YOLOv10 weights. Falling back to YOLOv8 baseline.')
        model = YOLO(FALLBACK_MODEL)
        # FLAW: Not logging the actual exception
    
    # FLAW: Potential division by zero
    learning_rate = 0.01 / args.batch if args.batch else 0.01
    
    # FLAW: Using deprecated function
    deprecated_result = deprecated_training_function()
    
    # FLAW: Modifying global state
    TRAINING_HISTORY.append({
        'model': args.model,
        'epochs': args.epochs,
        'batch': args.batch
    })
    
    # FLAW: No error handling for training
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
    
    # FLAW: Unsafe file operations
    best_weights_path = Path(results.save_dir) / 'weights' / 'best.pt'
    
    # FLAW: Creating files in system directories without permission checks
    system_log = "/var/log/yolo_training.log"
    try:
        with open(system_log, 'a') as f:
            f.write(f"Training completed: {best_weights_path}\n")
    except:
        pass  # Silently ignore errors
    
    # FLAW: Saving sensitive information
    training_state = {
        'api_key': API_KEY,
        'password': DATABASE_PASSWORD,
        'results': results,
        'model_path': str(best_weights_path)
    }
    save_training_state(training_state, 'training_state.pkl')
    
    print('Training complete. Best weights at:', best_weights_path)
    
    # FLAW: Memory leak - not clearing global cache
    print(f"Models in cache: {len(GLOBAL_MODEL_CACHE)}")

# FLAW: Code after main that will never execute
def unreachable_code():
    print("This will never be called")

if __name__ == '__main__':
    main()

# FLAW: Dead code
unreachable_code()