import os
import gc
import shutil
import uuid
import streamlit as st
from dotenv import load_dotenv

# Load environmental variables
load_dotenv()

from config import APP_TITLE, APP_SUBTITLE
from services.git_service import GitService
from services.llm_service import LLMService
from services.indexer import IndexerService
from services.analyzer import CodebaseAnalyzer
from ui.components import UIComponents

# Streamlit Page Configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1. Inject Premium Stylesheet
script_dir = os.path.dirname(os.path.abspath(__file__))
css_path = os.path.join(script_dir, "ui", "styles.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize Session State Variables
if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "repo_loaded" not in st.session_state:
    st.session_state.repo_loaded = False
if "query_engine" not in st.session_state:
    st.session_state.query_engine = None
if "repo_tree" not in st.session_state:
    st.session_state.repo_tree = ""
if "repo_stats" not in st.session_state:
    st.session_state.repo_stats = {}
if "repo_name" not in st.session_state:
    st.session_state.repo_name = ""
if "repo_owner" not in st.session_state:
    st.session_state.repo_owner = ""
if "local_dir" not in st.session_state:
    st.session_state.local_dir = ""

def reset_chat_session():
    st.session_state.messages = []
    gc.collect()

# UI Header
st.title(f"🚀 {APP_TITLE}")
st.caption(APP_SUBTITLE)
st.markdown("---")

# Render Sidebar Options
ui_config = UIComponents.render_sidebar_controls()

# Check Ingestion Button Click
if ui_config["load_btn"]:
    if not ui_config["github_url"]:
        st.sidebar.error("Please enter a valid GitHub repository URL.")
    else:
        try:
            with st.status("🔄 Ingesting and building RAG index...", expanded=True) as status:
                # 1. Clear previous session messages on new repo load
                reset_chat_session()
                
                # 2. Validate URL and extract repo info
                if not GitService.validate_url(ui_config["github_url"]):
                    raise ValueError("Please provide a valid GitHub repository URL (e.g., https://github.com/owner/repo).")
                
                owner, repo_name = GitService.extract_repo_info(ui_config["github_url"])
                st.session_state.repo_name = repo_name
                st.session_state.repo_owner = owner
                
                # 3. Download/clone and run GitIngest
                status.update(label="🤖 Cloning repository files...", state="running")
                temp_clone_dir = os.path.join(
                    os.getcwd(), 
                    "temp_repos", 
                    f"{owner}_{repo_name}"
                )
                
                summary, tree, content, local_path = GitService.clone_and_ingest(
                    url=ui_config["github_url"],
                    token=ui_config["token"],
                    temp_dir=temp_clone_dir
                )
                
                st.session_state.repo_tree = tree
                st.session_state.local_dir = local_path
                
                # 4. Perform Code Static Analysis
                status.update(label="📊 Running static analysis scan...", state="running")
                analysis_stats = CodebaseAnalyzer.analyze_repository(local_path)
                st.session_state.repo_stats = analysis_stats
                
                # 5. Initialize LLM & Embeddings Model
                status.update(label="🧠 Booting LLM & Embedding models...", state="running")
                llm = LLMService.get_llm(
                    provider=ui_config["provider"],
                    model_name=ui_config["model_name"],
                    api_key=ui_config["api_key"],
                    temperature=ui_config["temperature"]
                )
                embed_model = LLMService.get_embedding(
                    provider=ui_config["provider"],
                    embed_name=ui_config["embed_name"],
                    api_key=ui_config["api_key"]
                )
                
                # 6. Index files using LlamaIndex
                status.update(label="⚡ Constructing vector embeddings & indexing codebase...", state="running")
                index = IndexerService.build_or_load_index(
                    local_dir=local_path,
                    owner=owner,
                    repo=repo_name,
                    llm=llm,
                    embed_model=embed_model,
                    provider=ui_config["provider"],
                    embedding_name=ui_config["embed_name"],
                    force_rebuild=ui_config["force_rebuild"]
                )
                
                # 7. Create custom query engine
                status.update(label="🚀 Wrapping query engine interface...", state="running")
                query_engine = IndexerService.get_query_engine(
                    index=index,
                    tree_structure=tree
                )
                
                st.session_state.query_engine = query_engine
                st.session_state.repo_loaded = True
                
                status.update(label="✅ Ready! Codebase intelligence loaded successfully.", state="complete")
                st.toast("Success! Application is ready.")
                
        except PermissionError as pe:
            st.sidebar.error(f"Access Denied: {str(pe)}")
        except Exception as e:
            st.sidebar.error(f"Initialization Failed: {str(e)}")
            # Cleanup on failure
            if st.session_state.local_dir and os.path.exists(st.session_state.local_dir):
                shutil.rmtree(st.session_state.local_dir)

# Main Application Pages (Rendered when repository is successfully loaded)
if st.session_state.repo_loaded:
    # Render Application Tabs
    tab_chat, tab_insights, tab_backlog, tab_security, tab_explorer = st.tabs([
        "💬 Codebase Chat",
        "📊 Codebase Insights",
        "📋 Project Backlog",
        "🛡️ Security Scanner",
        "🌳 Code File Explorer"
    ])
    
    # ------------------
    # TAB: Codebase Chat
    # ------------------
    with tab_chat:
        col_header, col_clear = st.columns([6, 1])
        with col_header:
            st.markdown(f"#### Ask questions about **{st.session_state.repo_owner}/{st.session_state.repo_name}**")
        with col_clear:
            st.button("Clear Chat ↺", on_click=reset_chat_session, use_container_width=True)
            
        # Display chat conversation messages
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        # Handle chat query submission
        if prompt := st.chat_input("Explain how the main routine is implemented..."):
            # Add user input to conversation state
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
                
            # Process response using the active RAG engine
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_resp = ""
                
                try:
                    response = st.session_state.query_engine.query(prompt)
                    
                    # Handle streaming generator response
                    if hasattr(response, "response_gen"):
                        for chunk in response.response_gen:
                            if isinstance(chunk, str):
                                full_resp += chunk
                                message_placeholder.markdown(full_resp + "▌")
                    else:
                        full_resp = str(response)
                    
                    message_placeholder.markdown(full_resp)
                    
                    # Store response in session state
                    st.session_state.messages.append({"role": "assistant", "content": full_resp})
                except Exception as ex:
                    st.error(f"Failed to generate answer: {str(ex)}")
                    message_placeholder.markdown("⚠️ I ran into an error retrieving answers for your query.")

    # ------------------
    # TAB: Codebase Insights
    # ------------------
    with tab_insights:
        st.markdown(f"#### 📊 Code Repository Metrics & Language Breakdown")
        UIComponents.render_analytics_dashboard(st.session_state.repo_stats)

    # ------------------
    # TAB: Project Backlog
    # ------------------
    with tab_backlog:
        UIComponents.render_todos(st.session_state.repo_stats)

    # ------------------
    # TAB: Security Scanner
    # ------------------
    with tab_security:
        UIComponents.render_security_scan(st.session_state.repo_stats)

    # ------------------
    # TAB: Code File Explorer
    # ------------------
    with tab_explorer:
        st.markdown("#### 🌳 Repository Directory Structure Tree")
        st.text_area(
            label="Hierarchy Visualizer",
            value=st.session_state.repo_tree,
            height=500,
            disabled=True
        )

else:
    # Landing / Onboarding View
    st.info("👈 Use the left sidebar to add a GitHub repository and initialize the AI codebase models.")
    
    with st.container(border=True):
        st.markdown("#### 💡 Welcome to GitChat Pro!")
        st.markdown(
            """
            This platform acts as an interactive code intelligence scanner. Simply supply a repository URL on the left panel to:
            
            1. **💬 Chat directly with your codebase** to explain architectures, refactor functions, or trace dependencies.
            2. **📊 Inspect key metrics** like Language breakdown (LOC percentages) and file-size anomalies.
            3. **📋 Automatically extract TODO tasks** to maintain a project backlog.
            4. **🛡️ Scan for security vulnerabilities** like leaked secrets, API keys, or unsafe runtime calls.
            
            Supported providers include: **Ollama** (completely local LLMs & Embeddings), **OpenAI**, **Gemini**, and **Anthropic**.
            """
        )