import threading
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from tools import (
    search_file, get_disk_info, get_ram_info,
    get_cpu_info, search_application, get_system_info,
    read_file, git_backup_before_edit,
    list_running_processes, get_windows_settings_help,
)
from config import OLLAMA_MODEL, OLLAMA_BASE_URL
from logger import log_question, log_error

chat_history = []

TOOLS = [
    search_file, get_disk_info, get_ram_info,
    get_cpu_info, search_application, get_system_info,
    read_file, git_backup_before_edit,
    list_running_processes, get_windows_settings_help,
]

SYSTEM_PROMPT = """You are Grain Rock, a secure Windows laptop assistant.

STRICT RULES:
1. READ-ONLY — never delete, modify or execute anything
2. Always ask permission before accessing anything
3. Never access C:\\ drive except allowed user folders
4. Never access passwords, keys, or credentials
5. Always tell user exactly what you are going to access
6. If user denies permission, respect it completely
7. Never run as administrator without permission
8. Always create Git backup before suggesting code edits
9. Be helpful, clear and transparent

FOR WINDOWS SETTINGS QUESTIONS:
When user asks about settings like Bluetooth, Display, WiFi,
Sound, etc. — use the get_windows_settings_help tool to give
exact navigation instructions.

FOR APP SEARCH:
When searching for installed applications, check:
- Windows Registry (installed programs)
- Start Menu shortcuts
- Common install folders
- Microsoft Store apps
- AppData\\Local\\Programs
- Desktop shortcuts
Always be thorough — check ALL locations before saying not found.
"""


def load_agent():
    try:
        llm = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.3,
        )
        agent = create_react_agent(
            model=llm,
            tools=TOOLS,
            prompt=SYSTEM_PROMPT,
        )
        return agent, None
    except Exception as e:
        log_error(str(e))
        return None, str(e)


def ask_agent(agent, question: str,
              stop_event: threading.Event = None) -> str:
    try:
        log_question(question)

        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        messages += [
            HumanMessage(content=m["content"])
            if m["role"] == "user"
            else AIMessage(content=m["content"])
            for m in chat_history[-10:]
        ]
        messages.append(HumanMessage(content=question))

        # Check stop before invoking
        if stop_event and stop_event.is_set():
            return "⏹  Stopped before processing."

        response = agent.invoke({"messages": messages})

        # Check stop after invoking
        if stop_event and stop_event.is_set():
            return "⏹  Stopped."

        answer = response["messages"][-1].content

        chat_history.append({"role": "user", "content": question})
        chat_history.append({"role": "assistant", "content": answer})

        if len(chat_history) > 20:
            chat_history.pop(0)
            chat_history.pop(0)

        return answer

    except Exception as e:
        log_error(str(e))
        return f"Error: {str(e)}"