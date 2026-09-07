# GitHub RAG

<p align="center">
  <strong>AI-Powered Retrieval-Augmented Generation Application</strong>
</p>

<p align="center">
  Retrieve relevant information from documents and generate accurate, context-aware AI responses.
</p>

---

## Overview

GitHub RAG is a Retrieval-Augmented Generation (RAG) application that combines document retrieval with Large Language Models to provide accurate and context-aware responses.

Instead of relying solely on the knowledge stored within the language model, the application retrieves relevant information from external documents using semantic search and provides that information as context to the AI model.

This approach helps improve response accuracy and reduce hallucinations.

## Features

- **🔍 Semantic Search** — Retrieves the most relevant document chunks using vector embeddings.
- **🤖 AI-Powered Responses** — Generates responses based on retrieved contextual information.
- **📚 Document-Based Q&A** — Allows users to ask questions based on uploaded documents.
- **🎯 Context-Aware Answers** — Grounds responses in external knowledge instead of relying solely on the language model.
- **⚡ Fast Retrieval** — Uses vector search to efficiently find relevant information.
- **💬 Interactive Interface** — Provides an easy-to-use interface for interacting with the RAG system.

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Framework | Streamlit |
| AI / LLM | OpenAI / Ollama |
| RAG Framework | LangChain, LlamaIndex |
| Search | Vector Search |
| Embeddings | Vector Embeddings |
| Environment | Python-dotenv |

## Getting Started

### Prerequisites

- Python 3.9 or later
- OpenAI API key (if using OpenAI)
- Ollama (if using local LLMs)

### Installation

#### Option 1: Using `requirements.txt` (Recommended)

```bash
pip install -r requirements.txt

### Option 2:
pip install streamlit langchain llama-index \
llama-index-llms-ollama llama-index-llms-openai \
llama-index-agent-openai python-dotenv
