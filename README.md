# 🏦 FinAgentFlow — Automated Banking Task Orchestration

An AI-driven Python platform for automating routine banking tasks through intelligent workflow orchestration. Built with **LangGraph**, **EuriAI**, and **FastAPI**.

> **Internship Project 2026** — Satish Kumar

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Environment Variables](#environment-variables)
- [API Documentation](#api-documentation)
- [Testing](#testing)
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
| **LangGraph Orchestration** | Graph-based task sequencing with topological dependency resolution |
| **AI Content Generation** | EuriAI (gpt-4.1-nano) generated reports and summaries |
| **Structured Outputs** | JSON and CSV artifacts for every workflow step |
| **Audit Trail** | Complete step-by-step execution logging with timestamped audit logs |
| **Extensible** | Add new task modules without modifying core code via `AgentRegistry` |
| **REST API** | Full OpenAPI-documented async REST API with Swagger UI |
| **Continue-on-Failure** | Optional flag to allow workflows to continue past failed steps |
| **Execution History** | All workflow executions are stored and queryable via API |

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

Architecture diagrams (PNG) are available in the [`Architecture__Flowcharts/`](Architecture__Flowcharts/) folder:

| Diagram | File |
|---|---|
| System Architecture | `01_system_architecture.png` |
| Data Flow | `02_data_flow.png` |
| Workflow Execution Flow | `03_workflow_execution_flow.png` |
| Class Diagram | `04_class_diagram.png` |
| Tech Stack Overview | `05_tech_stack.png` |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Workflow Engine | LangGraph |
| Agentic Framework | Custom agent pattern (`TaskAgent` + `AgentRegistry`) — implements agentic-AI concepts natively |
| AI Generation | EuriAI (gpt-4.1-nano) |
| REST API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Data Validation | Pydantic v2 + pydantic-settings |
| Storage | Local filesystem (JSON/CSV) |
| Testing | Pytest + pytest-asyncio (27 tests) |
| Package Manager | pip / uv |

---

## 📁 Project Structure

```
FinAgentFlow/
├── app/
│   ├── __init__.py                 # App metadata
│   ├── core/                       # Configuration, logging, exceptions
│   │   ├── config.py               # Pydantic settings (env vars)
│   │   ├── logging.py              # Structured logging + audit trails
│   │   └── exceptions.py           # Custom exception hierarchy
│   ├── models/                     # Pydantic data models
│   │   ├── task.py                 # TaskDefinition, TaskResult, TaskType
│   │   ├── workflow.py             # WorkflowDefinition, WorkflowExecution
│   │   ├── artifact.py             # Artifact, ArtifactType
│   │   └── user.py                 # UserInput model
│   ├── agents/                     # Task agent implementations
│   │   ├── base.py                 # Abstract TaskAgent base class
│   │   ├── reconciliation.py       # ReconcileAgent
│   │   ├── compliance.py           # ComplianceAgent
│   │   ├── communication.py        # CommunicationAgent
│   │   └── registry.py             # AgentRegistry (dynamic lookup)
│   ├── orchestration/              # Workflow orchestration engine
│   │   ├── dependency_resolver.py  # Topological sort + cycle detection
│   │   ├── graph_builder.py        # LangGraph StateGraph builder
│   │   └── workflow_manager.py     # WorkflowManager (full lifecycle)
│   ├── generation/                 # AI content generation
│   │   ├── content_generator.py    # EuriAI client + retry + caching
│   │   └── prompts.py              # Prompt templates per task type
│   ├── storage/                    # Data persistence
│   │   └── artifact_store.py       # File-based artifact storage
│   └── api/                        # FastAPI REST API
│       ├── app.py                  # App factory + CORS + redirects
│       └── routes/
│           ├── health.py           # Health check endpoint
│           ├── workflows.py        # Workflow CRUD + execution + executions
│           ├── tasks.py            # Agent listing
│           └── artifacts.py        # Artifact retrieval + download
├── frontend/
│   └── streamlit_app.py            # Streamlit web UI
├── tests/
│   ├── test_models.py              # Model unit tests (7 tests)
│   ├── test_dependency_resolver.py # Dependency resolver tests (5 tests)
│   ├── test_agents.py              # Agent + registry unit tests (7 tests)
│   └── test_integration.py         # End-to-end workflow tests (8 tests)
├── data/
│   └── samples/                    # Sample banking data
│       ├── ledger_transactions.json
│       └── bank_statement.json
├── Architecture__Flowcharts/       # System design diagrams (PNG)
├── main.py                         # CLI entry point (api / ui / demo)
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Project + tool configuration
├── .env.example                    # Environment variable template
├── pytest.ini                      # Test configuration
└── README.md                       # This file
```

---

## 🚀 Getting Started

### Prerequisites

- Python **3.10+**
- EuriAI API key — [get one at euron.one](https://euron.one)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/finagentflow.git
cd finagentflow

# 2. Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Open .env and set your EURI_API_KEY
```

---

## 💡 Usage

All commands are run from the project root with the virtual environment activated.

### Start the API Server — Terminal 1
```bash
python main.py api
```
> Server starts at **http://localhost:8000**
> Swagger docs at **http://localhost:8000/docs**

### Start the Web UI — Terminal 2 (keep API running)
```bash
python main.py ui
```
> Opens at **http://localhost:8501**

### Run the Built-in Demo Pipeline — Terminal 3
```bash
python main.py demo
```
> Executes a full 3-agent pipeline (Reconcile → Comply → Draft) using sample banking data from `data/samples/`.
> Artifacts are saved to `data/artifacts/`.

---

## 🔧 Environment Variables

Copy `.env.example` to `.env` and configure the following:

| Variable | Default | Description |
|---|---|---|
| `EURI_API_KEY` | *(required)* | Your EuriAI API key from [euron.one](https://euron.one) |
| `EURI_MODEL` | `gpt-4.1-nano` | EuriAI model to use for AI generation |
| `EURI_TEMPERATURE` | `0.3` | Generation temperature (0.0 – 1.0) |
| `EURI_MAX_TOKENS` | `2048` | Max tokens per AI generation call |
| `EURI_RETRY_ATTEMPTS` | `3` | Number of retry attempts on API failure |
| `API_HOST` | `0.0.0.0` | FastAPI host (use `localhost` in browser) |
| `API_PORT` | `8000` | FastAPI port |
| `API_PREFIX` | `/api/v1` | REST API route prefix |
| `STREAMLIT_PORT` | `8501` | Streamlit frontend port |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`) |
| `STORAGE_BACKEND` | `local` | Storage backend (`local` filesystem) |

---

## 📡 API Documentation

Once the API is running, interactive docs are available at:

- **Swagger UI**: `http://localhost:8000/docs` *(redirects to `/api/v1/docs`)*
- **ReDoc**: `http://localhost:8000/redoc` *(redirects to `/api/v1/redoc`)*

### Full Endpoint Reference

#### Workflows

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/workflows` | Create a new workflow |
| `POST` | `/api/v1/workflows/from-user-input` | Create workflow from `UserInput` schema |
| `GET` | `/api/v1/workflows` | List all workflows |
| `GET` | `/api/v1/workflows/{id}` | Get a specific workflow |
| `POST` | `/api/v1/workflows/{id}/tasks` | Append a task to an existing workflow |
| `POST` | `/api/v1/workflows/{id}/run` | Execute a workflow |
| `GET` | `/api/v1/workflows/{id}/executions` | List executions for a workflow |

#### Executions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/executions` | List all executions across all workflows |
| `GET` | `/api/v1/executions/{id}` | Get a specific execution result |
| `GET` | `/api/v1/executions/{id}/audit-log` | Get the raw audit log for an execution |

#### Artifacts

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/artifacts/{workflow_id}` | List all artifacts for a workflow |
| `GET` | `/api/v1/artifacts/{workflow_id}/{task_id}/{artifact_id}` | Get artifact content |
| `GET` | `/api/v1/artifacts/{workflow_id}/{task_id}/{artifact_id}/download` | Download artifact file |

#### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | API health check |
| `GET` | `/api/v1/tasks/agents` | List all registered agent types |

---

## 🧪 Testing

The project includes **27 automated tests** across 4 test modules.

```bash
# Run all 27 tests
pytest

# Run with verbose output
pytest -v

# Run a specific test module
pytest tests/test_agents.py
pytest tests/test_dependency_resolver.py
pytest tests/test_integration.py
pytest tests/test_models.py

# Run a specific test
pytest tests/test_agents.py::TestReconcileAgent::test_reconciliation
```

### Test Coverage

| Module | Tests | What It Covers |
|---|---|---|
| `test_models.py` | 7 | `TaskDefinition`, `TaskResult`, `WorkflowDefinition`, `WorkflowExecution`, `Artifact`, `UserInput` |
| `test_agents.py` | 7 | `ReconcileAgent`, `ComplianceAgent`, `CommunicationAgent`, `AgentRegistry` |
| `test_dependency_resolver.py` | 5 | Linear, diamond, single, no-dependency graphs; circular dependency detection |
| `test_integration.py` | 8 | End-to-end workflow creation, retrieval, execution, task appending, cycle rejection |

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

**Built with ❤️ by Satish Kumar — Internship Project 2026**
