# ADR-001: Technology Stack Selection

## Status
Approved

## Context
We need to select a technology stack for building "Hiqonis", an enterprise-grade, open-source AI Agent platform for customer experience (CX). The system must be highly efficient, developer-friendly for AI coding, scalable, and avoid vendor lock-in.

## Decision
We chose the following unified tech stack:

1. **Backend Programming Language**: Python 3.12+
   - *Rationale*: Python is the industry standard for AI/ML engineering. Key agent orchestration libraries (Google ADK, LangGraph, LangChain) are Python-first. Large LLM code bases make AI coding assistants extremely accurate when writing Python.
2. **Backend Web Framework**: FastAPI
   - *Rationale*: Modern, high performance (async), type-safe (Pydantic), and provides automatic OpenAPI docs.
3. **AI Agent Orchestration**: Google ADK (A2A protocol) + LangGraph (complex graph workflows) + LiteLLM Proxy.
   - *Rationale*: Google ADK offers lightweight agent-to-agent collaboration and event compaction to reduce token costs. LangGraph handles complex loops and human-in-the-loop takeover. LiteLLM acts as a unified OpenAI-compatible LLM Gateway to prevent vendor lock-in.
4. **Frontend Stack**: TypeScript 5.x + Next.js 15+ (App Router) + Tailwind CSS 4 + shadcn/ui + next-intl.
   - *Rationale*: Next.js offers superior SSR/SSG capabilities and React Server Components. shadcn/ui provides clean, customizable Radix primitives. next-intl handles dual-language support (ID + EN) seamlessly.
5. **Database & Storage**: PostgreSQL 16+ (with pgvector), Redis 7+, MinIO (S3-compatible).
   - *Rationale*: Postgres handles core relational structures and vector search via pgvector for KB retrieval. Redis handles caching and async queue tasks. MinIO acts as self-hosted object storage.

## Consequences
- **Developer Productivity**: Leveraging Python and TypeScript maximizes the efficiency of AI-native code generation.
- **Lock-in Prevention**: Swapping LLM providers requires zero code changes due to LiteLLM integration.
- **Portability**: The entire infrastructure can run fully containerized within a single Docker compose setup for easy self-hosting.
