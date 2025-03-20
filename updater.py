from repo_parser import get_repo_structure, get_file_metadata
from doc_generator import generate_file_docs

def detect_changes(repo_path, vector_store):
    """
    Detect changes in the repository by comparing current file states with stored metadata.
    
    Args:
        repo_path (str): Path to the repository
        vector_store (VectorStore): Vector store containing file metadata and documentation
        
    Returns:
        list: List of changed file paths
    """
    # Get current file structure
    current_files = get_repo_structure(repo_path)
    
    # Get stored file paths
    stored_files = vector_store.get_all_files()
    
    # Identify new, modified, and deleted files
    changed_files = []
    
    # Check for new or modified files
    for file_path in current_files:
        current_metadata = get_file_metadata(file_path)
        
        if not current_metadata:
            continue
            
        stored_metadata = vector_store.get_metadata(file_path)
        
        if not stored_metadata:
            # New file
            changed_files.append(file_path)
        elif current_metadata['content_hash'] != stored_metadata['content_hash']:
            # Modified file
            changed_files.append(file_path)
    
    # Check for deleted files
    for file_path in stored_files:
        if file_path not in current_files:
            # Mark deleted files for removal
            changed_files.append(file_path)
    
    return changed_files

def update_changed_files(changed_files, vector_store, repo_path):
    """
    Update documentation for changed files.
    
    Args:
        changed_files (list): List of file paths that have changed
        vector_store (VectorStore): Vector store to update
        repo_path (str): Path to the repository
    """
    for file_path in changed_files:
        # Check if file exists (could be deleted)
        try:
            metadata = get_file_metadata(file_path)
            
            if metadata:
                # File exists, update documentation
                documentation = generate_file_docs(file_path)
                
                if documentation:
                    # Update or add the file in the vector store
                    if vector_store.get(file_path):
                        vector_store.update(file_path, metadata, documentation)
                    else:
                        vector_store.add(file_path, metadata, documentation)
            else:
                # File was deleted, remove from vector store
                vector_store.remove(file_path)
        except FileNotFoundError:
            # File was deleted, remove from vector store
            vector_store.remove(file_path)
    
    # Save the updated vector store
    vector_store.save()