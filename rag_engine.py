from pathlib import Path
import re
import hashlib
import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"
COLLECTION_NAME = "cyber_career_knowledge"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MIN_RELEVANCE = 0.30  # Tune using your own evaluation set; not a probability.

def parse_markdown(path: Path):
    text = path.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else path.stem.replace("_", " ").title()
    # Split on second-level headings while preserving heading names.
    sections = re.split(r"(?m)^##\s+", text)
    chunks = []
    for section in sections[1:]:
        lines = section.strip().splitlines()
        if not lines:
            continue
        heading = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        if body:
            chunks.append({"title": title, "section": heading, "text": f"{title} — {heading}\n{body}", "path": str(path.relative_to(Path(__file__).parent))})
    if not chunks and text.strip():
        chunks.append({"title": title, "section": "Overview", "text": text, "path": str(path.relative_to(Path(__file__).parent))})
    return chunks

class CyberCareerRAG:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.client = chromadb.PersistentClient(path=str(Path(__file__).parent / ".chroma"))
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        self._index_knowledge()

    def _index_knowledge(self):
        all_chunks = []
        for path in sorted(KNOWLEDGE_DIR.rglob("*.md")):
            if path.name.lower() in {"index.md", "readme.md"}:
                continue
            all_chunks.extend(parse_markdown(path))
        if not all_chunks:
            raise RuntimeError(f"No Markdown knowledge files found in {KNOWLEDGE_DIR}")
        # Rebuild on launch so edits to the small teaching knowledge base are reflected.
        existing = self.collection.get()
        if existing and existing.get("ids"):
            self.collection.delete(ids=existing["ids"])
        vectors = self.model.encode([c["text"] for c in all_chunks], normalize_embeddings=True)
        ids = [hashlib.sha1((c["path"] + c["section"]).encode()).hexdigest() for c in all_chunks]
        self.collection.add(
            ids=ids,
            embeddings=vectors.tolist(),
            documents=[c["text"] for c in all_chunks],
            metadatas=[{"title": c["title"], "section": c["section"], "path": c["path"]} for c in all_chunks]
        )

    def list_careers(self):
        careers = []
        for path in sorted((KNOWLEDGE_DIR / "careers").glob("*.md")):
            careers.append(path.stem.replace("_", " ").title())
        return careers or ["SOC Analyst", "Penetration Tester"]

    def retrieve(self, question, top_k=4):
        q_vector = self.model.encode([question], normalize_embeddings=True)[0]
        results = self.collection.query(
            query_embeddings=[q_vector.tolist()],
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"]
        )
        sources = []
        for doc, meta, distance in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
            score = max(0.0, min(1.0, 1.0 - float(distance)))
            sources.append({"title": meta["title"], "section": meta["section"], "path": meta["path"], "text": doc, "score": score})
        return sources

    def answer(self, question, top_k=4):
        sources = self.retrieve(question, top_k=top_k)
        relevant = [s for s in sources if s["score"] >= MIN_RELEVANCE]
        if not relevant:
            return {
                "answer": "I couldn't find sufficiently relevant information in the current career knowledge base. Try asking about a listed career, its skills, learning roadmap, certifications, or beginner projects.",
                "sources": []
            }
        # Transparent extractive answer: grounded and works without an LLM/API.
        # Upgrade path: pass relevant excerpts to a local/API LLM with strict source-only instructions.
        answer = "Based on the retrieved career guides:\n\n" + "\n\n".join(
            f'**{s["title"]} — {s["section"]}**\n{s["text"].splitlines()[1] if len(s["text"].splitlines()) > 1 else s["text"]}'
            for s in relevant[:3]
        )
        answer += "\n\n*This response summarizes retrieved notes. Check the cited source excerpts before relying on it.*"
        return {"answer": answer, "sources": relevant}
