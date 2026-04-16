# 🏦 FinAgentFlow — Automated Banking Task Orchestration

An AI-driven Python platform for automating routine banking tasks through intelligent workflow orchestration. Built with **LangGraph**, **EuriAI**, and **FastAPI**.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

FinAgentFlow enables users to define multi-step banking workflows (e.g., transaction reconciliation, compliance checks, customer communication drafting) via a web UI or REST API. Each workflow step is orchestrated by an agentic AI engine built on **LangGraph**, with human-readable outputs generated using **EuriAI (gpt-4.1-nano)**.

The platform produces structured data artifacts (JSON/CSV) and comprehensive audit trails for every workflow execution.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Task Definition** | Define banking tasks via web UI or REST API |
| **Modular Agents** | Pluggable agents — Reconciliation, Compliance, Communication |
| **LangGraph Orchestration** | Graph-based task sequencing with dependency resolution |
| **AI Content Generation** | EuriAI (gpt-4.1-nano) generated reports and summaries |
| **Structured Outputs** | JSON and CSV artifacts for every workflow step |
| **Audit Trail** | Complete step-by-step execution logging |
| **Extensible** | Add new task modules without modifying core code |

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌────────────────┐
│   Frontend   │────▶│   FastAPI REST    │────▶│  Orchestration │
│  (Streamlit) │◀────│     API Layer     │◀────│    Engine      │
└─────────────┘     └──────────────────┘     └───────┬────────┘
                                                      │
                           ┌──────────────────────────┼──────────────────┐
                           │                          │                  │
                    ┌──────▼──────┐  ┌────────────────▼┐  ┌─────────────▼──┐
                    │  Reconcile  │  │   Compliance     │  │ Communication  │
                    │    Agent    │  │     Agent        │  │     Agent      │
                    └──────┬──────┘  └────────┬────────┘  └───────┬────────┘
                           │                  │                    │
                    ┌──────▼──────────────────▼────────────────────▼──┐
                    │           AI Generation Layer                    │
                    │            (EuriAI — gpt-4.1-nano)              │
                    └──────────────────────┬──────────────────────────┘
                                           │
                    ┌──────────────────────▼──────────────────────────┐
                    │              Artifact Store                      │
                    │        (JSON / CSV / Reports / Logs)            │
                    └─────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Workflow Engine | LangGraph |
| AI Generation | EuriAI (gpt-4.1-nano) |
| REST API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Data Validation | Pydantic v2 |
| Storage | Local filesystem (JSON/CSV) |
| Testing | Pytest + pytest-asyncio |
| Package Manager | pip / uv |

---

## 📁 Project Structure

```
finagentflow/
├── app/
│   ├── __init__.py                 # App metadata
│   ├── core/                       # Configuration, logging, exceptions
│   │   ├── config.py               # Pydantic settings (env vars)
│   │   ├── logging.py              # Structured logging + audit trails
│   │   └── exceptions.py           # Custom exception hierarchy
│   ├── models/                     # Pydantic data models
│   │   ├── task.py                 # TaskDefinition, TaskResult
│   │   ├── workflow.py             # WorkflowDefinition, WorkflowExecution
│   │   ├── artifact.py             # Artifact model
│   │   └── user.py                 # UserInput model
│   ├── agents/                     # Task agent implementations
│   │   ├── base.py                 # Abstract TaskAgent base class
│   │   ├── reconciliation.py       # ReconcileAgent
│   │   ├── compliance.py           # ComplianceAgent
│   │   ├── communication.py        # CommunicationAgent
│   │   └── registry.py             # AgentRegistry (dynamic lookup)
│   ├── orchestration/              # Workflow orchestration engine
│   │   ├── dependency_resolver.py  # Topological sort
│   │   ├── graph_builder.py        # LangGraph StateGraph builder
│   │   └── workflow_manager.py     # WorkflowManager (lifecycle)
│   ├── generation/                 # AI content generation
│   │   ├── content_generator.py    # OpenAI / Google AI client
│   │   └── prompts.py             # Prompt templates
│   ├── storage/                    # Data persistence
│   │   └── artifact_store.py       # File-based artifact storage
│   └── api/                        # FastAPI REST API
│       ├── app.py                  # App factory
│       └── routes/
│           ├── health.py           # Health check
│           ├── workflows.py        # Workflow CRUD + execution
│           ├── tasks.py            # Agent listing
│           └── artifacts.py        # Artifact retrieval
├── frontend/
│   └── streamlit_app.py           # Streamlit web UI
├── tests/
│   ├── test_models.py             # Model unit tests
│   ├── test_dependency_resolver.py # Dependency resolver tests
│   ├── test_agents.py             # Agent unit tests
│   └── test_integration.py        # End-to-end tests
├── data/
│   └── samples/                   # Sample banking data
│       ├── ledger_transactions.json
│       └── bank_statement.json
├── main.py                        # CLI entry point (api/ui/demo)
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Project configuration
├── .env.example                   # Environment template
├── pytest.ini                     # Test configuration
└── README.md                      # This file
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- EuriAI API key ([get one here](https://euron.one))

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/finagentflow.git
cd finagentflow

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your EURI_API_KEY
```

---

## 💡 Usage

### Start the API Server
```bash
python main.py api
# Server runs at http://localhost:8000
# Docs at http://localhost:8000/api/v1/docs
```

### Start the Web UI
```bash
python main.py ui
# Opens at http://localhost:8501
```

### Run the Demo
```bash
python main.py demo
# Runs a sample workflow with test data
```

---

## 📡 API Documentation

Once the API is running, interactive docs are available at:
- **Swagger UI**: `http://localhost:8000/api/v1/docs`
- **ReDoc**: `http://localhost:8000/api/v1/redoc`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/workflows` | Create a workflow |
| `GET` | `/api/v1/workflows` | List all workflows |
| `POST` | `/api/v1/workflows/{id}/run` | Execute a workflow |
| `GET` | `/api/v1/workflows/{id}/executions` | List executions |
| `GET` | `/api/v1/tasks/agents` | List available agents |
| `GET` | `/api/v1/artifacts/{workflow_id}` | Get workflow artifacts |
| `GET` | `/api/v1/health` | Health check |

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_agents.py

# Run specific test
pytest tests/test_agents.py::TestReconcileAgent::test_reconciliation
```

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

**Built with ❤️ by Satish Kumar**
