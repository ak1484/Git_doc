import os
import shutil

def create_mirrored_directory_structure(source_path, target_path):
    """
    Creates a directory structure in target_path that mirrors the structure in source_path.
    
    Args:
        source_path (str): Path to the source repository
        target_path (str): Path where the mirrored structure will be created
    """
    # Get all directories in the source path
    for root, dirs, _ in os.walk(source_path):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            relative_path = os.path.relpath(dir_path, source_path)
            target_dir = os.path.join(target_path, relative_path)
            os.makedirs(target_dir, exist_ok=True)
    
    # Ensure the root target directory exists too
    os.makedirs(target_path, exist_ok=True)

def save_file_documentation(file_path, documentation, repo_path, docs_path):
    """
    Saves the documentation for a file in the mirrored repository structure.
    
    Args:
        file_path (str): Path to the original file
        documentation (dict): Documentation object
        repo_path (str): Path to the original repository
        docs_path (str): Path to the documentation root directory
    
    Returns:
        str: Path to the saved documentation file
    """
    # Get relative path of the file in the repository
    relative_path = os.path.relpath(file_path, repo_path)
    
    # Construct the target file path in the docs directory
    # Use .md extension for all documentation files
    target_dir = os.path.dirname(os.path.join(docs_path, relative_path))
    os.makedirs(target_dir, exist_ok=True)
    
    # Create filename with .md extension
    filename = os.path.basename(file_path)
    target_file = os.path.join(target_dir, f"{filename}.md")
    
    # Prepare documentation content
    content = f"# Documentation for {filename}\n\n"
    content += f"**Original File Path:** `{relative_path}`\n\n"
    content += documentation.get("documentation", "No documentation available")
    
    # Write documentation to file
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return target_file

def remove_file_documentation(file_path, repo_path, docs_path):
    """
    Removes the documentation file for a deleted repository file.
    
    Args:
        file_path (str): Path to the original file
        repo_path (str): Path to the original repository
        docs_path (str): Path to the documentation root directory
        
    Returns:
        bool: True if file was removed, False otherwise
    """
    try:
        relative_path = os.path.relpath(file_path, repo_path)
        doc_file_path = os.path.join(docs_path, relative_path + ".md")
        
        if os.path.exists(doc_file_path):
            os.remove(doc_file_path)
            return True
        return False
    except Exception as e:
        print(f"Error removing documentation file: {e}")
        return False

def cleanup_empty_dirs(docs_path):
    """
    Removes empty directories from the documentation structure.
    
    Args:
        docs_path (str): Path to the documentation root directory
    """
    for root, dirs, files in os.walk(docs_path, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            
            # Check if directory is empty
            if not os.listdir(dir_path):
                os.rmdir(dir_path)