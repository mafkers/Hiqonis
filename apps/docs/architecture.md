# 🏗️ Hiqonis Technical Architecture

Hiqonis is structured as a **Modular Monolith** applying **Domain-Driven Design (DDD)** and **Clean Architecture (Hexagonal)** principles.

```
+-------------------------------------------------------------+
|                     Presentation Layer                      |
|                  FastAPI HTTP / WebSockets                  |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                      Application Layer                      |
|                 Use Cases / Workflow Orchestrators          |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                        Domain Layer                         |
|                 Entities / Value Objects / Interfaces        |
+-------------------------------------------------------------+
                               ^
                               |
+------------------------------+------------------------------+
|                     Infrastructure Layer                    |
|             Adapters (WhatsApp, pgvector, MinIO)            |
+-------------------------------------------------------------+
```

## Bounded Contexts

The codebase is organized into modular directories representing our subdomains in `libs/core/`:

1. **Conversation Engine** (`libs/core/conversation`): Manages multi-channel conversation sessions, messages, and human takeover handoff.
2. **Agent Manager** (`libs/core/agent`): Handles agent configuration, tool registrations, system instructions, and execution state.
3. **Knowledge Base** (`libs/core/knowledge`): Processes files, splits chunks, computes embeddings, and executes RAG retrievals.
4. **CRM & Leads** (`libs/core/crm`): Tracks customer profiles, leads, pipelines, and user activity history.

## AI Agent Orchestration Flow

- **Primary Agent Driver**: **Google ADK** (Agent Development Kit). We use ADK for agent-to-agent collaboration and context compaction.
- **Workflow State Machine**: **LangGraph**. Graph-based state management handles complex CX flows, branching, and conditional loops.
- **LLM Gateway**: **LiteLLM Proxy**. All LLM requests route through LiteLLM using standard OpenAI-compatible requests, providing instant support for Gemini, Anthropic, Ollama, OpenAI, OpenRouter, and xAI with zero code changes.
