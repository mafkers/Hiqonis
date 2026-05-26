# ADR-002: Architecture Pattern Selection

## Status
Approved

## Context
Hiqonis is an open-source platform intended to grow from a solo-developed project to a massive enterprise deployment. We need an architectural style that keeps development velocity high while maintaining clean boundaries to support modular growth, scalability, and maintainability.

## Decision
We chose a **Modular Monolith** architecture utilizing **Domain-Driven Design (DDD)** and **Clean Architecture** patterns, coupled with an **Event-Driven** model.

1. **Modular Monolith**
   - *Rationale*: Microservices introduce huge operational complexity, network latency, and infrastructure costs. A modular monolith allows us to run everything in a single deployment artifact, reducing Hetzner/VPS monthly cost dramatically, while enforcing strict module boundaries.
2. **Domain-Driven Design (DDD)**
   - *Rationale*: Organizing code around business subdomains (Bounded Contexts) like Conversation Engine, Agent Manager, CRM, and Knowledge Base keeps the codebase highly understandable and maps logically to business requirements.
3. **Clean Architecture (Hexagonal)**
   - *Rationale*: We strictly separate the Domain (business logic) from Infrastructure (DB, HTTP routers, external APIs). The Domain has zero external dependencies, making it extremely easy to test and swap infrastructure components without modifying business logic.
4. **Event-Driven Communication**
   - *Rationale*: Modules communicate asynchronously via domain events (using Redis pub/sub or NATS), allowing decoupled processing (e.g. updating a lead stage in the CRM when a conversation tag is set).

## Consequences
- **Extensibility**: Adding new integrations (like Shopee or a payment gateway) in future phases requires writing simple adapters implementing standard domain interfaces, satisfying the Open-Closed Principle (OCP).
- **Scalability**: If a specific module (e.g., voice processing or document embeddings) becomes a bottleneck, it can easily be extracted into a separate service later, without rewrite.
- **Maintainability**: Clear architectural layers prevent spaghetti code, allowing AI coding assistants to write predictable and bug-free code.
