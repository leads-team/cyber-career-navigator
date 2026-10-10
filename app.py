import streamlit as st
from rag_engine import CyberCareerRAG
from career_advisor import recommend_paths, build_roadmap

st.set_page_config(page_title="Cyber Career Navigator AI", page_icon="🧭", layout="wide")
st.title("🧭 Cyber Career Navigator AI")
st.caption("Explore cybersecurity careers with answers grounded in a curated knowledge base.")

@st.cache_resource
def load_rag():
    return CyberCareerRAG()

rag = load_rag()

with st.sidebar:
    st.header("🎯 Career discovery")
    st.write("Tell us a little about yourself to get a starting point—not a definitive career decision.")
    level = st.selectbox("Current stage", ["Beginner", "1st–2nd year student", "3rd–4th year student", "Graduate / career changer"])
    programming = st.select_slider("Programming comfort", options=["New", "Basic", "Intermediate", "Strong"], value="Basic")
    networking = st.select_slider("Networking comfort", options=["New", "Basic", "Intermediate", "Strong"], value="Basic")
    interests = st.multiselect("What sounds interesting?", [
        "Investigating alerts and incidents", "Ethical hands-on testing",
        "Investigating digital evidence", "Cloud and infrastructure",
        "Building secure software", "Automating tasks with Python"
    ])
    work_style = st.selectbox("Preferred work style", [
        "Not sure yet", "Investigative and analytical", "Hands-on testing",
        "Programming and building", "Infrastructure and configuration"
    ])
    if st.button("Suggest career paths", type="primary", use_container_width=True):
        st.session_state["recommendations"] = recommend_paths(interests, programming, networking, work_style)
        st.session_state["profile"] = {"level": level, "programming": programming, "networking": networking}

tab_chat, tab_compare, tab_roadmap, tab_about = st.tabs(["💬 Ask the knowledge agent", "⚖️ Compare careers", "🗺️ Build a roadmap", "ℹ️ About"])

with tab_chat:
    st.subheader("Ask a cybersecurity career question")
    st.write("Examples: *What does a SOC analyst do?* · *Compare application security and penetration testing.*")
    question = st.text_input("Your question", key="question")
    if st.button("Ask", type="primary", key="ask_btn") and question.strip():
        with st.spinner("Searching the career knowledge base…"):
            result = rag.answer(question)
        st.markdown("### Answer")
        st.write(result["answer"])
        if result["sources"]:
            st.markdown("### Sources retrieved")
            for source in result["sources"]:
                with st.expander(f'{source["title"]} · relevance {source["score"]:.2f}'):
                    st.caption(source["path"])
                    st.write(source["text"])
        else:
            st.info("No sufficiently relevant source was found. Add verified material to the knowledge base or rephrase the question.")
    elif st.button("Clear question", key="clear_btn"):
        st.session_state["question"] = ""

with tab_compare:
    st.subheader("Career comparison")
    careers = rag.list_careers()
    c1, c2 = st.columns(2)
    with c1:
        first = st.selectbox("First career", careers, index=0)
    with c2:
        second = st.selectbox("Second career", careers, index=min(1, len(careers)-1))
    if st.button("Compare selected careers"):
        q = f"Compare {first} and {second}, including responsibilities, skills, beginner projects, and first learning steps."
        result = rag.answer(q, top_k=5)
        st.write(result["answer"])
        for source in result["sources"]:
            st.caption(f'Source: {source["title"]} ({source["path"]})')

with tab_roadmap:
    st.subheader("Starter learning roadmap")
    career = st.selectbox("Choose a career path", rag.list_careers(), key="roadmap_career")
    weeks = st.selectbox("Time horizon", [4, 8, 12], index=1, format_func=lambda x: f"{x} weeks")
    if st.button("Generate roadmap"):
        result = build_roadmap(career, weeks, rag)
        st.markdown(result["answer"])
        if result["sources"]:
            st.markdown("**Knowledge sources used**")
            for source in result["sources"]:
                st.caption(f'{source["title"]} — {source["path"]}')

with tab_about:
    st.markdown("""
    **How it works**
    1. Curated Markdown career guides are loaded from `knowledge/`.
    2. Sentence Transformers converts document chunks and questions into embeddings.
    3. ChromaDB retrieves semantically relevant chunks.
    4. The app shows source excerpts and uses a local text-generation model when enabled.

    **Responsible use:** this is an educational exploration tool, not a hiring, certification, or career-outcome guarantee. Verify certification requirements, exam prices, and employer expectations from official sources.
    """)
    st.code("python -m pip install -r requirements.txt\npython -m streamlit run app.py", language="bash")

if "recommendations" in st.session_state:
    st.divider()
    st.subheader("✨ Suggested paths to explore")
    st.caption("These are exploratory matches based on your answers, not a psychometric assessment.")
    for item in st.session_state["recommendations"]:
        st.markdown(f'**{item["career"]}** — {item["reason"]}')
        st.write("Try next:", item["next_step"])
