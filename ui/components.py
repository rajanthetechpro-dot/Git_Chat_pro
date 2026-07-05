import streamlit as st
import plotly.express as px
import pandas as pd
from typing import Dict, Any, List

class UIComponents:
    @staticmethod
    def render_metric_card(label: str, value: Any, icon: str = ""):
        """Renders a premium glass-morphism style metric card."""
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="metric-label">{icon} {label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def render_sidebar_controls() -> Dict[str, Any]:
        """Renders unified repository ingestion and LLM configuration sidebar controls."""
        config = {}
        
        st.sidebar.markdown("### 📥 1. Load Repository")
        config["github_url"] = st.sidebar.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/owner/repo",
            help="Enter a valid public or private GitHub repository URL"
        )
        
        # Expandable credentials for private repos
        with st.sidebar.expander("🔑 Private Repository Credentials"):
            config["token"] = st.sidebar.text_input(
                "Personal Access Token (PAT)",
                type="password",
                placeholder="ghp_...",
                help="Supply a token to read your private repositories securely"
            )

        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🧠 2. AI Model Settings")
        
        # LLM Provider selection
        from config import PROVIDERS
        provider_options = list(PROVIDERS.keys())
        config["provider"] = st.sidebar.selectbox("LLM Provider", provider_options)

        # Model selection based on provider
        provider_info = PROVIDERS[config["provider"]]
        config["model_name"] = st.sidebar.selectbox("Model", provider_info["models"])
        
        # Embeddings selection
        config["embed_name"] = st.sidebar.selectbox("Embedding Model", provider_info["embeddings"])

        # Cloud Provider Credentials
        config["api_key"] = ""
        if "Cloud" in config["provider"]:
            with st.sidebar.expander("🔑 Provider API Keys"):
                provider_key_env = config["provider"].split(" ")[0].upper() + "_API_KEY"
                config["api_key"] = st.sidebar.text_input(
                    f"{config['provider'].split(' ')[0]} API Key",
                    type="password",
                    placeholder=f"Loaded from environment if empty...",
                    help=f"Optionally override your {provider_key_env} here"
                )

        # Additional Advanced Generation Options
        with st.sidebar.expander("⚙️ Advanced Parameters"):
            config["temperature"] = st.slider("Temperature", 0.0, 1.0, 0.1, 0.05)
            config["force_rebuild"] = st.checkbox("Force Rebuild Index", value=False, help="Re-index and ignore existing disk caches")

        st.sidebar.markdown("---")
        config["load_btn"] = st.sidebar.button("Initialize Repository & RAG Engine", type="primary", use_container_width=True)
        
        return config

    @staticmethod
    def render_analytics_dashboard(stats: Dict[str, Any]):
        """Renders repository stats, charts, file metrics, and lists of large files."""
        # Top level metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            UIComponents.render_metric_card("Total Files", f"{stats['total_files']:,}", "📁")
        with col2:
            UIComponents.render_metric_card("Total Lines of Code", f"{stats['total_lines']:,}", "📝")
        with col3:
            UIComponents.render_metric_card("Blank Lines", f"{stats['blank_lines']:,}", "📭")
        with col4:
            UIComponents.render_metric_card("Remaining TODOs", f"{len(stats['todos'])}", "⏳")

        # Visual Grid Layout for detailed charts & files
        tab1, tab2 = st.tabs(["📊 Language & Size Breakdown", "📁 Largest Files"])
        
        with tab1:
            # Language breakdown chart
            lang_data = []
            for ext, details in stats["languages"].items():
                lang_data.append({
                    "Language/Type": ext if ext != "No Extension" else "Other",
                    "Files": details["files"],
                    "Lines of Code": details["lines"]
                })
            
            if lang_data:
                df = pd.DataFrame(lang_data)
                
                chart_col, table_col = st.columns([3, 2])
                with chart_col:
                    fig = px.pie(
                        df, 
                        values="Lines of Code", 
                        names="Language/Type", 
                        hole=0.4,
                        title="Line Count Distribution",
                        color_discrete_sequence=px.colors.sequential.RdBu
                    )
                    fig.update_layout(
                        margin=dict(t=30, b=0, l=0, r=0),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font_color="#f8fafc"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                with table_col:
                    st.markdown("##### Languages Details")
                    st.dataframe(
                        df.sort_values(by="Lines of Code", ascending=False),
                        hide_index=True,
                        use_container_width=True
                    )
            else:
                st.info("No languages found to analyze.")

        with tab2:
            st.markdown("##### 🕵️ Top 10 Largest Files in Repository")
            large_df = pd.DataFrame(
                stats["large_files"], 
                columns=["File Path", "Size (Bytes)"]
            )
            large_df["Size (KB)"] = (large_df["Size (Bytes)"] / 1024).round(2)
            st.dataframe(
                large_df[["File Path", "Size (KB)"]], 
                use_container_width=True, 
                hide_index=True
            )

    @staticmethod
    def render_security_scan(stats: Dict[str, Any]):
        """Renders static security scanner alerts."""
        alerts = stats.get("security_alerts", [])
        
        st.subheader(f"🛡️ Static Code Security Scan ({len(alerts)} Alerts)")
        
        if not alerts:
            st.success("Great! No critical issues or secrets were found exposed in the repository files.")
            return

        for idx, alert in enumerate(alerts):
            severity = alert["severity"]
            badge_color = "red" if severity == "High" else "orange"
            
            with st.expander(f"🔴 [{severity}] {alert['issue']} — {alert['file']}:{alert['line']}"):
                st.markdown(f"**Location:** `{alert['file']}` (Line {alert['line']})")
                st.markdown(f"**Hazard Description:** {alert['issue']}")
                st.code(alert["content"], language="python")

    @staticmethod
    def render_todos(stats: Dict[str, Any]):
        """Renders Codebase TODOs and FIXMEs checklist."""
        todos = stats.get("todos", [])
        
        st.subheader(f"📋 Codebase Task Checklist / TODOs ({len(todos)})")
        
        if not todos:
            st.success("Nice! No outstanding TODOs or FIXMEs found in comments.")
            return

        # Add a search filter for TODOs
        search = st.text_input("Filter TODOs by text or file path", placeholder="e.g. database, setup, app.py")
        
        for idx, todo in enumerate(todos):
            if search and (search.lower() not in todo["file"].lower() and search.lower() not in todo["content"].lower()):
                continue
                
            st.markdown(
                f"- [ ] `{todo['file']}:{todo['line']}` : {todo['content'].replace('TODO', '').replace('FIXME', '').strip()}"
            )
