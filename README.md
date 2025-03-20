# Dynamic Repository Documentation Generator

A tool to automatically generate and maintain documentation for code repositories using OpenAI and FAISS vector storage.

## Features

- 📚 Generates comprehensive documentation for each file in your repository
- 🔄 Detects changes and updates only the affected documentation
- 🧠 Uses OpenAI and Langchain for intelligent documentation generation
- 🔍 Stores documentation in a FAISS vector database for efficient retrieval
- 📝 Produces a final Markdown document with all repository documentation
- 🔗 Supports downloading repositories directly from GitHub

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/dynamic-doc-generator.git
   cd dynamic-doc-generator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   ```bash
   export OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

### Generate Documentation for a Local Repository

To generate documentation for a local repository:

```bash
python main.py --repo_path /path/to/your/repository --openai_api_key your_openai_api_key
```

### Generate Documentation for a GitHub Repository

To download and generate documentation for a GitHub repository:

```bash
python main.py --github_repo https://github.com/username/repository.git --openai_api_key your_openai_api_key
```

### Update Existing Documentation

To update documentation after changes to the repository:

```bash
python main.py --repo_path /path/to/your/repository --mode update --openai_api_key your_openai_api_key
```

### Additional Options

- `--output_dir`: Directory to store documentation output (default: ./output)
- `--mode`: Mode of operation: "initial" or "update" (default: initial)

## Project Structure

```
dynamic-doc-generator/
├── main.py                    # Entry point for the application
├── repo_parser.py             # Repository traversal and file metadata extraction
├── doc_generator.py           # Documentation generation using OpenAI
├── vector_store.py            # FAISS vector storage for documentation
├── updater.py                 # Change detection and documentation updates
├── final_doc_generator.py     # Final documentation generation and updates
└── download_repo.py           # GitHub repository downloading
```

## Example Usage

### Example 1: Document a GitHub Repository

```bash
# Download and document a repository
python main.py --github_repo https://github.com/langchain-ai/langchain.git --openai_api_key your_openai_api_key
```

### Example 2: Update Documentation After Changes

```bash
# Update documentation after making changes
python main.py --repo_path download_repo --mode update --openai_api_key your_openai_api_key
```

## Output

The tool generates:

1. A FAISS vector database containing the documentation for each file
2. A comprehensive Markdown file with documentation for the entire repository

The documentation is organized by directory structure, making it easy to navigate and understand the repository.

## Notes

- The tool uses OpenAI's API, so you'll need an API key with sufficient quota
- For large repositories, the process may take some time and consume a significant number of API calls
- The tool works best with code repositories, but can also document text files