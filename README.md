# Cyber Career Navigator AI

A beginner-friendly Retrieval-Augmented Generation (RAG) project that helps cybersecurity learners explore career paths using a curated Markdown knowledge base.

## Features

- Semantic search with Sentence Transformers (`all-MiniLM-L6-v2`)
- Persistent local ChromaDB vector store (rebuilt from Markdown at app startup)
- Source excerpts shown alongside answers
- Basic relevance threshold and unsupported-question fallback
- Career interest questionnaire with transparent rule-based suggestions
- Career comparison and starter roadmap views
- Ten-question retrieval evaluation script

> This starter uses extractive, source-grounded responses by default. It does not call a generative LLM or guarantee career outcomes. Add a local model or API only after the retrieval and evaluation are reliable.

## Requirements

- Python 3.10–3.12 recommended
- Internet access for initial package/model downloads
- 4 GB RAM recommended; the embedding model download is required on first run

## Setup (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`.

## Evaluate retrieval

Stop Streamlit if needed, then run:

```powershell
python evaluate.py
```

The first run downloads the embedding model. If the environment is offline, model initialization will fail until the model is available locally.

## Project structure

```text
cyber_career_navigator/
├── app.py
├── rag_engine.py
├── career_advisor.py
├── evaluate.py
├── requirements.txt
└── knowledge/
    ├── careers/
    ├── skills/
    ├── projects/
    └── certifications/
```

## Add knowledge

Create `.md` files under `knowledge/`. Use a title and descriptive `##` sections. Prefer concise, factual, dated information with source URLs and a `Last reviewed` field. The loader splits each file by second-level headings.

## Accuracy and safety notes

- Similarity scores are ranking signals, not confidence probabilities.
- The included relevance threshold is a starting point; tune it against evaluation examples.
- Certification names and requirements can change. Verify current details on official provider websites before publishing.
- Only practice penetration testing on systems you own or have explicit permission to test.
- Do not add confidential student information or secrets to the knowledge base.
