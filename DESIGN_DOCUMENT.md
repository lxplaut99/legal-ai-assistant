# GenAI Assistant for Lawyers — Design Document

## Table of Contents

1. [Product Vision](#1-product-vision)
2. [Market Landscape & Competitive Analysis](#2-market-landscape--competitive-analysis)
3. [Capability Requirements](#3-capability-requirements)
4. [System Architecture](#4-system-architecture)
5. [Core Technical Components](#5-core-technical-components)
6. [Model Strategy](#6-model-strategy)
7. [Modular Practice Area Design](#7-modular-practice-area-design)
8. [Data Strategy](#8-data-strategy)
9. [Security & Compliance](#9-security--compliance)
10. [Development Roadmap](#10-development-roadmap)
11. [References & Resources](#11-references--resources)

---

## 1. Product Vision

An agentic AI assistant purpose-built for legal professionals. The system performs tasks a lawyer would normally do — research, document review, drafting, analysis, and workflow management — while keeping the lawyer in the loop for judgment calls, strategy, and client relationships.

### Design Principles

- **Human-in-the-loop**: AI drafts and recommends; lawyers approve and refine. Critical actions always require human sign-off.
- **Citation grounding**: Every output is traceable to source documents. No hallucinated citations.
- **Modular by practice area**: Shared core capabilities (research, drafting, deadlines) with pluggable specializations per practice area.
- **Data flywheel**: Every interaction improves the system — feedback collection, clause benchmarking, and workflow optimization compound over time.
- **Start narrow, expand deliberately**: Prove one practice area before generalizing.

---

## 2. Market Landscape & Competitive Analysis

### Harvey — The Platform Play

- **Valuation**: ~$8B+ (Series F, Dec 2025). 1,000+ customers in 59 countries.
- **Founded**: 2022 by Winston Weinberg (ex-Meta ML) and Gabriel Pereyra (ex-DeepMind).
- **Approach**: Engineering-first. Started with a legal chat interface on early GPT-4 access, iterated embedded with Allen & Overy, expanded to a multi-product platform.
- **Architecture**: Multi-model (OpenAI primary, also Claude, possibly Google). Custom fine-tuning via RLHF with lawyer feedback. Enterprise RAG with citation grounding. Orchestrates "hundreds of specialized models" for different subtasks.
- **Key products**: Harvey Assistant (chat), Vault (10K+ file review), Workflow Builder (no-code custom workflows).
- **Target market**: BigLaw, enterprise in-house teams. AmLaw 100 firms.
- **Lesson**: Started with the model layer, then built up to workflows. Deep model provider partnerships were a key early advantage.

**References:**
- [Harvey AI](https://www.harvey.ai/)
- [Harvey AI Review 2025 — Purple Law](https://purple.law/blog/harvey-ai-review-2025/)
- [Harvey Wikipedia](https://en.wikipedia.org/wiki/Harvey_(software))

### Legora (formerly Leya) — The Legal Workspace

- **Funding**: ~$35-40M, Series A led by Benchmark.
- **Founded**: 2023 in Stockholm by Jonathan Berggard and Simon Jalden.
- **Approach**: Product-led, domain-focused. Started with document Q&A in the Nordic market, added Tabular Review as the killer feature, then expanded to UK/US.
- **Architecture**: Multi-model, multi-provider — Claude Sonnet 4 as primary reasoning engine (18% higher on their legal eval set), plus GPT-4o and GPT-o1 via Azure OpenAI. Hybrid retrieval (semantic + keyword). "Tens of thousands of parallel calls" for document extraction. Multi-agentic behavior for complex queries.
- **Key products**: Assistant (Q&A with citations), Tabular Review (structured extraction across hundreds of docs), Agentic Workflows, EDGAR integration, SharePoint/Word integration.
- **Target market**: Large law firms across Europe and US (A&O Shearman, Vinge, Mannheimer Swartling).
- **Lesson**: One killer feature (Tabular Review) solved acute pain in due diligence. Structured output at scale is what lawyers actually need, not just free-text answers.

**References:**
- [Legora](https://legora.com/)
- [Legora — Anthropic Customer Story](https://claude.com/customers/legora)
- [Legora — Microsoft Azure Customer Story](https://www.microsoft.com/en/customers/story/23171-legora-azure-openai)
- [Legora on Y Combinator](https://www.ycombinator.com/companies/legora)

### Crosby — The AI-Native Law Firm

- **Funding**: $20M Series A from Sequoia and Bain Capital Ventures.
- **Founded**: 2024 by Ryan Daniels (Stanford-trained lawyer, former startup GC) and John Sarihan (early Ramp engineer).
- **Approach**: Service-first. Operates as an actual law firm — uses AI internally to deliver legal services, not selling software to lawyers. "You can't automate what you don't deeply understand."
- **Architecture**: Human-in-the-loop by design. AI agents do initial contract review and redlining, lawyers verify. "Bailiff" triage system routes contracts by priority. Proprietary data flywheel — captures clause benchmarking data across every negotiation.
- **Key insight**: Semantic embeddings miss critical legal nuance ("commercially reasonable" vs. "reasonable" appear identical in embedding space but have vastly different legal implications).
- **Scope**: Narrow — MSAs, NDAs, DPAs only. Volume-based pricing (per contract), not billable hours.
- **Customers**: Cursor, Clay, UnifyGTM, Cartesia, Alloy, Overjet.
- **Lesson**: Operating the service teaches you what to automate. The data flywheel from actual contract negotiations creates a compounding moat.

**References:**
- [Bain Capital on Crosby](https://baincapitalventures.com/insight/crosby-is-redefining-legal-work-with-ai-powered-contract-automation/)
- [Sequoia on Crosby](https://inferencebysequoia.substack.com/p/deal-velocity-not-billable-hours)
- [Crosby AI — eesel.ai](https://www.eesel.ai/blog/crosby-ai)
- [TechCrunch — Crosby Launch](https://techcrunch.com/2025/06/17/sequoia-backed-crosby-launches-a-new-kind-of-ai-powered-law-firm/)

### Competitive Gaps / Opportunities

| Gap | Detail |
|---|---|
| **Practice area depth** | Harvey and Legora go broad. Deep niche ownership (immigration, family law, criminal defense, employment) is underserved. |
| **Market segment** | Both target BigLaw/enterprise. Solo practitioners and small firms (the majority of lawyers) are underserved. |
| **Geographic specialization** | Jurisdiction-specific deep expertise (state court rules, local procedures) is not a focus for any competitor. |
| **Service model** | Crosby proved the AI-native law firm model works. Most competitors sell software. |

---

## 3. Capability Requirements

### What Lawyers Actually Do (by category)

Workflows vary significantly by practice area. The system must be modular enough to support different workflows while sharing common infrastructure.

#### Research & Analysis
- Legal research (case law, statutes, regulations)
- Fact investigation and gathering
- Analyzing opposing counsel's arguments
- Regulatory compliance analysis
- Comparative law across jurisdictions

#### Document Work
- Drafting (contracts, pleadings, briefs, wills, corporate filings)
- Document review and due diligence
- Redlining and negotiating contract terms
- Proofreading and citation checking
- Summarizing depositions and transcripts

#### Strategy & Reasoning
- Case strategy and theory development
- Risk assessment and exposure analysis
- Settlement valuation and negotiation strategy
- Identifying weaknesses in your own case
- Predicting likely outcomes based on precedent

#### Client Management
- Client intake and conflict checks
- Explaining legal concepts in plain language
- Managing client expectations
- Status updates and communication drafting
- Billing and time tracking

#### Court & Procedural
- Calendar/deadline management (filing deadlines, statutes of limitations)
- Court rule compliance (formatting, page limits, local rules)
- Discovery management (interrogatories, document requests, privilege review)
- E-discovery and document production
- Witness preparation materials

#### Communication & Negotiation
- Demand letters, settlement offers
- Negotiation strategy and preparation
- Mediation/arbitration preparation
- Opposing counsel correspondence

#### Administrative
- Conflict of interest checks
- Knowledge management (internal precedent banks)
- New client/matter onboarding

### What Can Be Automated vs. What Stays Human

| Automatable | Human-essential |
|---|---|
| Document review and extraction | Final judgment and strategy |
| Legal research and citation | Client relationship and trust |
| First drafts of documents | Court appearances |
| Deadline computation | Ethical decision-making |
| Conflict checks | Negotiation (in-person) |
| Summarization and analysis | Witness credibility assessment |
| Compliance checklists | Novel legal argumentation |
| Routine correspondence | Client counseling |

---

## 4. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐   │
│  │  Web App  │  │  Word    │  │  Slack   │  │  Email        │   │
│  │  (React)  │  │  Plugin  │  │  Bot     │  │  Integration  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬────────┘   │
└───────┼──────────────┼─────────────┼───────────────┼────────────┘
        │              │             │               │
        ▼              ▼             ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API GATEWAY                              │
│           Authentication · Rate Limiting · Routing              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                          │
│                                                                 │
│  ┌────────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │  Agent Router   │  │  Task Planner │  │  Workflow Engine   │  │
│  │  (routes to     │  │  (decomposes  │  │  (multi-step      │  │
│  │   practice-area │  │   complex     │  │   execution with  │  │
│  │   specialists)  │  │   requests)   │  │   human checkpts) │  │
│  └────────┬───────┘  └──────┬───────┘  └────────┬───────────┘  │
└───────────┼─────────────────┼────────────────────┼──────────────┘
            │                 │                    │
            ▼                 ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CAPABILITY LAYER                           │
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │ Research  │ │ Document │ │ Drafting │ │ Analysis /       │   │
│  │ Engine   │ │ Review   │ │ Engine   │ │ Reasoning        │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────────┬─────────┘   │
│       │             │            │                │             │
│  ┌────┴─────┐ ┌─────┴────┐ ┌────┴─────┐ ┌───────┴──────────┐  │
│  │ Deadline │ │ Citation │ │ Conflict │ │ Tabular          │  │
│  │ Tracker  │ │ Checker  │ │ Checker  │ │ Extraction       │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PRACTICE AREA MODULES                         │
│                   (Pluggable Specializations)                   │
│                                                                 │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────────┐   │
│  │ Litigation│ │ Corporate │ │Immigration│ │  [Future]     │   │
│  │ Module    │ │ Module    │ │ Module    │ │  Modules      │   │
│  └───────────┘ └───────────┘ └───────────┘ └───────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INTELLIGENCE LAYER                           │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Model Router     │  │  RAG Pipeline │  │  Feedback Loop  │  │
│  │  (selects best    │  │  (retrieval + │  │  (collects      │  │
│  │   model per task) │  │   grounding)  │  │   preferences)  │  │
│  └──────────────────┘  └──────────────┘  └──────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  LLM Providers                                           │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                  │   │
│  │  │ Claude  │  │ GPT-4o  │  │ Future  │                  │   │
│  │  │ (primary│  │ (backup/│  │ models  │                  │   │
│  │  │  reason)│  │  tasks) │  │         │                  │   │
│  │  └─────────┘  └─────────┘  └─────────┘                  │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │PostgreSQL│ │ Vector   │ │ Object   │ │ Document         │   │
│  │(users,   │ │ DB       │ │ Storage  │ │ Processing       │   │
│  │ matters, │ │(pgvector │ │ (S3 —    │ │ Pipeline         │   │
│  │ history) │ │ embeddings│ │  files)  │ │ (parse, chunk,   │   │
│  └──────────┘ └──────────┘ └──────────┘ │  embed)          │   │
│                                          └──────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Multi-model | Yes — Claude primary, GPT-4o secondary | Legora showed 18% performance variance across models on legal tasks. Route to best model per task. Avoid vendor lock-in. |
| RAG approach | Hybrid (semantic + keyword) | Crosby showed pure semantic embeddings miss legal nuance. Keyword search catches precise legal terms. |
| Agent framework | Custom orchestration | Legal workflows are too domain-specific for generic frameworks. Build task decomposition and routing tailored to legal tasks. |
| Human-in-the-loop | Required for all outputs | Every competitor learned this. AI assists, lawyers decide. |
| Practice area modules | Pluggable | Shared core + practice-specific tools, prompts, data sources, and workflows. |

---

## 5. Core Technical Components

### 5.1 RAG Pipeline (Retrieval-Augmented Generation)

RAG grounds the LLM's responses in actual documents rather than training data, eliminating hallucinated citations and enabling work with private/confidential data.

```
Document Ingestion → Chunking → Embedding → Vector Storage → Retrieval → Generation

1. INGEST:   Parse PDF/DOCX/HTML into text (handle OCR for scans)
2. CHUNK:    Split into semantically meaningful segments
             (respect section boundaries, not arbitrary character limits)
3. EMBED:    Convert chunks to vectors using embedding model
4. STORE:    Index in vector database with metadata
             (document type, jurisdiction, date, client, matter)
5. RETRIEVE: At query time, find relevant chunks via hybrid search
             (semantic similarity + keyword matching + metadata filters)
6. GENERATE: Feed retrieved chunks as context to the LLM
             with instructions to cite sources
```

#### Legal-Specific RAG Considerations

- **Chunk boundaries matter**: Legal documents have defined structure (sections, clauses, definitions). Chunk at structural boundaries, not arbitrary token counts.
- **Cross-reference handling**: Legal documents reference other sections internally ("as defined in Section 2.3"). The chunking strategy must preserve or link these references.
- **Definitions sections**: Many contracts have a definitions section that's needed to understand any other clause. Always include relevant definitions in the context.
- **Temporal awareness**: Laws change. The retrieval system must understand which version of a statute or regulation applies.
- **Hybrid search is essential**: Pure semantic search misses precise legal terms. "Commercially reasonable" and "reasonable" are semantically similar but legally distinct. Keyword matching catches these differences.

#### Technical Stack

| Component | Recommended | Alternatives |
|---|---|---|
| Document parsing | Docling, Unstructured | PyMuPDF, pdfplumber |
| OCR | Tesseract, AWS Textract | Google Document AI |
| Embeddings | Voyage AI (legal-optimized), OpenAI embeddings | Cohere embed |
| Vector DB | pgvector (start), Pinecone (scale) | Weaviate, Qdrant |
| Keyword search | Elasticsearch or PostgreSQL full-text | Typesense |

### 5.2 Agent Orchestration

The orchestration layer decomposes complex legal tasks into subtasks, routes them to appropriate tools/models, and assembles results.

```
User Request: "Review these 50 vendor contracts and flag any non-standard indemnification clauses"

Agent Planner decomposes into:
├── For each contract (parallelized):
│   ├── Parse document
│   ├── Extract indemnification clauses (RAG + extraction prompt)
│   ├── Compare against standard market terms (benchmark data)
│   └── Flag deviations with severity score
├── Aggregate results into summary table
├── Generate executive summary of key findings
└── Present to lawyer for review with citations to source docs
```

#### Agent Design Patterns

1. **Router Agent**: Classifies the request and routes to the appropriate specialist agent or workflow.
2. **Planner Agent**: Decomposes complex requests into ordered subtasks with dependencies.
3. **Executor Agents**: Specialized agents for specific tasks (research, extraction, drafting, analysis).
4. **Reviewer Agent**: Checks outputs for quality, citation accuracy, and completeness before presenting to the user.

### 5.3 Document Processing Pipeline

```
Input (PDF, DOCX, scan, email)
    │
    ▼
┌─────────────────┐
│  File Detection  │ ← Determine file type, encoding, quality
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  OCR (if needed) │ ← Scanned documents, images
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Structure       │ ← Detect sections, headings, tables,
│  Extraction      │   lists, signature blocks, exhibits
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Metadata        │ ← Document type, date, parties,
│  Extraction      │   jurisdiction, governing law
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Chunking &      │ ← Segment by structure, preserve
│  Embedding       │   cross-references, embed
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Index & Store   │ ← Vector DB + metadata store + file store
└─────────────────┘
```

### 5.4 Citation System

Every output must include verifiable citations. This is architecturally enforced, not optional.

```
LLM Output:
"The MSA permits termination for convenience with 30 days notice. [1]
However, the liability cap is unusually low at $50,000. [2]"

Citations:
[1] Vendor_MSA_v3.pdf, Section 8.2 (Termination), page 12
[2] Vendor_MSA_v3.pdf, Section 9.1 (Limitation of Liability), page 14

Each citation links to:
- Source document
- Specific section/clause
- Page number
- Highlighted text passage
```

Implementation:
- Retrieved chunks carry source metadata through the entire pipeline.
- The LLM is instructed (via system prompt) to cite chunk IDs in its response.
- Post-processing maps chunk IDs back to document locations.
- The UI renders citations as clickable links to source documents.

### 5.5 Feedback Collection System

Every interaction is an opportunity to collect training data for future model improvement.

```
Lawyer interacts with output:
├── 👍 / 👎 rating
├── Edits to generated text (implicit preference signal)
├── Selected vs. rejected alternative outputs
├── Corrections to citations
└── Comments on quality

Data stored as:
{
  "query": "...",
  "context_retrieved": ["chunk_1", "chunk_2", ...],
  "model_output": "...",
  "lawyer_rating": "positive" | "negative",
  "lawyer_edits": "...",  // what they changed
  "practice_area": "litigation",
  "task_type": "contract_review",
  "timestamp": "..."
}

Future use:
- Prompt improvement (analyze what queries get bad ratings)
- Fine-tuning data (preference pairs for DPO)
- Retrieval improvement (which chunks were actually useful)
- Benchmark dataset (known-good Q&A pairs)
```

---

## 6. Model Strategy

### The Training Spectrum (What applies to us vs. model providers)

```
Model Providers Handle:              We Handle:
─────────────────────                ──────────
Pre-training                         Prompt Engineering
   └─ Learn language                    └─ System prompts, few-shot examples
RLHF                                 RAG
   └─ Learn to follow instructions      └─ Ground in specific documents
Safety training                      Feedback collection
   └─ Refuse harmful outputs            └─ Lawyer ratings and edits
General capability                   Lightweight fine-tuning (later)
                                        └─ Via provider APIs, using collected data
                                     Evaluation
                                        └─ Legal benchmarks, lawyer-scored outputs
```

### Why We Don't Need Fine-Tuning (Yet)

1. **Base models are already excellent** at legal reasoning. Claude Sonnet 4 scores highly on legal benchmarks out of the box.
2. **Prompting + RAG gets 90%+ of the benefit** without any training cost.
3. **Fine-tuning risks "catastrophic forgetting"** — the model gets better at legal tasks but worse at general capabilities.
4. **We don't have training data yet.** Fine-tuning requires curated examples. Build the product first, collect data, fine-tune later.

### When to Consider Fine-Tuning

- When we have 5,000+ rated interactions from lawyers
- When we've identified specific failure modes that prompting can't fix
- When we need firm-specific style/tone that system prompts can't reliably produce
- Use provider fine-tuning APIs (not training from scratch)
- Consider DPO (Direct Preference Optimization) over full RLHF — simpler, no reward model needed, just preference pairs

### Model Routing Strategy

Different tasks have different optimal models:

| Task | Model Choice | Rationale |
|---|---|---|
| Complex legal reasoning | Claude Opus / Sonnet | Best instruction-following and reasoning |
| Simple extraction | Claude Haiku / GPT-4o-mini | Fast and cheap for structured extraction |
| Document summarization | Claude Sonnet | Good balance of quality and speed |
| Embeddings | Voyage AI or OpenAI embeddings | Purpose-built for semantic search |
| Citation verification | Claude Sonnet | Needs precision and faithfulness |

---

## 7. Modular Practice Area Design

### Shared Core (All Practice Areas)

Every practice area module builds on shared capabilities:

- **Document ingestion & RAG pipeline**
- **Citation system**
- **Drafting engine** (with configurable templates/styles)
- **Deadline/calendar management**
- **Conflict checking**
- **Feedback collection**
- **Chat/Q&A interface**

### Practice Area Module Structure

Each module contributes:

```
practice_area_module/
├── prompts/              # System prompts tuned for this practice area
├── tools/                # Practice-specific tools (e.g., sentencing calculator)
├── workflows/            # Multi-step workflows (e.g., due diligence checklist)
├── data_sources/         # Connectors to relevant databases
├── templates/            # Document templates (motions, contracts, etc.)
├── evaluation/           # Practice-specific eval benchmarks
└── config.yaml           # Practice area metadata, default settings
```

### Practice Area Comparison

| Practice Area | Key Workflows | Primary Data Sources | Automation Potential |
|---|---|---|---|
| **Litigation** | Discovery review, motion drafting, case research, deposition summaries | CourtListener, state court DBs, Westlaw/Lexis | High (doc review) |
| **Corporate / M&A** | Due diligence, contract drafting, deal analysis, closing checklists | EDGAR/SEC, deal databases | High (due diligence) |
| **Immigration** | Form preparation, eligibility analysis, case tracking, country conditions | USCIS, State Dept, country reports | Very high (form-driven) |
| **Real Estate** | Title search, lease review, closing docs, zoning research | County records, MLS, title databases | High (repetitive docs) |
| **Employment** | Policy drafting, compliance audit, investigation summaries | DOL, EEOC, state labor agencies | High (compliance) |
| **Criminal Defense** | Evidence review, sentencing guidelines, motion drafting | Court records, sentencing DBs, forensic data | Medium (judgment-heavy) |
| **Family Law** | Asset division, support calculations, custody arrangements | State family code, financial disclosures | Medium-high (calculable) |
| **IP** | Prior art search, application drafting, infringement analysis | USPTO, EPO, patent databases | Medium (specialized) |

### Recommended First Practice Area

**Decision criteria:**
1. Availability of public data sources
2. Structured/repeatable workflows (easier to automate reliably)
3. Market opportunity and willingness to pay
4. Access to domain expert feedback

**TBD** — Pending decision on target market, user access, and domain expertise. See [Development Roadmap](#10-development-roadmap).

---

## 8. Data Strategy

### Data Sources by Category

#### Public Legal Data (Free)
- **CourtListener / RECAP**: Federal court filings, opinions
- **US Code / CFR / Federal Register**: Statutes and regulations
- **EDGAR / SEC**: Public company filings (10-K, 10-Q, 8-K, proxy statements)
- **State court databases**: Vary by state, many are publicly accessible
- **USPTO / EPO**: Patent databases
- **USCIS**: Immigration forms, policy manuals

#### Commercial Legal Data (Paid)
- **Westlaw (Thomson Reuters)**: Case law, statutes, secondary sources
- **LexisNexis (RELX)**: Case law, statutes, news, public records
- **Casetext (Thomson Reuters)**: AI-powered legal research (acquired 2023)
- **Fastcase / vLex**: More affordable legal research alternatives

#### User-Provided Data (Per Client)
- Uploaded documents (contracts, filings, correspondence)
- Firm knowledge bases (precedent, templates, memos)
- Client matter data

### Data Flywheel

```
Users submit documents and queries
        ↓
System processes and responds
        ↓
Lawyers rate, edit, and correct outputs
        ↓
Feedback data improves:
├── Prompt quality (analyze failure patterns)
├── Retrieval relevance (which chunks helped)
├── Benchmarking data (clause terms across contracts)
└── Training data (for future fine-tuning)
        ↓
Better outputs → more usage → more feedback → compounding improvement
```

This is the Crosby insight — every contract reviewed builds proprietary benchmarking data. Terms across contracts become a navigable dataset. This creates a defensible moat over time.

---

## 9. Security & Compliance

### Non-Negotiable Requirements

Legal AI has the highest security bar of any vertical. Attorney-client privilege and professional responsibility rules make these requirements absolute.

| Requirement | Implementation |
|---|---|
| **Data isolation** | Complete tenant isolation. Firm A's data is never accessible to Firm B, never used in responses to Firm B, never used for training. |
| **Encryption** | At rest (AES-256) and in transit (TLS 1.3). |
| **SOC 2 Type II** | Required for enterprise law firm adoption. Plan for this from day one. |
| **No training on client data** | Client documents are used only for RAG retrieval within that client's session. Never for model training or improvement without explicit consent. |
| **Audit trail** | Every action, query, retrieval, and response is logged with timestamps. Lawyers are ethically responsible for AI output and need to verify. |
| **Access controls** | Role-based access. Matter-level permissions. Conflict walls (ethical screens between matters). |
| **Data residency** | Ability to keep data in specific geographic regions (required for some jurisdictions and clients). |
| **Right to delete** | Full data deletion capability when a matter concludes or client requests it. |

### Ethical Guardrails

- **Not legal advice**: The system assists licensed attorneys. It does not provide legal advice directly to non-lawyers (unauthorized practice of law).
- **Confidence indicators**: When the system is uncertain, it must say so. Lawyers need to know when to verify more carefully.
- **Scope boundaries**: The system should refuse to perform tasks outside its competence rather than attempt them poorly.

---

## 10. Development Roadmap

### Phase 0: Foundation (Weeks 1-4)

**Goal**: Get the core infrastructure running with one end-to-end workflow.

- [ ] Set up project scaffolding (backend API, frontend, database)
- [ ] Implement document ingestion pipeline (PDF/DOCX parsing, chunking)
- [ ] Set up vector database (pgvector) and embedding pipeline
- [ ] Build basic RAG pipeline with citation grounding
- [ ] Build chat interface with document upload
- [ ] Integrate Claude API as primary LLM
- [ ] Implement basic authentication and data isolation

**Stack:**
```
Frontend:    Next.js + React
Backend:     Python (FastAPI)
Database:    PostgreSQL + pgvector
LLM:         Claude API (Anthropic)
Storage:     S3-compatible (document storage)
Auth:        NextAuth or Clerk
Deployment:  Docker → AWS/GCP
```

### Phase 1: First Practice Area (Weeks 5-12)

**Goal**: Build a complete, usable product for one practice area.

- [ ] Select target practice area (pending decision)
- [ ] Build practice-area-specific prompts and workflows
- [ ] Integrate relevant public data sources
- [ ] Build document drafting with templates
- [ ] Implement tabular extraction (Legora's key insight)
- [ ] Add feedback collection (ratings, edits)
- [ ] Build evaluation benchmark for the practice area
- [ ] Alpha testing with 2-3 lawyers

### Phase 2: Refinement & Scale (Weeks 13-20)

**Goal**: Production-ready for first paying users.

- [ ] Improve retrieval quality based on alpha feedback
- [ ] Add multi-model routing (Claude + GPT-4o for different tasks)
- [ ] Build workflow builder (configurable multi-step workflows)
- [ ] Implement deadline/calendar management
- [ ] Add Word/email integration
- [ ] SOC 2 preparation
- [ ] Performance optimization (parallelization of document processing)
- [ ] Beta launch with 10-20 users

### Phase 3: Expansion (Weeks 21+)

**Goal**: Add practice areas, collect data, begin model improvement.

- [ ] Add second practice area module
- [ ] Implement data flywheel (clause benchmarking, pattern analysis)
- [ ] Use collected feedback data for prompt improvement
- [ ] Evaluate fine-tuning (if 5K+ rated interactions)
- [ ] Build conflict checking system
- [ ] Add collaborative features (team workspaces, matter management)
- [ ] Third practice area module

---

## 11. References & Resources

### Competitor Research

| Company | URL | Key Reference |
|---|---|---|
| Harvey AI | [harvey.ai](https://www.harvey.ai/) | [Harvey Wikipedia](https://en.wikipedia.org/wiki/Harvey_(software)) |
| Legora | [legora.com](https://legora.com/) | [Anthropic Customer Story](https://claude.com/customers/legora), [Microsoft Customer Story](https://www.microsoft.com/en/customers/story/23171-legora-azure-openai) |
| Crosby | [crosby.ai](https://crosby.ai/) | [Sequoia Spotlight](https://inferencebysequoia.substack.com/p/deal-velocity-not-billable-hours), [Bain Capital](https://baincapitalventures.com/insight/crosby-is-redefining-legal-work-with-ai-powered-contract-automation/) |

### Technical References

| Topic | Resource |
|---|---|
| RAG | [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (Lewis et al., 2020)](https://arxiv.org/abs/2005.11401) |
| Legal AI Benchmarks | [LegalBench: A Collaboratively Built Benchmark for Measuring Legal Reasoning](https://arxiv.org/abs/2308.11462) |
| DPO | [Direct Preference Optimization: Your Language Model is Secretly a Reward Model (Rafailov et al., 2023)](https://arxiv.org/abs/2305.18290) |
| RLHF | [Training language models to follow instructions with human feedback (Ouyang et al., 2022)](https://arxiv.org/abs/2203.02155) |
| Claude Tool Use | [Anthropic Tool Use Documentation](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview) |
| Agentic Patterns | [Anthropic: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) |

### Legal Data Sources

| Source | URL | Content |
|---|---|---|
| CourtListener | [courtlistener.com](https://www.courtlistener.com/) | Federal court opinions, oral arguments |
| RECAP | [free.law/recap](https://free.law/recap) | Federal court filings (PACER mirror) |
| EDGAR | [sec.gov/edgar](https://www.sec.gov/edgar/searchedgar/companysearch) | SEC public company filings |
| US Code | [uscode.house.gov](https://uscode.house.gov/) | Federal statutes |
| CFR | [ecfr.gov](https://www.ecfr.gov/) | Federal regulations |
| Federal Register | [federalregister.gov](https://www.federalregister.gov/) | Proposed and final rules |
| USPTO | [patft.uspto.gov](https://patft.uspto.gov/) | Patents |
| USCIS | [uscis.gov](https://www.uscis.gov/) | Immigration forms, policy manual |

---

*Document version: 1.0*
*Last updated: 2026-02-15*
*Status: Draft — pending practice area selection*
