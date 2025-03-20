import os
import pickle
import json
from typing import Dict, List, Optional, Any
import faiss
import numpy as np
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.vectorstores import FAISS
# from langchain_community.chat_models import ChatOpenAI
# from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI


class VectorStore:
    def __init__(self, store_dir: str):
        """
        Initialize the vector store for documentation.
        
        Args:
            store_dir (str): Directory to store the vector database and metadata
        """
        self.store_dir = store_dir
        self.metadata_path = os.path.join(store_dir, "metadata.json")
        self.faiss_index_path = os.path.join(store_dir, "faiss_index")
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings()
        
        # Initialize or load vector store
        self.file_metadata = {}  # Maps file paths to metadata
        self.file_docs = {}  # Maps file paths to documentation
        
        # Initialize FAISS vector store
        self.vector_store = None
        
        # Create directory if it doesn't exist
        os.makedirs(store_dir, exist_ok=True)
        
        # Try to load existing data
        self.load()
    
    def add(self, file_path: str, metadata: Dict, documentation: Dict) -> None:
        """
        Add a file's documentation to the vector store.
        
        Args:
            file_path (str): Path to the file
            metadata (dict): File metadata
            documentation (dict): Documentation object
        """
        # Store metadata and documentation
        self.file_metadata[file_path] = metadata
        self.file_docs[file_path] = documentation
        
        # Create FAISS entry
        self._update_faiss_index()
    
    def update(self, file_path: str, metadata: Dict, documentation: Dict) -> None:
        """
        Update existing documentation in the vector store.
        
        Args:
            file_path (str): Path to the file
            metadata (dict): Updated file metadata
            documentation (dict): Updated documentation object
        """
        # Update metadata and documentation
        self.file_metadata[file_path] = metadata
        self.file_docs[file_path] = documentation
        
        # Update FAISS index
        self._update_faiss_index()
    
    def get(self, file_path: str) -> Optional[Dict]:
        """
        Retrieve documentation for a file.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            dict: Documentation object or None if not found
        """
        return self.file_docs.get(file_path)
    
    def get_metadata(self, file_path: str) -> Optional[Dict]:
        """
        Retrieve metadata for a file.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            dict: Metadata or None if not found
        """
        return self.file_metadata.get(file_path)
    
    def get_all_files(self) -> List[str]:
        """
        Get all file paths in the vector store.
        
        Returns:
            list: List of file paths
        """
        return list(self.file_docs.keys())
    
    def remove(self, file_path: str) -> None:
        """
        Remove a file from the vector store.
        
        Args:
            file_path (str): Path to the file
        """
        if file_path in self.file_metadata:
            del self.file_metadata[file_path]
        
        if file_path in self.file_docs:
            del self.file_docs[file_path]
            
        # Update FAISS index
        self._update_faiss_index()
    
    def save(self) -> None:
        """Save the vector store to disk"""
        # Save metadata and docs mapping
        with open(self.metadata_path, 'w') as f:
            data = {
                "file_metadata": self.file_metadata,
                "file_docs": self.file_docs
            }
            json.dump(data, f, indent=2)
        
        # Save FAISS index if it exists
        if self.vector_store:
            self.vector_store.save_local(self.faiss_index_path)
    
    def load(self) -> bool:
        """
        Load the vector store from disk.
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        # Check if files exist
        if not os.path.exists(self.metadata_path):
            return False
        
        try:
            # Load metadata and docs mapping
            with open(self.metadata_path, 'r') as f:
                data = json.load(f)
                self.file_metadata = data.get("file_metadata", {})
                self.file_docs = data.get("file_docs", {})
            
            # Load FAISS index if it exists
            if os.path.exists(self.faiss_index_path):
                self.vector_store = FAISS.load_local(self.faiss_index_path, self.embeddings)
            else:
                self._update_faiss_index()
                
            return True
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return False
    
    def _update_faiss_index(self) -> None:
        """Update or create the FAISS index with current documentation"""
        if not self.file_docs:
            return
            
        # Prepare texts and metadatas for FAISS
        texts = []
        metadatas = []
        
        for file_path, doc in self.file_docs.items():
            text = doc["documentation"]
            metadata = {
                "file_path": file_path,
                "relative_path": doc["relative_path"],
                "language": doc.get("language", "unknown"),
                "filename": doc["filename"]
            }
            
            texts.append(text)
            metadatas.append(metadata)
        
        # Create or recreate the FAISS index
        self.vector_store = FAISS.from_texts(texts, self.embeddings, metadatas=metadatas)
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search the vector store for documentation related to the query.
        
        Args:
            query (str): Search query
            k (int): Number of results to return
            
        Returns:
            list: List of documentation objects with relevance scores
        """
        if not self.vector_store:
            return []
            
        results = self.vector_store.similarity_search_with_score(query, k=k)
        
        # Format results
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "file_path": doc.metadata["file_path"],
                "relative_path": doc.metadata["relative_path"],
                "score": float(score),
                "documentation": doc.page_content
            })
            
        return formatted_results