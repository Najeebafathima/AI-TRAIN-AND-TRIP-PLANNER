import base64
import os
import streamlit as st
import agent
from agent import chat
from images import get_place_images

st.set_page_config(page_title="AI Train & Trip Planner",
                   page_icon="🚆", layout="centered")


def background_css():
    """Use background.jpg if present, otherwise a colourful gradient."""
    if os.path.exists("background.jpg"):
        with open("background.jpg", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return (
            "linear-gradient(rgba(10,20,50,0.45), rgba(10,20,50,0.45)), "
            f'url("data:image/jpeg;base64,{b64}")'
        )
    return "linear-gradient(135deg, #1e3c72 0%, #2a5298 40%, #ff6a00 100%)"


st.markdown(
    f"""
    <style>
    .stApp {{
        background: {background_css()};
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    header[data-testid="stHeader"] {{ background: transparent; }}

    /* Title banner */
    .hero {{
        text-align: center;
        padding: 22px 10px;
        margin-bottom: 18px;
        border-radius: 20px;
        background: linear-gradient(90deg, #ff512f, #f09819, #dd2476);
        box-shadow: 0 8px 24px rgba(0,0,0,0.35);
    }}
    .hero h1 {{ color: white; margin: 0; font-size: 2.2rem; }}
    .hero p {{ color: #fff3e0; margin: 6px 0 0 0; font-size: 1.05rem; }}

    /* Chat bubbles */
    [data-testid="stChatMessage"] {{
        background: rgba(255,255,255,0.88);
        border-radius: 16px;
        padding: 12px 16px;
        margin-bottom: 10px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.25);
    }}
    [data-testid="stChatMessage"] * {{ color: #1a1a2e; }}

    /* Chat input */
    [data-testid="stBottom"] > div {{ background: transparent; }}
    [data-testid="stChatInput"] {{
        border-radius: 25px;
        border: 2px solid #f09819;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #141e30, #243b55);
    }}
    section[data-testid="stSidebar"] * {{ color: white; }}
    section[data-testid="stSidebar"] .stButton button {{
        width: 100%;
        border-radius: 12px;
        border: none;
        background: linear-gradient(90deg, #ff512f, #dd2476);
        color: white;
        font-weight: 600;
    }}
    section[data-testid="stSidebar"] .stButton button:hover {{
        filter: brightness(1.15);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>🚆 AI Train & Trip Planner ✈️</h1>
        <p>Tell me where you want to go. Any city, state or country.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "msgs" not in st.session_state:
    st.session_state.msgs = []
if "pending" not in st.session_state:
    st.session_state.pending = None
    if "gallery" not in st.session_state:
       st.session_state.gallery = {}


def show_images(urls):
    if urls:
        cols = st.columns(len(urls))
        for col, url in zip(cols, urls):
            col.image(url, use_container_width=True)

# Sidebar with quick-start buttons
with st.sidebar:
    st.header("🌍 Try these")
    examples = [
        "Plan 3 days in Goa",
        "Trains from Hyderabad to Mumbai",
        "Kerala trip for 5 days",
        "Best time to visit Manali",
        "Plan a week in Japan",
    ]
    for ex in examples:
        if st.button(ex):
            st.session_state.pending = ex
    st.markdown("---")
    if st.button("🗑️ Clear chat"):
        st.session_state.msgs = []
        st.rerun()
    st.caption("Always verify train timings on IRCTC / NTES.")

# Show chat history
for i, m in enumerate(st.session_state.msgs):
    if isinstance(m, dict) and m["role"] in ("user", "assistant"):
        avatar = "🧳" if m["role"] == "user" else "🤖"
        with st.chat_message(m["role"], avatar=avatar):
            if m["role"] == "assistant":
                show_images(st.session_state.gallery.get(i, []))
            st.write(m["content"])
# Get input (typed or from a sidebar button)
prompt = st.chat_input("Where do you want to go?")
if st.session_state.pending:
    prompt = st.session_state.pending
    st.session_state.pending = None

if prompt:
    st.chat_message("user", avatar="🧳").write(prompt)
    st.session_state.msgs.append({"role": "user", "content": prompt})
    with st.spinner("Planning your trip... ✨"):
        reply = chat(st.session_state.msgs)
        urls = get_place_images(agent.LAST_PLACE)
    st.session_state.gallery[len(st.session_state.msgs) - 1] = urls
    with st.chat_message("assistant", avatar="🤖"):
        show_images(urls)
        st.write(reply)