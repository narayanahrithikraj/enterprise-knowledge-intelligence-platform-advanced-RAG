# 🛡️ Enterprise Knowledge Intelligence Platform (Advanced RAG)

An enterprise-grade, production-ready Advanced Retrieval-Augmented Generation (RAG) ecosystem built with a completely decoupled microservices architecture. The platform combines a high-performance **Python FastAPI backend** orchestrated via **LangGraph agentic reasoning layers**, and a responsive, interactive **Streamlit frontend** secured by a cloud-persistent **Neon PostgreSQL** database cluster.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://advanced-rag-intelligence.streamlit.app)
[![FastAPI Backend](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=FastAPI&logoColor=white)](https://enterprise-rag-backend-fhzm.onrender.com)
[![Database: Neon PostgreSQL](https://img.shields.io/badge/Database-Neon_PostgreSQL-00e599?style=flat&logo=postgresql&logoColor=white)](https://neon.tech)

---

## ⚡ Core Architectural Milestones & Features

### 🧠 Agentic RAG & Contextual Grounding Core
* **LangGraph Orchestration:** Utilizes state-machine graphs to power structured, multi-turn dialogue agents with state memory.
* **Hallucination Mitigation:** Enforces rigid vector-space grounding boundaries; answers are strictly anchored to verified document contexts.
* **Hybrid Search Foundations:** Tracks text alignment across index mappings, matching specialized document contexts (SOPs, technical matrices) while generating automated source citation strings.

### 🛡️ Hardened Enterprise Access Governance (RBAC)
* **Clearance Isolation:** Segregates application layers completely into structured `User` and `Admin` permissions workspaces.
* **Cryptographic Token Provisioning:** Includes an administrative verification workflow utilizing live, single-use, cryptographically generated token strings for secure new administrator sign-ups.
* **Executive Console Overrides:** Powers privileged administrative root mutations, providing live user account revocation matrices and targeted database password override fields.

### 🗄️ Resilient Lifespan Cluster Data Layers
* **Neon Cloud Synchronization:** Fully integrated with a serverless cloud PostgreSQL database cluster, ensuring robust relational data storage and complete defense against ephemeral cloud server resets.
* **Race Condition Eradication:** Developed using modern FastAPI asynchronous lifespan context controllers to ensure the platform conducts patient connection pools and schema creation sequences without falling back prematurely to transient files.
* **Memory-Decoupled Processing:** Ingests documents, session records, and vector properties straight into live SQL tables, eliminating local file storage footprints.

### 📊 System Telemetry & Analytical Visibility
* **Knowledge Gap Intelligence:** Automatically flags and stores ungrounded client inputs, providing administrators with clean metadata tables detailing specific operational information deficits.
* **Visual Telemetry Dashboarding:** Connects analytical API metrics to frontend Plotly Express modules, rendering line performance distributions and file allocation pie chart tracking arrays.

---

## 🏗️ System Execution Blueprint

```text
    ┌─────────────────────────┐               ┌────────────────────────┐
    │    Streamlit UI         │  REST HTTP    │    FastAPI Backend     │
    │  (Frontend Web App)    ├──────────────►│    (API Core Hub)      │
    └───────────┬─────────────┘   Payloads    └───────────┬────────────┘
                │                                         │
                ▼                                         ▼
     Custom CSS UI Injection                    LangGraph Agentic Core
     JavaScript Field Validator                 Enterprise Guardrail Hooks
                │                                         │
                └───────────────► 💾 ◄────────────────────┘
                          Neon PostgreSQL Cloud
                        (Persistent Database Vault)
