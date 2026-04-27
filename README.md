# 🧠 RecallAI - Intelligent Memory System

> A personal AI assistant that **remembers you across sessions** — powered by Groq's blazing-fast LLM, ChromaDB semantic search, and JSON episodic storage. Accessible via **Telegram** and a **Streamlit web interface**.


---

## ✨ Features

- 🧠 **Dual Memory Engine** — JSON for recent context + ChromaDB for semantic search across all history
- 💬 **Telegram Bot** — chat via Telegram on any device, anytime
- 🌐 **Streamlit UI** — test and chat via browser locally
- ⚡ **Groq Powered** — blazing fast responses using `llama-3.3-70b-versatile` (free tier)
- 🔍 **Semantic Search** — finds relevant memories by meaning, not just recency
- 👤 **Per-User Memory** — each user gets their own isolated memory store
- 🔄 **Persistent Storage** — memory survives bot restarts and sessions

---

## 🏗️ Architecture

```
User sends message
       ↓
┌─────────────────────────────────┐
│         Memory Engine           │
│                                 │
│  JSON  → last 8 episodes        │
│  ChromaDB → semantic search     │
│         top 5 relevant          │
└──────────────┬──────────────────┘
               ↓
     Combined context prompt
               ↓
┌─────────────────────────────────┐
│           Groq API              │
│   llama-3.3-70b-versatile       │
└──────────────┬──────────────────┘
               ↓
    Context-aware AI response
               ↓
     Save as new episode to
     JSON + ChromaDB vectors
```

---

## 📁 Folder Structure

```
telegram_chatbot/
│
├── telegram_bot/               ← all source files go here
│   ├── bot.py                  # Telegram bot — handlers & Groq integration
│   ├── memory_engine.py        # Dual memory — JSON + ChromaDB
│   ├── streamlit_app.py        # Streamlit web interface
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Secret keys (never commit this!)
│   │
│   ├── memories/               # Auto-created — JSON storage per user
│   │   └── {user_id}.json
│   │
│   └── chroma_db/              # Auto-created — ChromaDB vector store
│
└── venv/                       # Virtual environment
```

---

## 🛠️ Prerequisites

- Python 3.10+
- A **Groq API key** → [console.groq.com](https://console.groq.com)
- A **Telegram Bot Token** → get from [@BotFather](https://t.me/BotFather) on Telegram

---

## ⚙️ Setup

### 1. Navigate to project folder
```bash
cd telegram_chatbot
```

### 2. Create & activate virtual environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Go into source folder
```bash
cd telegram_bot
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```
> ⚠️ First install takes 3-5 minutes — downloads the `all-MiniLM-L6-v2` embedding model (~80MB)

### 5. Configure your keys

Edit the `.env` file:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GROQ_API_KEY=your_groq_api_key_here
```

---

## 🚀 Running the App

### Option A: Streamlit Web Interface
```bash
streamlit run streamlit_app.py
```
Opens at **http://localhost:8501** 🌐

### Option B: Telegram Bot
```bash
python bot.py
```
Find your bot on Telegram and start chatting! 💬

> 💡 Both interfaces share the **same memory engine** — conversations from Streamlit are remembered in Telegram and vice versa!

---

## 🤖 Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Greet the bot and see available commands |
| `/memory` | See memory stats — JSON episodes + ChromaDB vectors |
| `/clear` | Wipe all memory (JSON + ChromaDB) and start fresh |

---

## 🧠 How the Dual Memory Works

| Layer | Storage | Purpose |
|-------|---------|---------|
| **JSON** | `memories/{user_id}.json` | Stores every episode, loads last 8 for recent context |
| **ChromaDB** | `chroma_db/` | Embeds every episode as a vector, semantically searches top 5 relevant memories |

Each saved episode looks like:
```json
{
  "timestamp": "2026-04-25T11:30:00",
  "user": "My name is Nithish and I prefer Python",
  "bot": "Nice to meet you Nithish! I'll remember your preference for Python."
}
```

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `python-telegram-bot` | Telegram bot framework |
| `groq` | Groq API client (LLM) |
| `chromadb` | Vector database for semantic memory |
| `sentence-transformers` | Embedding model for ChromaDB |
| `streamlit` | Web chat interface |
| `python-dotenv` | Load `.env` variables |

---

## 🔒 Security Notes

- **Never commit your `.env` file** to GitHub
- Add `.env` and `chroma_db/` and `memories/` to your `.gitignore`
```
.env
memories/
chroma_db/
venv/
.venv/
```

---

## 💡 Ideas to Improve

- [ ] Deploy Streamlit app to [Streamlit Cloud](https://streamlit.io/cloud)
- [ ] Host Telegram bot on a server (Railway, Render, etc.)
- [ ] Add voice message support
- [ ] Add multi-language support
- [ ] Build a memory timeline visualizer
- [ ] Add user authentication to Streamlit interface

---



---


