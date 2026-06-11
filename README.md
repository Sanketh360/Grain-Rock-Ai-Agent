# ⚡ Grain Rock

Grain Rock is a **local Agentic AI Desktop Assistant** built using **Python, LangChain, LangGraph, Ollama, Qwen 2.5, and CustomTkinter**.

The goal of Grain Rock is to allow users to interact with their laptop using natural language instead of manually searching through files, checking system settings, or monitoring resources.

Grain Rock runs completely **offline**, ensuring privacy and security while providing real-time information about the system.

---

# 🚀 Features

## 🖥 System Monitoring

- CPU Information
- RAM Usage
- Disk Usage
- System Details
- Running Processes
- Storage Statistics

### Example Queries

```text
How much RAM is available?

How many CPU cores do I have?

What is my current disk usage?

Show system information.
```

---

## 📂 File Search

Search files and folders using natural language.

### Example Queries

```text
Is there a PDF called resume?

Find my Java project.

Search for a file named report.pdf.
```

---

## 📦 Application Search

Search installed applications and locate them.

### Example Queries

```text
Is Blender installed?

Find Visual Studio Code.

Search for IntelliJ IDEA.
```

---

## 🔐 Security Features

- Read-only operation
- Permission confirmation system
- Sensitive path protection
- Audit logging
- Secure file access restrictions

---

## 📜 Logging

Every action is logged for auditing purposes.

Logs include:

- User queries
- Tool usage
- Permission decisions
- Errors

Log file:

```text
grainrock_audit.log
```

---

# 🏗 Architecture

```text
User
 │
 ▼
CustomTkinter Desktop UI
 │
 ▼
LangGraph ReAct Agent
 │
 ▼
LangChain
 │
 ├── File Search Tool
 ├── Disk Information Tool
 ├── RAM Information Tool
 ├── CPU Information Tool
 ├── Application Search Tool
 ├── Process Monitoring Tool
 │
 ▼
Ollama
 │
 ▼
Qwen 2.5 7B
```

---

# 🛠 Tech Stack

| Layer | Technology |
|---------|------------|
| Programming Language | Python 3.14+ |
| Desktop UI | CustomTkinter |
| Agent Framework | LangChain |
| Agent Workflow | LangGraph |
| LLM Runtime | Ollama |
| AI Model | Qwen 2.5 7B |
| System Monitoring | psutil |
| Image Handling | Pillow |
| Logging | Python Logging |

---

# 📁 Project Structure

```text
GrainRock/
│
├── main.py
├── agent.py
├── tools.py
├── security.py
├── logger.py
├── config.py
│
├── assets/
│   ├── logo.png
│   └── logo.ico
│
├── grainrock_audit.log
├── requirements.txt
└── README.md
```

---

# ⚙️ Prerequisites

Before running Grain Rock, install the following:

## Python

Verify installation:

```bash
python --version
```

Expected:

```text
Python 3.14+
```

---

## Git

Verify:

```bash
git --version
```

---

## Ollama

Download and install:

https://ollama.com

Verify:

```bash
ollama --version
```

---

# 📥 Installation

## 1. Clone Repository

```bash
git clone <repository-url>
cd GrainRock
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv grainrock-env
grainrock-env\Scripts\activate
```

### Linux / Ubuntu

```bash
python3 -m venv grainrock-env
source grainrock-env/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install langchain
pip install langchain-community
pip install langchain-ollama
pip install langgraph
pip install customtkinter
pip install psutil
pip install pillow
```

---

# 🤖 Download AI Model

Start Ollama:

```bash
ollama serve
```

Open a second terminal and download the model:

```bash
ollama pull qwen2.5:7b
```

Verify:

```bash
ollama list
```

Expected:

```text
NAME         SIZE
qwen2.5:7b   4.7 GB
```

---

# ▶️ Running Grain Rock

Activate virtual environment:

### Windows

```bash
grainrock-env\Scripts\activate
```

### Ubuntu

```bash
source grainrock-env/bin/activate
```

Run application:

```bash
python main.py
```

---

# 💬 Example Queries

## File Search

```text
Is there a PDF called resume?

Find project report.

Search for a file named invoice.pdf.
```

---

## System Information

```text
How much RAM is available?

Show CPU information.

How much storage is remaining?

Show system information.
```

---

## Applications

```text
Is Blender installed?

Find Visual Studio Code.

Search for IntelliJ IDEA.
```

---

## Processes

```text
What applications are currently running?

Show active processes.
```

---

# 🔒 Security Architecture

Grain Rock follows a secure-by-default design.

## Read-Only Mode

The AI cannot:

- Delete files
- Modify files
- Execute scripts
- Run terminal commands automatically

---

## Blocked Sensitive Locations

Examples:

```text
.ssh
.aws
.env
wallet
credentials
id_rsa
```

---

## Protected Extensions

```text
.pem
.key
.ppk
.p12
.pfx
.kdbx
```

---

## Permission Layer

Certain operations require user approval:

```text
Allow access?
[Yes] [No]
```

---

## Audit Logging

All actions are logged:

```text
grainrock_audit.log
```

Including:

- User queries
- Tool calls
- Permission decisions
- Errors

---

# 🖥 Recommended Environment

## VMware Setup

```text
OS       : Ubuntu 24.04 / 26.04
RAM      : 4 GB
CPU      : 3 Cores
Disk     : 40 GB
Network  : NAT
```

---

# 🎯 Future Enhancements

- Voice Assistant
- Screenshot Analysis
- MCP Support
- Browser Agent
- Multi-Agent Architecture
- Project Memory
- Git Assistant
- Codebase Analyzer
- Real-Time Dashboard
- Plugin System

---

# 👨‍💻 Author

**Sanketh K Kottary**

---

## Grain Rock

**"Manage your laptop through natural language — privately, securely, and completely offline."**
