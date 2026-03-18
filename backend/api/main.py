"""
FastAPI backend for the Bank Marketing AI Platform.
Exposes REST endpoints for the React frontend.
"""

import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from config.settings import settings
from orchestrator.orchestrator import orchestrator, AGENT_REGISTRY, PHASE_AGENT_MAP
from tools.azure_cosmos_tools import (
    list_campaigns, get_campaign, update_campaign_status,
    list_leads, get_lead, list_assets, list_compliance_records,
)

logging.basicConfig(level=getattr(logging, settings.log_level, logging.INFO))
logger = logging.getLogger(__name__)


# ─── Pydantic Models ──────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    agent_name: Optional[str] = None
    context: Optional[dict] = None


class WorkflowRequest(BaseModel):
    workflow_name: str
    data: dict
    session_id: Optional[str] = None


class CampaignCreateRequest(BaseModel):
    campaign_name: str
    product: str
    objective: str
    target_segment: str
    budget: float
    channels: list[str]
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class LeadCaptureRequest(BaseModel):
    source_channel: str
    product_interest: str
    intent_signal: str
    customer_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    estimated_value: Optional[float] = None
    campaign_id: Optional[str] = None


# ─── App Setup ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Bank Marketing AI Platform starting up...")
    logger.info("Registered agents: %s", list(AGENT_REGISTRY.keys()))
    yield
    logger.info("Bank Marketing AI Platform shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Agentic AI platform for UK bank marketing operations — 9 specialist AI agents covering all 8 phases of the marketing lifecycle.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health Check ──────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agents_available": list(AGENT_REGISTRY.keys()),
        "azure_openai_configured": bool(settings.azure_openai_endpoint),
    }


# ─── Agent Endpoints ───────────────────────────────────────────────────────────

@app.get("/api/agents")
async def list_agents():
    """Get all available agents with their capabilities."""
    capabilities = orchestrator.get_all_agent_capabilities()
    return {"agents": capabilities, "total": len(capabilities)}


@app.get("/api/agents/{agent_name}")
async def get_agent(agent_name: str):
    """Get a specific agent's capabilities."""
    if agent_name not in AGENT_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found. Available: {list(AGENT_REGISTRY.keys())}")
    from agents import (StrategyAgent, CopywritingAgent, ComplianceAgent, AssetProductionAgent,
                        SegmentationAgent, CampaignOrchestrationAgent, LeadManagementAgent,
                        NurtureAgent, AnalyticsAgent)
    agent_map = {
        "strategy": StrategyAgent, "copywriting": CopywritingAgent, "compliance": ComplianceAgent,
        "asset": AssetProductionAgent, "segmentation": SegmentationAgent,
        "campaign": CampaignOrchestrationAgent, "lead": LeadManagementAgent,
        "nurture": NurtureAgent, "analytics": AnalyticsAgent,
    }
    agent = agent_map[agent_name]()
    return agent.get_capabilities()


# ─── Chat / Conversation ───────────────────────────────────────────────────────

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Send a message to the AI agent platform.
    Automatically routes to the appropriate specialist agent.
    """
    session_id = request.session_id or orchestrator.new_session()

    result = orchestrator.run(
        message=request.message,
        session_id=session_id,
        agent_name=request.agent_name,
        context=request.context,
    )

    return {
        "session_id": session_id,
        "agent": result.get("routed_to"),
        "response": result.get("response"),
        "tool_calls": result.get("tool_calls", []),
        "timestamp": result.get("timestamp"),
        "demo_mode": result.get("demo_mode", False),
    }


@app.get("/api/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """Get conversation history for a session."""
    history = orchestrator.get_session_history(session_id)
    return {"session_id": session_id, "messages": history, "count": len(history)}


@app.post("/api/sessions")
async def create_session():
    """Create a new conversation session."""
    session_id = orchestrator.new_session()
    return {"session_id": session_id, "created_at": datetime.now(timezone.utc).isoformat()}


@app.delete("/api/sessions/{session_id}")
async def reset_session(session_id: str):
    """Reset/clear a conversation session."""
    orchestrator.reset_session(session_id)
    return {"session_id": session_id, "status": "reset"}


# ─── Workflow Endpoints ─────────────────────────────────────────────────────────

@app.post("/api/workflows/run")
async def run_workflow(request: WorkflowRequest):
    """
    Run a predefined multi-agent workflow.
    Available workflows: campaign_launch, compliance_review, audience_build, full_campaign, performance_review
    """
    session_id = request.session_id or str(uuid.uuid4())
    result = orchestrator.run_workflow(
        workflow_name=request.workflow_name,
        initial_data=request.data,
        session_id=session_id,
    )
    return result


@app.get("/api/workflows")
async def list_workflows():
    """List available multi-agent workflows."""
    return {
        "workflows": [
            {
                "name": "campaign_launch",
                "description": "Phase 1–5: Strategy → Copy → Compliance pre-screen → Audience → Launch plan",
                "agents_involved": ["strategy", "copywriting", "compliance", "segmentation", "campaign"],
            },
            {
                "name": "compliance_review",
                "description": "Phase 4: Full FCA financial promotions review with certificate generation",
                "agents_involved": ["compliance"],
            },
            {
                "name": "audience_build",
                "description": "Phase 3: Audience segmentation, suppression, and GDPR validation",
                "agents_involved": ["segmentation"],
            },
            {
                "name": "full_campaign",
                "description": "All 8 phases: End-to-end campaign from strategy through measurement",
                "agents_involved": ["strategy", "copywriting", "asset", "segmentation", "compliance", "campaign", "lead", "nurture", "analytics"],
            },
            {
                "name": "performance_review",
                "description": "Phase 8: Performance reporting, attribution, and budget recommendations",
                "agents_involved": ["analytics"],
            },
        ]
    }


# ─── Campaign Endpoints ─────────────────────────────────────────────────────────

@app.get("/api/campaigns")
async def get_campaigns(status: Optional[str] = None):
    campaigns = list_campaigns(status_filter=status)
    return {"campaigns": campaigns, "total": len(campaigns)}


@app.get("/api/campaigns/{campaign_id}")
async def get_campaign_detail(campaign_id: str):
    campaign = get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")
    return campaign


@app.post("/api/campaigns")
async def create_campaign(request: CampaignCreateRequest):
    """Create a new campaign using the Strategy Agent."""
    session_id = orchestrator.new_session()
    result = orchestrator.run(
        message=(
            f"Create a campaign brief for '{request.campaign_name}' — "
            f"product: {request.product}, objective: {request.objective}, "
            f"target: {request.target_segment}, budget: £{request.budget:,.0f}, "
            f"channels: {', '.join(request.channels)}"
        ),
        session_id=session_id,
        agent_name="strategy",
        context=request.model_dump(),
    )
    return {
        "campaign": result,
        "session_id": session_id,
    }


@app.patch("/api/campaigns/{campaign_id}/status")
async def update_campaign_status_endpoint(campaign_id: str, status: str, notes: Optional[str] = None):
    updated = update_campaign_status(campaign_id, status, {"notes": notes} if notes else None)
    return updated


# ─── Lead Endpoints ─────────────────────────────────────────────────────────────

@app.get("/api/leads")
async def get_leads(status: Optional[str] = None):
    leads = list_leads(status_filter=status)
    return {"leads": leads, "total": len(leads)}


@app.get("/api/leads/{lead_id}")
async def get_lead_detail(lead_id: str):
    lead = get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail=f"Lead {lead_id} not found")
    return lead


@app.post("/api/leads/capture")
async def capture_lead(request: LeadCaptureRequest):
    """Capture and score a new lead using the Lead Management Agent."""
    session_id = orchestrator.new_session()
    result = orchestrator.run(
        message=(
            f"Capture and score new lead: {request.product_interest} enquiry "
            f"via {request.source_channel}, estimated value £{request.estimated_value or 0:,.0f}"
        ),
        session_id=session_id,
        agent_name="lead",
        context=request.model_dump(),
    )
    return result


# ─── Asset Endpoints ────────────────────────────────────────────────────────────

@app.get("/api/assets")
async def get_assets(campaign_id: Optional[str] = None, asset_type: Optional[str] = None):
    assets = list_assets(campaign_id=campaign_id, asset_type=asset_type)
    return {"assets": assets, "total": len(assets)}


@app.get("/api/assets/manifest/{campaign_id}")
async def get_asset_manifest(campaign_id: str, product_name: str = "Product", campaign_name: str = "Campaign"):
    """Generate asset variant manifest for a campaign."""
    from tools.azure_storage_tools import generate_asset_variants_manifest
    manifest = generate_asset_variants_manifest(campaign_id, product_name, campaign_name)
    return manifest


# ─── Compliance Endpoints ───────────────────────────────────────────────────────

@app.get("/api/compliance/records")
async def get_compliance_records(campaign_id: Optional[str] = None):
    records = list_compliance_records(campaign_id=campaign_id)
    return {"records": records, "total": len(records)}


@app.post("/api/compliance/review")
async def compliance_review(content: str, product_type: str, channel: str, campaign_id: Optional[str] = None):
    """Submit content for FCA compliance review."""
    session_id = orchestrator.new_session()
    result = orchestrator.run(
        message=f"Review this {product_type} {channel} content for FCA compliance: {content[:1000]}",
        session_id=session_id,
        agent_name="compliance",
        context={"product_type": product_type, "channel": channel, "campaign_id": campaign_id},
    )
    return result


# ─── Analytics Endpoints ────────────────────────────────────────────────────────

@app.get("/api/analytics/overview")
async def analytics_overview():
    """Get a high-level marketing performance overview."""
    session_id = orchestrator.new_session()
    result = orchestrator.run(
        message="Generate a marketing performance overview with channel metrics, attribution, and budget recommendations",
        session_id=session_id,
        agent_name="analytics",
    )
    return result


@app.get("/api/analytics/campaigns/{campaign_id}")
async def campaign_analytics(campaign_id: str, report_type: str = "in_flight_weekly"):
    """Get performance report for a specific campaign."""
    session_id = orchestrator.new_session()
    result = orchestrator.run(
        message=f"Generate {report_type} report for campaign {campaign_id}",
        session_id=session_id,
        agent_name="analytics",
        context={"campaign_id": campaign_id, "report_type": report_type},
    )
    return result


# ─── Phase Information Endpoints ────────────────────────────────────────────────

@app.get("/api/phases")
async def get_phases():
    """Get the 8-phase marketing lifecycle with agent assignments."""
    return {
        "phases": [
            {
                "id": "phase_1",
                "name": "Strategy & Annual Planning",
                "agents": ["strategy"],
                "sub_phases": ["1a. Annual Marketing Strategy", "1b. Quarterly Campaign Planning"],
                "colour": "#6366f1",
            },
            {
                "id": "phase_2",
                "name": "Campaign Design & Creative Production",
                "agents": ["copywriting", "asset"],
                "sub_phases": ["2a. Copywriting", "2b. Design & Assets", "2c. Images", "2d. PDFs", "2e. Video", "2f. DAM", "2g. Landing Pages"],
                "colour": "#8b5cf6",
            },
            {
                "id": "phase_3",
                "name": "Audience Segmentation & Data Preparation",
                "agents": ["segmentation"],
                "sub_phases": ["3a. Segment Definition & List Build"],
                "colour": "#06b6d4",
            },
            {
                "id": "phase_4",
                "name": "Compliance & Regulatory Review",
                "agents": ["compliance"],
                "sub_phases": ["4a. Financial Promotions Compliance"],
                "colour": "#ef4444",
            },
            {
                "id": "phase_5",
                "name": "Channel Execution & Campaign Launch",
                "agents": ["campaign"],
                "sub_phases": ["5a. Email & CRM", "5b. Paid Media", "5c. Direct Mail & Branch"],
                "colour": "#f59e0b",
            },
            {
                "id": "phase_6",
                "name": "Lead Capture, Scoring & Routing",
                "agents": ["lead"],
                "sub_phases": ["6a. Lead Capture", "6b. Lead Scoring & Routing"],
                "colour": "#10b981",
            },
            {
                "id": "phase_7",
                "name": "Nurture, Follow-Up & Conversion",
                "agents": ["nurture"],
                "sub_phases": ["7a. Automated Nurture Journeys", "7b. RM Follow-Up"],
                "colour": "#3b82f6",
            },
            {
                "id": "phase_8",
                "name": "Measurement, Attribution & Optimisation",
                "agents": ["analytics"],
                "sub_phases": ["8a. Campaign Performance Reporting", "8b. Attribution & ROI Analysis"],
                "colour": "#ec4899",
            },
        ]
    }


# ─── Dashboard Summary ──────────────────────────────────────────────────────────

@app.get("/api/dashboard")
async def dashboard_summary():
    """Get summary data for the main dashboard."""
    campaigns = list_campaigns()
    leads = list_leads()
    assets = list_assets()
    compliance_records = list_compliance_records()

    return {
        "summary": {
            "campaigns": {
                "total": len(campaigns),
                "live": len([c for c in campaigns if c.get("status") == "live"]),
                "draft": len([c for c in campaigns if c.get("status") == "draft"]),
                "awaiting_compliance": len([c for c in campaigns if c.get("status") == "awaiting_compliance"]),
            },
            "leads": {
                "total": len(leads),
                "new": len([l for l in leads if l.get("status") == "new"]),
                "priority": len([l for l in leads if l.get("score_tier") == "PRIORITY"]),
                "converted": len([l for l in leads if l.get("status") == "converted"]),
            },
            "assets": {
                "total": len(assets),
                "approved": len([a for a in assets if a.get("compliance_approved")]),
                "pending_approval": len([a for a in assets if not a.get("compliance_approved")]),
            },
            "compliance": {
                "total_reviews": len(compliance_records),
                "approved": len([r for r in compliance_records if r.get("decision") in ["APPROVED", "APPROVED_WITH_AMENDMENTS"]]),
                "pending": len([r for r in compliance_records if not r.get("decision")]),
            },
        },
        "agents": [
            {"name": name, "status": "active", "phase": name.replace("_", " ").title()}
            for name in AGENT_REGISTRY.keys()
        ],
        "recent_activity": [
            {"time": datetime.now(timezone.utc).isoformat(), "event": "System initialised", "type": "system"},
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
