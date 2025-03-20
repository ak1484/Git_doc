import os
import time
import hashlib

def get_repo_structure(repo_path):
    """
    Recursively scans the repository and returns a list of all file paths.
    
    Args:
        repo_path (str): Path to the repository
        
    Returns:
        list: List of file paths
    """
    file_paths = []
    ignored_dirs = ['.git', '__pycache__', 'node_modules', 'venv', '.env']
    ignored_extensions = ['.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe']
    
    for root, dirs, files in os.walk(repo_path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        
        for file in files:
            # Skip ignored file extensions
            if any(file.endswith(ext) for ext in ignored_extensions):
                continue
                
            file_path = os.path.join(root, file)
            file_paths.append(file_path)
    
    return file_paths

def get_file_metadata(file_path):
    """
    Retrieves metadata for a file, including size, last modified time, and content hash.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        dict: Dictionary containing file metadata
    """
    try:
        stat_info = os.stat(file_path)
        
        # Calculate file hash for efficient change detection
        file_hash = calculate_file_hash(file_path)
        
        metadata = {
            'path': file_path,
            'size': stat_info.st_size,
            'last_modified': stat_info.st_mtime,
            'content_hash': file_hash,
            'relative_path': os.path.relpath(file_path)
        }
        
        return metadata
    except Exception as e:
        print(f"Error getting metadata for {file_path}: {e}")
        return None

def calculate_file_hash(file_path):
    """
    Calculates SHA-256 hash of a file's content for change detection.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: Hexadecimal hash digest
    """
    try:
        hash_obj = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            # Read in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
                
        return hash_obj.hexdigest()
    except Exception as e:
        print(f"Error calculating hash for {file_path}: {e}")
        return None

def is_text_file(file_path):
    """
    Determines if a file is a text file that can be parsed for documentation.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if the file is likely a text file, False otherwise
    """
    # Common text file extensions
    text_extensions = [
        '.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp',
        '.html', '.css', '.md', '.txt', '.json', '.xml', '.yml', '.yaml',
        '.sh', '.bash', '.rb', '.php', '.go', '.rs', '.swift'
    ]
    
    # Check if the file has a text extension
    if any(file_path.endswith(ext) for ext in text_extensions):
        return True
    
    # For files without recognized extensions, check the first few bytes
    try:
        with open(file_path, 'rb') as f:
            content = f.read(1024)
            return not bool(content.translate(None, bytes(range(32, 127)))) and b'\0' not in content
    except:
        return False

def get_file_content(file_path):
    """
    Reads the content of a text file safely.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: Content of the file or None if it couldn't be read
    """
    if not is_text_file(file_path):
        return None
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            # Try with a different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None