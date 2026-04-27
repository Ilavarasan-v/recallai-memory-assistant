import json
import os
from datetime import datetime

import chromadb
from chromadb.utils import embedding_functions

# ── Config ─────────────────────────────────────────────────────────────────────
MEMORY_DIR = "memories"
CHROMA_DIR = "chroma_db"

# Use ChromaDB's built-in sentence transformer for embeddings (no API key needed)
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Initialize ChromaDB persistent client
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)


# ── Helpers ────────────────────────────────────────────────────────────────────
def _get_memory_path(user_id: int) -> str:
    """Get the file path for a user's JSON memory file."""
    os.makedirs(MEMORY_DIR, exist_ok=True)
    return os.path.join(MEMORY_DIR, f"{user_id}.json")


def _get_chroma_collection(user_id: int):
    """Get or create a ChromaDB collection for a user."""
    return chroma_client.get_or_create_collection(
        name=f"user_{user_id}",
        embedding_function=embedding_fn,
    )


# ── JSON Memory (Recent Context) ───────────────────────────────────────────────
def load_episodes(user_id: int) -> list:
    """Load all episodes from JSON for a user."""
    path = _get_memory_path(user_id)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def save_episode(user_id: int, user_message: str, bot_response: str) -> None:
    """Save a new episode to both JSON and ChromaDB."""
    timestamp = datetime.now().isoformat()

    # ── Save to JSON ──────────────────────────────────────────────────────────
    episodes = load_episodes(user_id)
    episode = {
        "timestamp": timestamp,
        "user": user_message,
        "bot": bot_response,
    }
    episodes.append(episode)
    path = _get_memory_path(user_id)
    with open(path, "w") as f:
        json.dump(episodes, f, indent=2)

    # ── Save to ChromaDB ──────────────────────────────────────────────────────
    collection = _get_chroma_collection(user_id)
    episode_id = f"{user_id}_{timestamp}"
    combined_text = f"User: {user_message}\nAssistant: {bot_response}"
    collection.add(
        documents=[combined_text],
        ids=[episode_id],
        metadatas=[{"timestamp": timestamp, "user_id": str(user_id)}],
    )


# ── ChromaDB Memory (Semantic Search) ─────────────────────────────────────────
def search_relevant_episodes(user_id: int, query: str, top_k: int = 5) -> str:
    """Search ChromaDB for episodes semantically relevant to the query."""
    collection = _get_chroma_collection(user_id)

    if collection.count() == 0:
        return ""

    results = collection.query(
        query_texts=[query],
        n_results=min(top_k, collection.count()),
    )

    if not results["documents"] or not results["documents"][0]:
        return ""

    lines = ["Relevant past conversations (semantic search):"]
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        ts = meta.get("timestamp", "")[:10]
        lines.append(f"[{ts}] {doc}")
        lines.append("")

    return "\n".join(lines)


# ── Combined Context Builder ───────────────────────────────────────────────────
def build_context_prompt(user_id: int, query: str = "", last_n: int = 8) -> str:
    """
    Build a rich context prompt combining:
    - Last N episodes from JSON (recent flow)
    - Top semantically relevant episodes from ChromaDB
    """
    context_parts = []

    # Part 1: Semantic search from ChromaDB
    if query:
        semantic_context = search_relevant_episodes(user_id, query, top_k=5)
        if semantic_context:
            context_parts.append(semantic_context)

    # Part 2: Recent episodes from JSON
    episodes = load_episodes(user_id)
    if episodes:
        recent = episodes[-last_n:]
        lines = ["Recent conversation history:"]
        for ep in recent:
            lines.append(f"[{ep['timestamp'][:10]}]")
            lines.append(f"User: {ep['user']}")
            lines.append(f"Assistant: {ep['bot']}")
            lines.append("")
        context_parts.append("\n".join(lines))

    return "\n\n".join(context_parts)


# ── Memory Management ──────────────────────────────────────────────────────────
def clear_memory(user_id: int) -> None:
    """Delete all memory for a user from both JSON and ChromaDB."""
    path = _get_memory_path(user_id)
    if os.path.exists(path):
        os.remove(path)
    try:
        chroma_client.delete_collection(name=f"user_{user_id}")
    except Exception:
        pass


def get_memory_summary(user_id: int) -> str:
    """Return a human-readable summary of stored memory."""
    episodes = load_episodes(user_id)
    collection = _get_chroma_collection(user_id)
    chroma_count = collection.count()

    if not episodes:
        return "I have no memory of you yet. Start chatting!"

    total = len(episodes)
    first = episodes[0]["timestamp"][:10]
    last = episodes[-1]["timestamp"][:10]

    return (
        f"📝 JSON Episodes: {total}\n"
        f"🧠 ChromaDB Vectors: {chroma_count}\n"
        f"📅 First conversation: {first}\n"
        f"🕒 Most recent: {last}"
    )