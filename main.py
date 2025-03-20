import os
import argparse
from repo_parser import get_repo_structure, get_file_metadata
from doc_generator import generate_file_docs
from vector_store import VectorStore
from updater import detect_changes, update_changed_files
from final_doc_generator import generate_final_doc, update_final_doc
from download_repo import download_github_repo

def main():
    parser = argparse.ArgumentParser(description="Dynamic Repository Documentation Generator")
    parser.add_argument("--repo_path", type=str, help="Path to the repository to document")
    parser.add_argument("--github_repo", type=str, help="GitHub repository URL to download and document")
    parser.add_argument("--output_dir", type=str, default="./output", help="Directory to store documentation output")
    parser.add_argument("--openai_api_key", type=str, required=True, help="OpenAI API key")
    parser.add_argument("--mode", type=str, choices=["initial", "update"], default="initial", 
                        help="Mode: 'initial' for first-time documentation, 'update' for incremental updates")
    args = parser.parse_args()
    
    # Set OpenAI API key
    os.environ["OPENAI_API_KEY"] = args.openai_api_key
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Determine repository path
    repo_path = args.repo_path
    if args.github_repo:
        print(f"Downloading GitHub repository: {args.github_repo}")
        repo_path = download_github_repo(args.github_repo)
        if not repo_path:
            print("Failed to download repository. Exiting.")
            return
    
    if not repo_path:
        print("No repository path provided. Use --repo_path or --github_repo")
        return
    
    # Path for storing the vector database
    vector_db_path = os.path.join(args.output_dir, "vector_store")
    
    # Path for the final markdown documentation
    final_doc_path = os.path.join(args.output_dir, "repository_documentation.md")
    
    # Initialize vector store
    vector_store = VectorStore(vector_db_path)
    
    if args.mode == "initial":
        print(f"Initializing documentation for the entire repository: {repo_path}")
        initial_documentation(repo_path, vector_store)
        
        print("Generating final documentation...")
        generate_final_doc(vector_store, final_doc_path)
        
    elif args.mode == "update":
        print("Loading existing vector store...")
        vector_store.load()
        
        print("Detecting changes in repository...")
        changed_files = detect_changes(repo_path, vector_store)
        
        if changed_files:
            print(f"Found {len(changed_files)} changed files. Updating documentation...")
            update_changed_files(changed_files, vector_store, repo_path)
            
            print("Updating final documentation...")
            update_final_doc(changed_files, vector_store, final_doc_path)
        else:
            print("No changes detected. Documentation is up to date.")
    
    print("Documentation process completed successfully!")
    print(f"Final documentation saved to: {final_doc_path}")

def initial_documentation(repo_path, vector_store):
    """Generate initial documentation for all files in the repository"""
    # Get all file paths in the repository
    file_paths = get_repo_structure(repo_path)
    
    # Generate documentation for each file and add to vector store
    for file_path in file_paths:
        print(f"Processing: {file_path}")
        
        # Get file metadata
        metadata = get_file_metadata(file_path)
        
        # Generate documentation using OpenAI
        documentation = generate_file_docs(file_path)
        
        # Add to vector store
        if documentation:
            vector_store.add(file_path, metadata, documentation)
    
    # Save the vector store
    vector_store.save()

if __name__ == "__main__":
    main()

# python main.py --repo_path "C:\Users\ankit\Downloads\Git_doc\repo" --openai_api_key "your-openai-api-key-here" --mode "initial"