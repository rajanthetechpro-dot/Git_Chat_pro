import os
import hashlib
from typing import Any, List, Optional
from llama_index.core import (
    Settings, 
    SimpleDirectoryReader, 
    VectorStoreIndex, 
    StorageContext, 
    load_index_from_storage,
    PromptTemplate
)
from llama_index.core.node_parser import MarkdownNodeParser, SentenceSplitter
from llama_index.core.schema import Document

from config import CACHE_DIR, SUPPORTED_FILE_TYPES, DEFAULT_SYSTEM_PROMPT

class IndexerService:
    @staticmethod
    def _generate_cache_key(owner: str, repo: str, provider: str, embedding_name: str) -> str:
        """Generates a unique cache directory name based on repo and model details."""
        raw_key = f"{owner}/{repo}:{provider}:{embedding_name}"
        hash_digest = hashlib.md5(raw_key.encode("utf-8")).hexdigest()
        return f"{repo}_{hash_digest}"

    @staticmethod
    def is_cached(owner: str, repo: str, provider: str, embedding_name: str) -> bool:
        """Checks if a valid cached index exists on disk."""
        cache_key = IndexerService._generate_cache_key(owner, repo, provider, embedding_name)
        persist_dir = os.path.join(CACHE_DIR, cache_key)
        # Check if vector_store.json (which LlamaIndex creates) exists
        return os.path.exists(os.path.join(persist_dir, "vector_store.json"))

    @staticmethod
    def build_or_load_index(
        local_dir: str, 
        owner: str, 
        repo: str,
        llm: Any,
        embed_model: Any,
        provider: str,
        embedding_name: str,
        force_rebuild: bool = False
    ) -> VectorStoreIndex:
        """
        Loads files from local_dir, indexes them, and caches them on disk.
        If cache exists, loads from disk directly to avoid reprocessing.
        """
        # Configure global LlamaIndex settings for this run
        Settings.llm = llm
        Settings.embed_model = embed_model

        cache_key = IndexerService._generate_cache_key(owner, repo, provider, embedding_name)
        persist_dir = os.path.join(CACHE_DIR, cache_key)

        # 1. Try to load from cache
        if not force_rebuild and IndexerService.is_cached(owner, repo, provider, embedding_name):
            try:
                storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
                index = load_index_from_storage(storage_context)
                return index
            except Exception as e:
                # Fall back to rebuilding if cache is corrupted
                pass

        # 2. Build from scratch
        # Define supported file extensions for reader
        required_exts = SUPPORTED_FILE_TYPES
        
        # Load all documents from the directory recursively
        try:
            reader = SimpleDirectoryReader(
                input_dir=local_dir,
                recursive=True,
                required_exts=required_exts,
                exclude_hidden=True
            )
            documents = reader.load_data()
        except ValueError as e:
            if "No files found" in str(e):
                # Fallback: attempt to load all files without extension constraints
                try:
                    reader = SimpleDirectoryReader(
                        input_dir=local_dir,
                        recursive=True,
                        exclude_hidden=True
                    )
                    documents = reader.load_data()
                except Exception as fallback_err:
                    raise fallback_err
            else:
                raise e
        
        # We parser with SentenceSplitter for general code structure,
        # but fallback to MarkdownNodeParser if it's primarily markdown
        node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=128)
        
        # Create vector index
        index = VectorStoreIndex.from_documents(
            documents=documents, 
            transformations=[node_parser],
            show_progress=True
        )

        # 3. Persist to cache
        os.makedirs(persist_dir, exist_ok=True)
        index.storage_context.persist(persist_dir=persist_dir)

        return index

    @staticmethod
    def get_query_engine(
        index: VectorStoreIndex, 
        tree_structure: str, 
        system_prompt: str = ""
    ) -> Any:
        """
        Creates a streaming query engine over the provided index, configuring custom prompts.
        """
        query_engine = index.as_query_engine(
            streaming=True,
            similarity_top_k=5
        )

        # Formulate customized prompt template
        prompt_tmpl = system_prompt if system_prompt else DEFAULT_SYSTEM_PROMPT
        formatted_prompt = prompt_tmpl.replace("{tree}", tree_structure)
        
        qa_prompt_tmpl = PromptTemplate(formatted_prompt)

        query_engine.update_prompts(
            {"response_synthesizer:text_qa_template": qa_prompt_tmpl}
        )

        return query_engine
