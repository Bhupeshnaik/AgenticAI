# Bank Marketing AI Platform

> Complete agentic AI application for UK bank marketing operations — 9 specialist AI agents covering all 8 phases of the marketing lifecycle, built entirely on Azure.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    React TypeScript Frontend                         │
│         Dashboard · Chat · Workflows · Analytics · Phases           │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ REST API
┌──────────────────────────────▼──────────────────────────────────────┐
│                    FastAPI Backend (Python)                          │
│                  Multi-Agent Orchestrator                            │
└──┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────────────┘
   │      │      │      │      │      │      │      │
   ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼      ▼
 Strat  Copy  Comp  Asset  Seg  Camp  Lead  Nurt  Analytics
  [1]   [2a]   [4]  [2b-f]  [3]   [5]   [6]   [7]    [8]
```

## 9 Specialist AI Agents

| Agent | Phase | Key Capability |
|---|---|---|
| **Strategy Agent** | Phase 1 | Annual planning, budget optimisation, campaign briefs |
| **Copywriting Agent** | Phase 2a | All-channel copy generation, A/B variants, APR calculations |
| **Asset Production Agent** | Phase 2b–2f | DAM management, 25–40 variant generation, PDF production |
| **Segmentation Agent** | Phase 3 | Audience building, GDPR suppressions, propensity scoring |
| **Compliance Agent** | Phase 4 | FCA COBS 4 review, Consumer Duty, compliance certificates |
| **Campaign Orchestration Agent** | Phase 5 | Multi-channel launch, frequency caps, health monitoring |
| **Lead Management Agent** | Phase 6 | AI scoring, smart routing, SLA management, RM alerts |
| **Nurture Agent** | Phase 7 | Personalised journeys, NBA engine, application rescue |
| **Analytics Agent** | Phase 8 | Multi-touch attribution, ROI analysis, budget recommendations |

## Azure Services Used

| Service | Purpose |
|---|---|
| **Azure OpenAI (GPT-4o)** | Agent intelligence — all 9 agents |
| **Azure AI Foundry** | Agent orchestration & management |
| **Azure Cosmos DB** | Campaigns, leads, assets, compliance records |
| **Azure Blob Storage** | Digital Asset Management (DAM) — 25–40 variants per campaign |
| **Azure AI Search** | Semantic search over assets, campaigns, FCA rules KB |
| **Azure Document Intelligence** | PDF document processing & extraction |
| **Azure Communication Services** | Email/SMS campaign delivery |
| **Azure Service Bus** | Asynchronous campaign & lead processing queues |
| **Azure Container Apps** | Backend (FastAPI) + Frontend (React/Nginx) hosting |
| **Azure Key Vault** | Secrets management |
| **Azure Monitor / App Insights** | Observability & logging |
| **Azure Event Grid** | Event-driven architecture for rate changes & expiry alerts |

## Quick Start

### Prerequisites
- Azure subscription with quota for GPT-4o
- Azure CLI + Bicep installed
- Docker + Docker Compose (for local dev)
- Node.js 22+ and Python 3.12+

### 1. Deploy Azure Infrastructure

```bash
az login
az group create --name rg-bank-marketing-ai --location uksouth

az deployment group create \
  --resource-group rg-bank-marketing-ai \
  --template-file infrastructure/main.bicep \
  --parameters @infrastructure/parameters.dev.json
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Azure resource values from the deployment outputs
```

### 3. Run Locally

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Visit: http://localhost:5173

### 4. Docker Compose

```bash
docker-compose up --build
```

### 5. Deploy to Azure Container Apps

After infrastructure deployment, build and push Docker images:

```bash
# Build and push
docker build -t your-registry/bank-marketing-backend:latest ./backend
docker build -t your-registry/bank-marketing-frontend:latest ./frontend
docker push your-registry/bank-marketing-backend:latest
docker push your-registry/bank-marketing-frontend:latest

# Update container app images
az containerapp update \
  --name bankmarketingai-backend-<suffix> \
  --resource-group rg-bank-marketing-ai \
  --image your-registry/bank-marketing-backend:latest
```

## Key API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/agents` | List all 9 agents with capabilities |
| POST | `/api/chat` | Chat with auto-routed or specific agent |
| POST | `/api/workflows/run` | Run multi-agent workflow |
| GET | `/api/campaigns` | List campaigns |
| POST | `/api/campaigns` | Create campaign via Strategy Agent |
| GET | `/api/leads` | List leads |
| POST | `/api/leads/capture` | Capture & score new lead |
| GET | `/api/compliance/records` | List compliance reviews |
| POST | `/api/compliance/review` | Submit content for FCA review |
| GET | `/api/analytics/overview` | Marketing performance overview |
| GET | `/api/dashboard` | Dashboard summary |
| GET | `/api/phases` | 8-phase lifecycle map |

## Multi-Agent Workflows

| Workflow | Agents | Description |
|---|---|---|
| `campaign_launch` | Strategy → Copy → Compliance → Segmentation | Phase 1–5 |
| `full_campaign` | All 9 agents | Complete end-to-end |
| `compliance_review` | Compliance | FCA review with certificate |
| `audience_build` | Segmentation | GDPR-compliant audience |
| `performance_review` | Analytics | ROI & attribution report |

## Business Impact (vs As-Is)

| Problem | As-Is | With AI |
|---|---|---|
| Compliance turnaround | 5–20 days | 1–4 days (AI pre-screening) |
| Planning cycle | 6–8 weeks | Hours |
| Asset production | 25–40 manual variants | Auto-generated manifest |
| Lead response (£5M commercial) | 24–72 hours | < 1 hour |
| Attribution | Last-touch only | Multi-touch + data-driven |
| Nurture conversion | 3.8% | 7.2% (+89%) |
| Application rescue | ~3% | 23% recovery rate |
