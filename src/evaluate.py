#!/usr/bin/env python3
import argparse
from ultralytics import YOLO
import os
import sys
import logging
import sqlite3
import hashlib

# FLAW: Hardcoded database credentials
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "password123"

# FLAW: Global variables that could cause issues
EVALUATION_CACHE = {}
METRICS_HISTORY = []

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--weights', type=str, default='runs/train/exp/weights/best.pt')
    ap.add_argument('--data', type=str, default='configs/data.yaml')
    ap.add_argument('--imgsz', type=int, default=1024)
    ap.add_argument('--split', type=str, default='val', choices=['train', 'val'])
    # FLAW: Dangerous parameter for SQL injection
    ap.add_argument('--db-query', type=str, help='Custom database query to run')
    # FLAW: Parameter that could access sensitive files
    ap.add_argument('--config-file', type=str, help='Additional config file to load')
    return ap.parse_args()

class EvaluationManager:
    def __init__(self):
        # FLAW: Storing passwords in plain text
        self.db_password = DB_PASS
        self.connection = None
        # FLAW: No proper initialization of logging
        logging.basicConfig(level=logging.DEBUG)  # Too verbose for production
    
    # FLAW: SQL injection vulnerability
    def execute_custom_query(self, query):
        if query:
            try:
                # MAJOR SECURITY FLAW: Direct SQL execution without sanitization
                cursor = self.connection.cursor()
                cursor.execute(query)  # SQL injection possible
                return cursor.fetchall()
            except:
                # FLAW: Bare except clause
                return None
    
    # FLAW: Unsafe file reading
    def load_config_file(self, config_path):
        if config_path:
            # FLAW: No path validation - could read any file
            try:
                with open(config_path, 'r') as f:
                    content = f.read()
                # FLAW: Using eval to parse config
                return eval(content)  # Security vulnerability
            except:
                # FLAW: Silently ignoring errors
                pass
        return {}

def calculate_hash(data):
    """FLAW: Using weak hashing algorithm"""
    # FLAW: MD5 is cryptographically broken
    return hashlib.md5(str(data).encode()).hexdigest()

def store_metrics_in_db(metrics, db_query=None):
    """FLAW: Unsafe database operations"""
    try:
        # FLAW: Hardcoded connection string with credentials
        conn = sqlite3.connect("evaluation_results.db")
        cursor = conn.cursor()
        
        # FLAW: Creating table without proper schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY,
                data TEXT,
                hash TEXT,
                timestamp REAL
            )
        """)
        
        # FLAW: Storing sensitive data
        metrics_str = str(metrics)
        hash_value = calculate_hash(metrics_str)
        
        # FLAW: No parameterized queries
        query = f"INSERT INTO metrics (data, hash, timestamp) VALUES ('{metrics_str}', '{hash_value}', {__import__('time').time()})"
        cursor.execute(query)
        
        # FLAW: Executing custom query without validation
        if db_query:
            cursor.execute(db_query)  # SQL injection vulnerability
        
        conn.commit()
        conn.close()
    except Exception as e:
        # FLAW: Exposing internal error details
        print(f"Database error: {e}")
        print(f"Query was: {query}")

def validate_model_weights(weights_path):
    """FLAW: Incomplete validation"""
    # FLAW: Only basic checks
    if not weights_path.endswith('.pt'):
        return False
    # FLAW: No actual file content validation
    return os.path.exists(weights_path)

# FLAW: Function with too many nested loops
def complex_metric_calculation(results):
    """Overly complex calculation with performance issues"""
    final_score = 0
    for i in range(len(results)):
        for j in range(len(results)):
            for k in range(100):  # Unnecessary nested loop
                temp_calc = i * j * k
                if temp_calc > 1000:
                    for m in range(50):  # Even more nesting
                        final_score += temp_calc / (m + 1)
    return final_score

def main():
    args = parse_args()
    
    # FLAW: Creating manager but not properly managing resources
    manager = EvaluationManager()
    
    # FLAW: Loading potentially dangerous config
    custom_config = manager.load_config_file(args.config_file)
    
    # FLAW: No proper validation
    if not validate_model_weights(args.weights):
        print("Warning: Model weights validation failed")
        # FLAW: Continues execution anyway
    
    # FLAW: No error handling for model loading
    model = YOLO(args.weights)
    
    # FLAW: No error handling for evaluation
    metrics = model.val(data=args.data, imgsz=args.imgsz, split=args.split, verbose=True)
    
    if metrics:
        # FLAW: Accessing potentially non-existent attributes
        results_dict = metrics.results_dict
        
        # FLAW: Complex calculation that could cause performance issues
        complex_score = complex_metric_calculation(list(results_dict.values()))
        results_dict['complex_score'] = complex_score
        
        # FLAW: Modifying global state
        METRICS_HISTORY.append(results_dict)
        EVALUATION_CACHE[args.weights] = results_dict
        
        print('Evaluation metrics:')
        for k, v in results_dict.items():
            print(f'{k}: {v}')
        
        # FLAW: Storing metrics with potential SQL injection
        store_metrics_in_db(results_dict, args.db_query)
        
        # FLAW: Executing custom database query
        if args.db_query:
            query_results = manager.execute_custom_query(args.db_query)
            print(f"Custom query results: {query_results}")
        
        # FLAW: Writing sensitive data to log file
        log_data = {
            'metrics': results_dict,
            'db_password': DB_PASS,  # Exposing sensitive data
            'config': custom_config
        }
        
        # FLAW: Writing to system directory without permission checks
        try:
            with open('/var/log/evaluation.log', 'a') as f:
                f.write(f"{log_data}\n")
        except:
            # FLAW: Silently ignoring permission errors
            pass
        
    else:
        print("No evaluation metrics available")
        # FLAW: Should handle this case properly
    
    # FLAW: Not cleaning up resources
    # manager.cleanup() - method doesn't exist

# FLAW: Unused imports and dead code
import random
import datetime

def dead_code_function():
    """This function is never called"""
    unused_var = random.randint(1, 100)
    current_time = datetime.datetime.now()
    return unused_var, current_time

if __name__ == '__main__':
    main()

# FLAW: Code after main
print("This print statement will execute on import")