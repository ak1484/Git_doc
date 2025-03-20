import os
from typing import Dict, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from repo_parser import get_file_content, is_text_file

def generate_file_docs(file_path: str) -> Optional[Dict]:
    """
    Generates documentation for a single file using OpenAI.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        dict: Dictionary containing documentation details or None if generation failed
    """
    # Skip non-text files
    if not is_text_file(file_path):
        print(f"Skipping non-text file: {file_path}")
        return None
        
    # Get file content
    content = get_file_content(file_path)
    if not content:
        print(f"Could not read content for: {file_path}")
        return None
        
    # Skip empty files
    if not content.strip():
        print(f"Skipping empty file: {file_path}")
        return None
    
    # Get file extension and set language
    _, ext = os.path.splitext(file_path)
    language = ext[1:] if ext else "text"
    
    # Initialize OpenAI chat model
    llm = ChatOpenAI(
        model_name="gpt-4",
        temperature=0.1
    )
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a technical documentation expert. Analyze the provided code or text file and generate comprehensive documentation for it.
        
        Your documentation should include:
        1. A brief overview of the file's purpose
        2. Key functionalities and features
        3. Any important classes/functions with their descriptions
        4. Dependencies and relationships with other components (if apparent)
        5. Usage examples (if appropriate)
        
        Format your response as a structured markdown document."""),
        ("human", "File: {file_name}\nLanguage: {language}\n\nContent:\n```{language}\n{content}\n```")
    ])

    try:
        # Generate documentation
        response = llm.invoke(prompt.format(file_name=os.path.basename(file_path), language=language, content=content))

        
        # Extract the documentation text
        documentation = response.content
        
        # Create documentation object
        doc_object = {
            "file_path": file_path,
            "relative_path": os.path.relpath(file_path),
            "documentation": documentation,
            "language": language,
            "filename": os.path.basename(file_path)
        }
        
        return doc_object
    except Exception as e:
        print(f"Error generating documentation for {file_path}: {e}")
        return None

def batch_generate_docs(file_paths, batch_size=5):
    """
    Generates documentation for multiple files in batches to optimize API usage.
    
    Args:
        file_paths (list): List of file paths
        batch_size (int): Number of files to process in each batch
        
    Returns:
        list: List of documentation objects
    """
    results = []
    
    # Process files in batches
    for i in range(0, len(file_paths), batch_size):
        batch = file_paths[i:i+batch_size]
        
        print(f"Processing batch {i//batch_size + 1}/{(len(file_paths) + batch_size - 1)//batch_size}")
        
        for file_path in batch:
            doc_object = generate_file_docs(file_path)
            if doc_object:
                results.append(doc_object)
    
    return results
