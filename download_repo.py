import os
import argparse
import subprocess
import shutil

def download_github_repo(repo_url, target_dir="download_repo"):
    """
    Downloads a GitHub repository to the specified directory.
    
    Args:
        repo_url (str): URL of the GitHub repository to download
        target_dir (str): Directory to download the repository to
        
    Returns:
        str: Path to the downloaded repository
    """
    print(f"Downloading repository from {repo_url}...")
    
    # Create target directory if it doesn't exist
    if os.path.exists(target_dir):
        print(f"Target directory {target_dir} already exists. Removing...")
        shutil.rmtree(target_dir)
    
    # Clone the repository
    try:
        subprocess.run(["git", "clone", repo_url, target_dir], check=True)
        print(f"Repository downloaded successfully to {target_dir}")
        return target_dir
    except subprocess.CalledProcessError as e:
        print(f"Error downloading repository: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a GitHub repository")
    parser.add_argument("--repo_url", type=str, required=True, help="URL of the GitHub repository to download")
    parser.add_argument("--target_dir", type=str, default="download_repo", help="Directory to download the repository to")
    
    args = parser.parse_args()
    download_github_repo(args.repo_url, args.target_dir)


# python download_repo.py --repo_url "https://github.com/ak1484/go-server" --target_dir "C:\Users\ankit\Downloads\Git_doc\repo"