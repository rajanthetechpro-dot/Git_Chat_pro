
# 100% local RAG app to chat with GitHub!

This project leverages GitIngest to parse a GitHub repo in markdown format and the use LlamaIndex for RAG orchestration over it.


## Installation and setup

**Install Dependencies**:
   Ensure you have Python 3.9 or later installed (tested with Python 3.11.9).
   
   **Option 1: Using requirements.txt (Recommended)**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Option 2: Manual installation**
   ```bash
   pip install gitingest llama-index llama-index-llms-ollama llama-index-llms-openai llama-index-agent-openai llama-index-embeddings-huggingface streamlit pandas python-dotenv huggingface-hub
   ```

**Environment Setup**:
   For OpenAI integration, create a `.env` file in the project directory:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

**Running**:

Make sure you have Ollama Server running then you can run following command to start the streamlit application ```streamlit run app_local.py```.

---

