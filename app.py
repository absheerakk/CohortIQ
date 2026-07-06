import os
import streamlit as st
import google.generativeai as genai
from core import (
    get_embed_model,
    get_chroma_client,
    index_documents,
    query_pipeline,
    SYSTEM_PROMPT
)

# 1. Page Configuration
st.set_page_config(
    page_title="Cohort IQ",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject CSS styles from style.css using absolute paths
script_dir = os.path.dirname(os.path.abspath(__file__))
style_css_path = os.path.join(script_dir, "style.css")

if os.path.exists(style_css_path):
    with open(style_css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.warning("⚠️ stylesheet not found. Please verify style.css is in the app directory.")

# Initialize session state flags
if 'busy' not in st.session_state:
    st.session_state.busy = False
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""

# 3. Sidebar UI
with st.sidebar:
    # Sidebar Header with custom Brain SVG
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 2rem;'>
            <div style='color: #A855F7; display: flex; align-items: center; justify-content: center;'>
                <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-brain-icon lucide-brain"><path d="M12 18V5"/><path d="M15 13a4.17 4.17 0 0 1-3-4 4.17 4.17 0 0 1-3 4"/><path d="M17.598 6.5A3 3 0 1 0 12 5a3 3 0 1 0-5.598 1.5"/><path d="M17.997 5.125a4 4 0 0 1 2.526 5.77"/><path d="M18 18a4 4 0 0 0 2-7.464"/><path d="M19.967 17.483A4 4 0 1 1 12 18a4 4 0 1 1-7.967-.517"/><path d="M6 18a4 4 0 0 1-2-7.464"/><path d="M6.003 5.125a4 4 0 0 0-2.526 5.77"/></svg>
            </div>
            <div>
                <div style='font-weight: 800; font-size: 1.4rem; color: #FFFFFF; line-height: 1.1;'>Cohort IQ</div>
                <div style='font-size: 0.75rem; color: #6E7893;'>Intelligent Course Companion</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Navigation Items
    st.markdown("""
        <a href='#' class='nav-item active'>🏠 &nbsp; Home</a>
        <a href='#' class='nav-item'>💬 &nbsp; Ask Question</a>
        <a href='#' class='nav-item'>📚 &nbsp; Browse Sources</a>
        <a href='#' class='nav-item'>📈 &nbsp; Analytics</a>
        <a href='#' class='nav-item'>⚙️ &nbsp; Settings</a>
    """, unsafe_allow_html=True)
    
    # Load DB status details
    try:
        client = get_chroma_client()
        collection = client.get_or_create_collection("cohort_iq_lessons")
        chunk_count = collection.count()
        db_active = True
    except Exception:
        db_active = False
        chunk_count = 0
        
    db_empty = (chunk_count == 0)

    # Database Status Card
    if db_active:
        st.markdown(f"""
            <div class='sidebar-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='font-size: 0.85rem; font-weight: 600; color: #A7B1C2;'>Database Status</span>
                    <span class='status-badge' style='background: {"rgba(34, 197, 94, 0.15)" if not db_empty else "rgba(245, 158, 11, 0.15)"}; color: {"#22C55E" if not db_empty else "#F59E0B"};'>
                        {"Active" if not db_empty else "Empty"}
                    </span>
                </div>
                <p style='font-size: 0.75rem; color: #6E7893; margin-top: 8px; margin-bottom: 0px;'>
                    {"Your coursework database is ready to assist you." if not db_empty else "Ready but needs coursework files loaded."}
                </p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class='sidebar-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='font-size: 0.85rem; font-weight: 600; color: #A7B1C2;'>Database Status</span>
                    <span class='status-badge' style='background: rgba(239, 68, 68, 0.15); color: #EF4444;'>Offline</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    # Chunk Count Card
    st.markdown(f"""
        <div class='sidebar-card'>
            <span style='font-size: 0.85rem; font-weight: 600; color: #A7B1C2;'>📄 Indexed Coursework Chunks</span>
            <div class='giant-metric'>{chunk_count}</div>
            <p style='font-size: 0.75rem; color: #6E7893; margin-bottom: 0px;'>
                Spread across multiple coursework files.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    
    # Wipe Database Button
    st.markdown("<div class='wipe-btn'>", unsafe_allow_html=True)
    if st.button("🗑️ Wipe & Re-index Database", disabled=st.session_state.busy, use_container_width=True):
        st.session_state.busy = True
        with st.spinner("Deleting local database cache..."):
            try:
                client.delete_collection("cohort_iq_lessons")
                if os.path.exists("chroma_db"):
                    import shutil
                    shutil.rmtree("chroma_db")
                st.success("Database wiped successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to reset database: {e}")
            finally:
                st.session_state.busy = False
    st.markdown("</div>", unsafe_allow_html=True)

# 4. Main Page Header with Gradient Brain Logo SVG
st.markdown("""
    <div class='main-title'>
        <svg xmlns="http://www.w3.org/2000/svg" width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="url(#logo-grad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-brain-icon lucide-brain">
            <defs>
                <linearGradient id="logo-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#A855F7"/>
                    <stop offset="100%" stop-color="#3B82F6"/>
                </linearGradient>
            </defs>
            <path d="M12 18V5"/>
            <path d="M15 13a4.17 4.17 0 0 1-3-4 4.17 4.17 0 0 1-3 4"/>
            <path d="M17.598 6.5A3 3 0 1 0 12 5a3 3 0 1 0-5.598 1.5"/>
            <path d="M17.997 5.125a4 4 0 0 1 2.526 5.77"/>
            <path d="M18 18a4 4 0 0 0 2-7.464"/>
            <path d="M19.967 17.483A4 4 0 1 1 12 18a4 4 0 1 1-7.967-.517"/>
            <path d="M6 18a4 4 0 0 1-2-7.464"/>
            <path d="M6.003 5.125a4 4 0 0 0-2.526 5.77"/>
        </svg>
        <span>Cohort IQ</span>
    </div>
""", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>✦ Your Intelligent AI Coursework Companion & Study Sage ✦</div>", unsafe_allow_html=True)

# 5. Features Grid
col_f1, col_f2, col_f3, col_f4 = st.columns(4)

with col_f1:
    st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon-container' style='background-color: rgba(59, 130, 246, 0.15); color: #3B82F6;'>🔍</div>
            <h4 style='margin: 5px 0px; color: #FFFFFF;'>Smart Search</h4>
            <p style='font-size: 0.8rem; color: #A7B1C2; margin-bottom: 0px;'>AI-powered semantic search across your coursework.</p>
        </div>
    """, unsafe_allow_html=True)

with col_f2:
    st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon-container' style='background-color: rgba(168, 85, 247, 0.15); color: #A855F7;'>📄</div>
            <h4 style='margin: 5px 0px; color: #FFFFFF;'>Source Citations</h4>
            <p style='font-size: 0.8rem; color: #A7B1C2; margin-bottom: 0px;'>Get answers with exact file references.</p>
        </div>
    """, unsafe_allow_html=True)

with col_f3:
    st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon-container' style='background-color: rgba(20, 184, 166, 0.15); color: #14B8A6;'>
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-brain-icon lucide-brain"><path d="M12 18V5"/><path d="M15 13a4.17 4.17 0 0 1-3-4 4.17 4.17 0 0 1-3 4"/><path d="M17.598 6.5A3 3 0 1 0 12 5a3 3 0 1 0-5.598 1.5"/><path d="M17.997 5.125a4 4 0 0 1 2.526 5.77"/><path d="M18 18a4 4 0 0 0 2-7.464"/><path d="M19.967 17.483A4 4 0 1 1 12 18a4 4 0 1 1-7.967-.517"/><path d="M6 18a4 4 0 0 1-2-7.464"/><path d="M6.003 5.125a4 4 0 0 0-2.526 5.77"/></svg>
            </div>
            <h4 style='margin: 5px 0px; color: #FFFFFF;'>AI-Powered</h4>
            <p style='font-size: 0.8rem; color: #A7B1C2; margin-bottom: 0px;'>Advanced AI understands your course material.</p>
        </div>
    """, unsafe_allow_html=True)

with col_f4:
    st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon-container' style='background-color: rgba(245, 158, 11, 0.15); color: #F59E0B;'>⚡</div>
            <h4 style='margin: 5px 0px; color: #FFFFFF;'>Fast & Accurate</h4>
            <p style='font-size: 0.8rem; color: #A7B1C2; margin-bottom: 0px;'>Instant answers to save you hours of studying.</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 6. Load Models
@st.cache_resource
def load_resources():
    with st.spinner("🔄 Booting up semantic embedding models..."):
        embed_model = get_embed_model()
    with st.spinner("📚 Reading and indexing coursework lessons..."):
        collection = index_documents()
    with st.spinner("⚡ Initializing generative intelligence..."):
        llm = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
    return embed_model, collection, llm

# Load models
embed_model, collection, llm = load_resources()

# 7. Ask Question Section Card (Using native st.container with border)
with st.container(border=True):
    st.markdown("<div style='font-weight: 600; font-size: 1.1rem; color: #FFFFFF; margin-bottom: 15px;'>Ask a question about your AI Engineering coursework:</div>", unsafe_allow_html=True)

    col_in, col_btn = st.columns([4, 1])

    with col_in:
        # Edge Case: Disable input field if no data loaded yet (db_empty) or busy
        placeholder_text = "Type your question here..." if not db_empty else "Database is empty. Please add markdown coursework files to the data/ folder..."
        question = st.text_input(
            "Query Input",
            placeholder=placeholder_text,
            disabled=db_empty or st.session_state.busy,
            label_visibility="collapsed"
        )

    with col_btn:
        # Edge Case: Disable button if no data loaded yet (db_empty) or busy
        ask_button = st.button(
            "🚀 Ask Cohort IQ",
            disabled=db_empty or st.session_state.busy,
            use_container_width=True
        )

    # Edge Case: Very Long Input - Warn user if text is excessively long (over 1000 characters)
    if question and len(question.strip()) > 1000:
        st.warning("⚠️ Warning: Your question is very long (over 1000 characters). You can still submit, but matching performance or token limits may be affected.")

    st.markdown("<div style='font-size: 0.8rem; color: #6E7893; margin-top: 10px;'>💡 Try: <i>\"What is prompt injection?\"</i> or <i>\"Compare Day 5 and Day 10\"</i></div>", unsafe_allow_html=True)

# Define holders for answers and sources
answer_out = ""
sources_out = []
has_run = False
error_occurred = False

# Trigger processing
if ask_button or (question and st.session_state.last_query != question):
    st.session_state.last_query = question
    
    # Edge Case: Empty Input
    if not question.strip():
        st.info("ℹ️ Please enter a question.")
    elif db_empty:
        st.warning("⚠️ No documents indexed yet. Please add markdown files into the `data/` folder.")
    else:
        st.session_state.busy = True
        try:
            with st.spinner("🧠 Synthesizing coursework response..."):
                answer_out, sources_out = query_pipeline(question.strip(), collection, embed_model, llm)
                has_run = True
        except Exception as e:
            error_occurred = True
            err_str = str(e).lower()
            if any(term in err_str for term in ["api key", "api_key", "apikey", "invalid key", "invalid credentials"]):
                st.error("❌ Couldn't reach the AI service. Check your API key and try again.")
            elif any(term in err_str for term in ["connection", "dns", "network", "offline", "failed to establish"]):
                st.error("❌ Couldn't reach the AI service. Check your connection and try again.")
            else:
                st.error("Something unexpected went wrong. Please try a different question.")
                st.caption(f"Technical detail: {e}")
        finally:
            st.session_state.busy = False

# 8. AI Answer Section Card (Using native st.container with border)
with st.container(border=True):
    st.markdown("<div style='font-weight: 600; font-size: 1.1rem; color: #FFFFFF; margin-bottom: 15px;'>🔮 AI Answer</div>", unsafe_allow_html=True)

    col_ans_text, col_ans_img = st.columns([3, 1])

    with col_ans_text:
        if has_run:
            st.markdown(f"<div class='answer-text'>{answer_out}</div>", unsafe_allow_html=True)
        elif error_occurred:
            st.markdown("<div class='answer-text' style='color: #EF4444;'>An error occurred. Please view details above.</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style='color: #6E7893;'>
                    <p>Your answer will appear here with detailed explanations and source citations.</p>
                    <p>Cohort IQ will analyze your coursework and provide accurate, referenced answers.</p>
                </div>
            """, unsafe_allow_html=True)

    with col_ans_img:
        img_path = os.path.join(script_dir, "grad_cap_book.jpg")
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
        else:
            st.markdown("<div style='font-size: 5rem; text-align: center;'>🎓</div>", unsafe_allow_html=True)

# 9. Source References Section Card (Using native st.container with border)
with st.container(border=True):
    st.markdown("<div style='font-weight: 600; font-size: 1.1rem; color: #FFFFFF; margin-bottom: 15px;'>📚 Source References</div>", unsafe_allow_html=True)

    # Edge Case: Hide source cards if the pipeline returned "no good answer" (empty sources)
    if has_run and sources_out:
        unique_days = sorted(list(set(s["day"] for s in sources_out)))
        cols = st.columns(max(len(unique_days), 4))
        for idx, day in enumerate(unique_days):
            with cols[idx]:
                st.markdown(f"<div class='citation-card' style='border-left: 3px solid #7C3AED; margin-bottom: 0px;'>🎓 &nbsp;<b>{day}</b></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='color: #6E7893;'>Sources and references from your coursework will be listed here.</div>", unsafe_allow_html=True)

# 10. Footer
st.markdown("""
    <div style='text-align: center; color: #6E7893; font-size: 0.8rem; margin-top: 3rem;'>
        💖 Built for learners, by learners • Powered by RAG & Generative AI
    </div>
""", unsafe_allow_html=True)