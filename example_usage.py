#!/usr/bin/env python3
"""
Example script demonstrating how to use the dynamic documentation generator.
"""
import os
import subprocess

def run_example():
    """Run an example of the dynamic documentation generator."""
    # Example GitHub repository to document
    example_repo = "https://github.com/django/django-contrib-comments.git"
    
    # Get OpenAI API key from environment or prompt user
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        openai_api_key = input("Please enter your OpenAI API key: ")
    
    print(f"\n1. Downloading and documenting GitHub repository: {example_repo}")
    subprocess.run([
        "python", "main.py",
        "--github_repo", example_repo,
        "--openai_api_key", openai_api_key,
        "--output_dir", "./example_output"
    ])
    
    print("\n2. Documentation generated successfully!")
    
    # Optional: Make a change to the repository to demonstrate incremental updates
    print("\n3. Making a small change to a file to demonstrate incremental updates...")
    
    # Find a Python file to modify
    repo_dir = "download_repo"
    python_files = []
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    if python_files:
        # Modify the first Python file found
        test_file = python_files[0]
        print(f"   Modifying file: {test_file}")
        
        with open(test_file, "a") as f:
            f.write("\n# This is a test comment added to demonstrate incremental updates\n")
        
        print("\n4. Running incremental update...")
        subprocess.run([
            "python", "main.py",
            "--repo_path", repo_dir,
            "--mode", "update",
            "--openai_api_key", openai_api_key,
            "--output_dir", "./example_output"
        ])
        
        print("\n5. Documentation updated successfully!")
    else:
        print("   No Python files found to modify.")
    
    print("\nExample completed. Check the ./example_output directory for results.")

if __name__ == "__main__":
    run_example()