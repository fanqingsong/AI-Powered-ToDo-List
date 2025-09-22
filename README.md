# Agentic app with Azure AI Foundry Agent Service

This repository demonstrates how to build a modern FatAPI web application that integrates with Azure AI Foundry Agents. It provides a simple CRUD task management and the interactive chat agents to manage the tasks with nature language!

![Task Management AI Agent](ai-powered-todo-list-min.gif)

## Getting Started

See [Develop Agentic To-Do List with Azure AI Foundry Agent Service](https://medium.com/@organicprogrammer/b47a465fe56b).

## Run the application

`uvicorn src.app:app --host 0.0.0.0 --port 3000`

## Features

- **Task List**: Simple CRUD web app application.
- **Azure AI Foundry Agent**: Chat with an agent powered by Azure AI Foundry Agent Service to management the task. 

## Project Structure

```
public/
└── index.html                   # React frontend
src/
├── __init__.py
├── app.py                       # Main FastAPI application
├── agents/                      # AI agent implementations
│   ├── __init__.py
│   ├── foundry_task_agent.py    # Azure AI Foundry agent
│   └── agent_tools.py           # Agent tools with function calling
├── models/                      # Pydantic models for data validation
│   └── __init__.py
├── routes/                      # API route definitions
│   ├── __init__.py
│   └── api.py                   # Task and chat endpoints
└── services/                    # Business logic services
    ├── __init__.py
    └── task_service.py          # Task CRUD operations with SQLite
tasks.db                         # SQLite database file
requirements.txt                 # Python dependencies
README.md                        # Project documentation
```