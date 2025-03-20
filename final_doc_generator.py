import os
import re

def generate_file_doc_section(file_path, documentation):
    """
    Generate a documentation section for a single file with identifiable markers.
    
    Args:
        file_path (str): Path to the file
        documentation (dict): Documentation object
        
    Returns:
        str: Formatted documentation section with markers
    """
    relative_path = documentation.get("relative_path", file_path)
    doc_content = documentation.get("documentation", "No documentation available")
    
    # Create a section with identifiable markers for future updates
    section = f"""
<!-- START_DOC_SECTION: {relative_path} -->
## {os.path.basename(file_path)}

**Path:** `{relative_path}`

{doc_content}
<!-- END_DOC_SECTION: {relative_path} -->
"""
    return section

def generate_final_doc(vector_store, output_path):
    """
    Generate the final repository documentation by assembling all file documentation.
    
    Args:
        vector_store (VectorStore): Vector store containing file documentation
        output_path (str): Path to save the final documentation
    """
    # Get all file paths from the vector store
    file_paths = vector_store.get_all_files()
    
    # Sort file paths for consistent organization
    file_paths.sort()
    
    # Group files by directory for better organization
    directories = {}
    
    for file_path in file_paths:
        doc = vector_store.get(file_path)
        if not doc:
            continue
            
        relative_path = doc.get("relative_path", file_path)
        dir_name = os.path.dirname(relative_path)
        
        if dir_name not in directories:
            directories[dir_name] = []
            
        directories[dir_name].append((file_path, doc))
    
    # Generate the final document
    with open(output_path, 'w', encoding='utf-8') as f:
        # Write header
        f.write("# Repository Documentation\n\n")
        f.write("This documentation is automatically generated and updated.\n\n")
        
        # Write table of contents
        f.write("## Table of Contents\n\n")
        
        # Sort directories for consistent organization
        sorted_dirs = sorted(directories.keys())
        
        for dir_name in sorted_dirs:
            if dir_name:
                f.write(f"- [{dir_name}](#{dir_name.replace('/', '-').replace(' ', '-').lower()})\n")
                
                # Add file links under each directory
                for _, doc in directories[dir_name]:
                    filename = doc.get("filename", "Unknown")
                    f.write(f"  - [{filename}](#{filename.replace('.', '-').lower()})\n")
            else:
                f.write("- [Root Directory](#root-directory)\n")
                
                # Add file links under root directory
                for _, doc in directories[dir_name]:
                    filename = doc.get("filename", "Unknown")
                    f.write(f"  - [{filename}](#{filename.replace('.', '-').lower()})\n")
        
        f.write("\n")
        
        # Write documentation by directory
        for dir_name in sorted_dirs:
            if dir_name:
                f.write(f"## {dir_name}\n\n")
            else:
                f.write("## Root Directory\n\n")
                
            # Write file documentation
            for file_path, doc in sorted(directories[dir_name]):
                section = generate_file_doc_section(file_path, doc)
                f.write(section)
                f.write("\n")

def update_final_doc(changed_files, vector_store, output_path):
    """
    Update only the changed sections in the final documentation.
    
    Args:
        changed_files (list): List of file paths that have changed
        vector_store (VectorStore): Vector store containing file documentation
        output_path (str): Path to the final documentation file
    """
    # Check if the final documentation exists
    if not os.path.exists(output_path):
        # If not, generate it from scratch
        generate_final_doc(vector_store, output_path)
        return
        
    # Read existing documentation
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Process each changed file
    for file_path in changed_files:
        doc = vector_store.get(file_path)
        
        if doc:
            # File was updated or added
            relative_path = doc.get("relative_path", file_path)
            
            # Check if section exists
            section_pattern = re.compile(
                r'<!-- START_DOC_SECTION: ' + re.escape(relative_path) + r' -->.*?<!-- END_DOC_SECTION: ' + re.escape(relative_path) + r' -->', 
                re.DOTALL
            )
            
            new_section = generate_file_doc_section(file_path, doc)
            
            if section_pattern.search(content):
                # Update existing section
                content = section_pattern.sub(new_section.strip(), content)
            else:
                # Add new section
                # Determine where to add the section based on directory structure
                dir_name = os.path.dirname(relative_path)
                
                if dir_name:
                    # Try to find the directory section
                    dir_pattern = re.compile(r'## ' + re.escape(dir_name) + r'\n\n')
                    dir_match = dir_pattern.search(content)
                    
                    if dir_match:
                        # Add after directory heading
                        insert_pos = dir_match.end()
                        content = content[:insert_pos] + new_section + content[insert_pos:]
                    else:
                        # Add to the end of the document
                        content += f"\n## {dir_name}\n\n{new_section}"
                else:
                    # Try to find the root directory section
                    root_pattern = re.compile(r'## Root Directory\n\n')
                    root_match = root_pattern.search(content)
                    
                    if root_match:
                        # Add after root directory heading
                        insert_pos = root_match.end()
                        content = content[:insert_pos] + new_section + content[insert_pos:]
                    else:
                        # Add to the end of the document
                        content += "\n## Root Directory\n\n" + new_section
        else:
            # File was deleted, remove its section
            # Get the relative path from the section marker in the document
            section_start_pattern = re.compile(r'<!-- START_DOC_SECTION: (.*?) -->')
            matches = section_start_pattern.finditer(content)
            
            for match in matches:
                relative_path = match.group(1)
                
                if relative_path == file_path or os.path.abspath(relative_path) == os.path.abspath(file_path):
                    # Found the section for the deleted file
                    section_pattern = re.compile(
                        r'<!-- START_DOC_SECTION: ' + re.escape(relative_path) + r' -->.*?<!-- END_DOC_SECTION: ' + re.escape(relative_path) + r' -->', 
                        re.DOTALL
                    )
                    
                    # Remove the section
                    content = section_pattern.sub('', content)
    
    # Update table of contents
    # For simplicity, regenerate the entire document to ensure the TOC is accurate
    # In a production environment, you might want to update only the TOC
    
    # Write updated content
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)