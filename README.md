# 🔌 MCP-Based Modular Tooling System

This repository demonstrates a **modular system of MCP (Model Context Protocol) servers** with a **shared client interface**, enabling interaction with both external APIs (news, Wikipedia, stock market) and local SQLite databases.

---

## 📚 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Server 1: News & Wikipedia Agent](#server-1-news--wikipedia-agent)
- [Server 2: SQLite Database Agent](#server-2-sqlite-database-agent)
- [Client Interface](#client-interface)
- [How to Run](#how-to-run)
- [Dependencies](#dependencies)


---

## 🧠 Overview

This system is built using [`FastMCP`](https://github.com/mcptutorial/mcp-use), a minimal server interface for deploying callable tools in LLM-based environments.

- 🔎 **MCP News Server**: Fetches news headlines and Wikipedia summaries
- 🗂 **MCP SQLite Server**: Handles CRUD operations over a local SQLite database
- 🤝 **Shared Client Notebook**: Connects to any MCP server and interacts via tool calls

---

## 🏗 Architecture

```
                ┌──────────────────────┐
                │    ollama_client     │
                │  (Jupyter Notebook)  │
                └─────────┬────────────┘
                          │
          ┌───────────────┼────────────────────┐
          ▼                                       ▼
┌──────────────────────┐             ┌─────────────────────────┐
│  MCP News Server     │             │   MCP SQLite Server     │
│  (news-server.py)        │             │   (sqlite-server.py)    │
│ ──────────────────── │             │ ─────────────────────── │
│ get_latest_news()     │             │ add_data()              │
│ get_wikipedia_summary()│            │ read_data()             │
│ get_stock_news()       │            │ update_people()         │
│                        │            │ delete_person()         │
└──────────────────────┘             └─────────────────────────┘
```

## MCP News Architecture


```
              ┌────────────────────────────┐
              │     Client (Notebook)      │
              │  e.g., ollama_client.ipynb │
              └────────────┬───────────────┘
                           │  call("tool_name", {...})
                           ▼
              ┌────────────────────────────┐
              │      FastMCP Server        │
              │      (news-server.py)          │
              │        ID: news-demo       │
              └──────┬────────────┬────────┘
                     │            │
     ┌───────────────┘            └─────────────────────────────┐
     ▼                                                      ▼   ▼
┌───────────────┐                                ┌────────────────────────┐
│ get_latest_news() │ <─── HTTP ─── fetch ───┐    │ get_stock_news()      │
│                 │                         │    │                        │
│ Scrapes NPR/BBC │                         │    │ Scrapes Finviz         │
└───────────────┘                         │    └────────────────────────┘
                                         │
┌────────────────────┐                  ▼
│ get_wikipedia_summary() │ ◀─── REST ── Wikipedia API
└────────────────────┘


```


## MCP Sqlite Architecture

```

                     ┌──────────────────────┐
                     │   ollama_client.ipynb│
                     │ (Shared MCP Client)  │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │  MCP SQLite Server   │
                     │ (sqlite-server.py)   │
                     └──────────┬───────────┘
                                │
         ┌──────────────────────┼────────────────────────┐
         ▼                      ▼                        ▼
  ┌───────────────┐     ┌───────────────┐        ┌─────────────────┐
  │  add_data()    │     │  read_data()  │        │ update_people() │
  │ SQL INSERT     │     │ SQL SELECT    │        │ SQL UPDATE      │
  └───────────────┘     └───────────────┘        └─────────────────┘
                                ▼
                         ┌───────────────┐
                         │ delete_person │
                         │  SQL DELETE   │
                         └───────────────┘

Database Schema: `people(id, name, age, profession)`
Stored in `demo.db` (SQLite)


```





---

## 📁 Project Structure

```bash
.
├── mcp-news-server/
│   └── news-server.py
│
├── mcp-sqlite-server/
│   └── sqlite-server.py
│
├── mcp-client/
│   └── ollama_client.ipynb
│
└── README.md

```

---

## 🌐 Server 1: News & Wikipedia Agent

### File: `mcp-news-server/servers.py`

### 🔧 Tools

| Tool | Description |
|------|-------------|
| `get_latest_news(source)` | Fetches top headlines from NPR/BBC |
| `get_wikipedia_summary(topic)` | Retrieves the Wikipedia intro summary |
| `get_stock_news(ticker)` | Pulls latest stock headlines from Finviz |

### 🏁 Run

```bash
uv run servers.py --server_type=sse
```

---

## 🗃 Server 2: SQLite Database Agent

### File: `mcp-sqlite-server/ollama_server.py`

### 🔧 Tools

| Tool | Description |
|------|-------------|
| `add_data(query)` | Adds a new record using `INSERT INTO` |
| `read_data(query)` | Reads records using `SELECT` |
| `update_people(query)` | Updates existing records |
| `delete_person(query)` | Deletes entries using `DELETE` |

### 🏁 Run

```bash
uv run ollama_server.py --server_type=sse
```

📝 *Note: The database file `demo.db` is created on the fly and follows a simple `people(name, age, profession)` schema.*

---

## 🧪 Client Interface

### File: `mcp-client/ollama_client.ipynb`

This Jupyter notebook lets you connect to any running MCP server and invoke registered tools.

### 🔄 Supported Actions

```python
client.call("get_wikipedia_summary", {"topic": "LLM"})
client.call("add_data", {"query": "INSERT INTO people (name, age, profession) VALUES ('Jane', 32, 'Scientist')"})
client.call("read_data", {"query": "SELECT * FROM people"})
```

---

## 🚀 How to Run

1. **Start MCP Server (choose one):**

```bash
# News & Wikipedia
uv run mcp-news-server/news-server.py --server_type=sse

# OR SQLite
uv run mcp-sqlite-server/sqlite-server.py --server_type=sse
```

2. **Open Client:**

```bash
jupyter notebook mcp-client/ollama_client.ipynb
```

3. **Use `client.call()`** to invoke any tool exposed by the active server.

---

## 📦 Dependencies

Install these first:

```bash
pip install mcp llama-index requests beautifulsoup4
```

---
