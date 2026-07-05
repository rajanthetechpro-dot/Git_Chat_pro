import os

# Application Configurations
APP_TITLE = "GitChat Pro"
APP_SUBTITLE = "The Advanced AI Code Assistant & Repository Intelligence Dashboard"

# Directory configs
CACHE_DIR = os.path.join(os.getcwd(), ".cache")
TEMP_DIR_PREFIX = "gitchat_repo_"

# Ingestion config
SUPPORTED_FILE_TYPES = [
    ".py", ".js", ".ts", ".jsx", ".tsx", 
    ".java", ".cpp", ".c", ".h", ".cs", 
    ".go", ".rs", ".rb", ".php", ".pyw",
    ".md", ".json", ".yaml", ".yml", 
    ".ini", ".conf", ".toml", ".txt",
    ".html", ".css", ".scss", ".sh", ".bat",
    ".dart", ".kt", ".swift"
]

# LLM Providers Configuration
PROVIDERS = {
    "Ollama (Local)": {
        "models": ["llama3.2", "llama3", "mistral", "phi3", "qwen2.5-coder", "codegemma"],
        "default_model": "llama3.2",
        "embeddings": ["BAAI/bge-large-en-v1.5", "BAAI/bge-small-en-v1.5", "nomic-embed-text"],
        "default_embedding": "BAAI/bge-large-en-v1.5"
    },
    "OpenAI (Cloud)": {
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        "default_model": "gpt-4o-mini",
        "embeddings": ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"],
        "default_embedding": "text-embedding-3-small"
    },
    "Groq (Cloud)": {
        "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "deepseek-r1-distill-llama-70b", "gemma2-9b-it", "mixtral-8x7b-32768"],
        "default_model": "llama-3.3-70b-versatile",
        # Groq does not host embeddings; fall back to local HuggingFace models
        "embeddings": ["BAAI/bge-large-en-v1.5", "BAAI/bge-small-en-v1.5"],
        "default_embedding": "BAAI/bge-large-en-v1.5"
    },
    "Anthropic (Cloud)": {
        "models": ["claude-3-5-sonnet-latest", "claude-3-haiku-20240307"],
        "default_model": "claude-3-5-sonnet-latest",
        # Anthropic doesn't host embeddings directly, we default to local or OpenAI embeddings
        "embeddings": ["BAAI/bge-large-en-v1.5", "text-embedding-3-small"],
        "default_embedding": "BAAI/bge-large-en-v1.5"
    }
}

# Default Prompt Templates
DEFAULT_SYSTEM_PROMPT = """You are an elite software engineering AI assistant specialized in analyzing codebases.

Repository Structure:
{tree}
---------------------

Context information from the repository is provided below:
{context_str}
---------------------

Given the codebase context and repository structure above, answer the query step by step with extreme precision. 
Rules:
1. Always reference exact files, directories, functions, or lines of code where possible.
2. If code blocks are requested or needed, write syntactically correct code using Markdown syntax highlighting.
3. If the answer is not mentioned in the context or repository structure, say: 'I don't have enough information about that aspect of the repository.' Do not invent facts.

Query: {query_str}
Answer: """
