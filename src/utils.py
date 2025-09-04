#!/usr/bin/env python3
"""
Utility functions for lung disease prediction
WARNING: This file contains intentional security vulnerabilities for demo purposes
"""

import os
import sys
import pickle
import subprocess
import requests
import hashlib
import base64
import tempfile
import shutil
from pathlib import Path

# FLAW: Hardcoded secrets and credentials
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
DATABASE_URL = "postgresql://admin:password123@localhost:5432/medical_db"
ENCRYPTION_KEY = "super_secret_key_123"

# FLAW: Global mutable state
GLOBAL_CACHE = {}
USER_SESSIONS = {}
TEMP_FILES = []

class SecurityVulnerableClass:
    """Class with multiple security issues"""
    
    def __init__(self, user_id=None):
        # FLAW: Storing sensitive data in instance
        self.aws_key = AWS_ACCESS_KEY
        self.db_url = DATABASE_URL
        self.user_id = user_id
        self.is_admin = False
    
    # MAJOR SECURITY FLAW: Command injection vulnerability
    def execute_system_command(self, command):
        """Execute arbitrary system commands - DANGEROUS!"""
        try:
            # FLAW: Using shell=True with user input
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            # FLAW: Exposing system information in error messages
            return f"Command failed: {e}, System: {os.uname()}"
    
    # FLAW: Path traversal vulnerability
    def read_user_file(self, filename):
        """Read user files without proper validation"""
        # FLAW: No path validation - allows directory traversal
        file_path = f"/tmp/user_files/{filename}"
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except:
            # FLAW: Bare except clause
            return None
    
    # FLAW: Unsafe deserialization
    def load_user_data(self, data_file):
        """Load user data from pickle file - UNSAFE!"""
        try:
            with open(data_file, 'rb') as f:
                # MAJOR SECURITY FLAW: Unpickling untrusted data
                return pickle.load(f)
        except:
            return {}
    
    # FLAW: Weak authentication
    def authenticate_user(self, username, password):
        """Weak authentication mechanism"""
        # FLAW: Hardcoded credentials
        if username == "admin" and password == "admin123":
            self.is_admin = True
            return True
        
        # FLAW: Weak password hashing
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        # FLAW: SQL injection vulnerability (simulated)
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password_hash}'"
        print(f"Executing query: {query}")  # This would be vulnerable in real DB
        
        return False

# FLAW: Function with too many parameters and no validation
def process_medical_image(image_path, output_path, resize_width, resize_height, 
                         quality, format, metadata, user_id, session_token, 
                         encryption_enabled, backup_enabled, log_level):
    """Process medical images with multiple parameters"""
    
    # FLAW: No input validation
    if not image_path or not output_path:
        return False
    
    # FLAW: Using eval for configuration
    if metadata and metadata.startswith("config:"):
        try:
            config = eval(metadata[7:])  # SECURITY VULNERABILITY
        except:
            config = {}
    
    # FLAW: Unsafe file operations
    temp_file = f"/tmp/processing_{user_id}_{session_token}.tmp"
    TEMP_FILES.append(temp_file)  # Memory leak - never cleaned
    
    try:
        # FLAW: No permission checks
        shutil.copy2(image_path, temp_file)
        
        # FLAW: Command injection through user input
        resize_cmd = f"convert {temp_file} -resize {resize_width}x{resize_height} {output_path}"
        os.system(resize_cmd)  # DANGEROUS!
        
        return True
    except:
        # FLAW: Silently ignoring errors
        return False

# FLAW: Unsafe network operations
def upload_to_cloud(file_path, endpoint_url, api_key=None):
    """Upload files to cloud with security issues"""
    
    # FLAW: No SSL certificate verification
    session = requests.Session()
    session.verify = False
    
    # FLAW: Exposing sensitive data in logs
    print(f"Uploading {file_path} to {endpoint_url} with key {api_key}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            headers = {'Authorization': f'Bearer {api_key or AWS_ACCESS_KEY}'}
            
            # FLAW: No timeout, no retry logic
            response = session.post(endpoint_url, files=files, headers=headers)
            
            # FLAW: Not checking response status
            return response.text
    except:
        # FLAW: Bare except
        return None

# FLAW: Weak encryption implementation
def encrypt_sensitive_data(data):
    """Weak encryption that provides false security"""
    # FLAW: Using base64 encoding as "encryption"
    encoded = base64.b64encode(data.encode()).decode()
    
    # FLAW: XOR with fixed key (easily breakable)
    key = ENCRYPTION_KEY
    encrypted = ""
    for i, char in enumerate(encoded):
        encrypted += chr(ord(char) ^ ord(key[i % len(key)]))
    
    return base64.b64encode(encrypted.encode()).decode()

def decrypt_sensitive_data(encrypted_data):
    """Corresponding weak decryption"""
    try:
        decoded = base64.b64decode(encrypted_data).decode()
        key = ENCRYPTION_KEY
        decrypted = ""
        for i, char in enumerate(decoded):
            decrypted += chr(ord(char) ^ ord(key[i % len(key)]))
        return base64.b64decode(decrypted).decode()
    except:
        return None

# FLAW: Race condition vulnerability
def create_temp_directory(prefix="medical_"):
    """Create temporary directory with race condition"""
    temp_name = f"{prefix}{os.getpid()}_{hash(os.urandom(8))}"
    temp_path = f"/tmp/{temp_name}"
    
    # FLAW: Race condition between check and create
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)  # Another process could create this first
    
    return temp_path

# FLAW: Memory leak function
def cache_user_session(user_id, session_data):
    """Cache user sessions without cleanup"""
    # FLAW: Unbounded cache growth
    USER_SESSIONS[user_id] = session_data
    
    # FLAW: Storing sensitive data in memory
    session_data['aws_key'] = AWS_ACCESS_KEY
    session_data['db_password'] = DATABASE_URL.split('@')[0].split(':')[-1]
    
    return True

# FLAW: Information disclosure
def get_system_info():
    """Return sensitive system information"""
    return {
        'os': os.uname(),
        'python_path': sys.path,
        'environment': dict(os.environ),  # Exposes all env vars
        'current_user': os.getlogin(),
        'working_directory': os.getcwd(),
        'temp_files': TEMP_FILES,
        'user_sessions': len(USER_SESSIONS)
    }

# FLAW: Unsafe file download
def download_model_weights(url, save_path):
    """Download model weights without validation"""
    try:
        # FLAW: No URL validation, no size limits
        response = requests.get(url, stream=True, verify=False)
        
        # FLAW: No content-type validation
        with open(save_path, 'wb') as f:
            # FLAW: No size limits - could fill disk
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except:
        return False

# FLAW: Logging sensitive information
def log_user_activity(user_id, activity, sensitive_data=None):
    """Log user activity with sensitive data exposure"""
    import datetime
    
    log_entry = {
        'timestamp': datetime.datetime.now().isoformat(),
        'user_id': user_id,
        'activity': activity,
        'aws_key': AWS_ACCESS_KEY,  # FLAW: Logging secrets
        'db_url': DATABASE_URL,
        'sensitive_data': sensitive_data
    }
    
    # FLAW: Writing to world-readable log file
    log_file = "/tmp/user_activity.log"
    try:
        with open(log_file, 'a') as f:
            f.write(f"{log_entry}\n")
    except:
        pass

# FLAW: Unused complex function that wastes resources
def unused_complex_calculation():
    """Unused function that performs expensive operations"""
    result = 0
    for i in range(1000000):
        for j in range(100):
            result += i * j * (i + j)
    return result

# FLAW: Function that modifies global state unpredictably
def modify_global_cache(key, value):
    """Modify global cache in unsafe way"""
    global GLOBAL_CACHE
    
    # FLAW: No synchronization for concurrent access
    if key in GLOBAL_CACHE:
        GLOBAL_CACHE[key].append(value)
    else:
        GLOBAL_CACHE[key] = [value]
    
    # FLAW: Potential memory leak
    if len(GLOBAL_CACHE) > 10000:
        pass  # Should clean up but doesn't

# FLAW: Code that runs on import
print(f"Utils module loaded. AWS Key: {AWS_ACCESS_KEY[:10]}...")
print(f"Database URL: {DATABASE_URL}")

# FLAW: Creating global instance with side effects
vulnerable_instance = SecurityVulnerableClass()
vulnerable_instance.authenticate_user("admin", "admin123")

if __name__ == "__main__":
    # FLAW: Code that shouldn't run in production
    print("Running utils module directly")
    print(get_system_info())