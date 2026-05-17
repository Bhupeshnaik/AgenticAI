"""
HeyGen Interactive Avatar — booth / kiosk endpoints.

These endpoints back the trade-show booth UI at /booth:

    POST /api/avatar/token       mint a short-lived HeyGen streaming token
    GET  /api/avatar/config      avatar / voice / language config for the kiosk
    GET  /api/avatar/demos       catalog of demo videos + slides for the side panel
    POST /api/avatar/chat        conversational turn -> spoken text + parsed actions
    POST /api/avatar/lead        capture a booth visitor as a Lead Management lead
    POST /api/avatar/transcript  persist a finished booth conversation

The HeyGen API key NEVER leaves the server. The browser calls /token, gets a
short-lived session token, and uses it with the @heygen/streaming-avatar SDK
to negotiate a WebRTC stream.
"""

import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agents.lead_management_agent import LeadManagementAgent
from config.settings import settings
from orchestrator.orchestrator import orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/avatar", tags=["avatar"])


# ─── Action protocol ──────────────────────────────────────────────────────────

# Matches "[[ACTION:name|key=value|key=value]]" — minimal, forgiving.
_ACTION_RE = re.compile(r"\[\[ACTION:([a-z_]+)((?:\|[a-z_]+=[^\]|]+)*)\]\]", re.IGNORECASE)

_ALLOWED_ACTIONS = {
    "show_demo": {"id"},
    "show_slide": {"id"},
    "open_form": {"type"},
    "handoff": {"agent"},
    "end_topic": set(),
}


def _parse_actions(text: str) -> tuple[str, list[dict]]:
    """
    Pull [[ACTION:...]] tags out of the avatar's reply.
    Returns (spoken_text_with_tags_stripped, [{name, params}, ...]).
    Unknown action names are silently dropped so the avatar never speaks a tag.
    """
    actions: list[dict] = []

    def _consume(match: re.Match) -> str:
        name = match.group(1).lower()
        raw_params = match.group(2) or ""
        params: dict[str, str] = {}
        for piece in raw_params.split("|"):
            piece = piece.strip()
            if not piece or "=" not in piece:
                continue
            k, v = piece.split("=", 1)
            params[k.strip().lower()] = v.strip()

        if name not in _ALLOWED_ACTIONS:
            return ""

        allowed_keys = _ALLOWED_ACTIONS[name]
        params = {k: v for k, v in params.items() if k in allowed_keys}
        actions.append({"name": name, "params": params})
        return ""

    cleaned = _ACTION_RE.sub(_consume, text or "")
    # Tidy up the trailing whitespace / blank lines the tags left behind.
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned, actions


# ─── Demo / slide catalog ─────────────────────────────────────────────────────

DEMOS = [
    {
        "id": "lead_routing",
        "title": "Sub-1-hour commercial lead routing",
        "duration_seconds": 90,
        "poster_url": "/booth-assets/posters/lead-routing.jpg",
        "video_url": "/booth-assets/demos/lead-routing.mp4",
        "tagline": "From web form to RM phone call in under an hour.",
    },
    {
        "id": "compliance_review",
        "title": "FCA compliance review live",
        "duration_seconds": 75,
        "poster_url": "/booth-assets/posters/compliance.jpg",
        "video_url": "/booth-assets/demos/compliance-review.mp4",
        "tagline": "COBS 4 + Consumer Duty check in seconds.",
    },
    {
        "id": "campaign_launch",
        "title": "End-to-end campaign launch",
        "duration_seconds": 120,
        "poster_url": "/booth-assets/posters/campaign-launch.jpg",
        "video_url": "/booth-assets/demos/campaign-launch.mp4",
        "tagline": "Strategy -> copy -> compliance -> audience -> live, in one workflow.",
    },
    {
        "id": "attribution",
        "title": "Multi-touch attribution",
        "duration_seconds": 60,
        "poster_url": "/booth-assets/posters/attribution.jpg",
        "video_url": "/booth-assets/demos/attribution.mp4",
        "tagline": "Last-touch is dead. Here's the data-driven view.",
    },
]

SLIDES = [
    {
        "id": "architecture",
        "title": "9-agent platform architecture",
        "image_url": "/booth-assets/slides/architecture.svg",
    },
    {
        "id": "roi_summary",
        "title": "Outcomes vs the as-is process",
        "image_url": "/booth-assets/slides/roi-summary.svg",
    },
    {
        "id": "phase_map",
        "title": "8-phase marketing lifecycle",
        "image_url": "/booth-assets/slides/phase-map.svg",
    },
]


# ─── Pydantic models ──────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    token: str
    expires_in_seconds: int = 3600
    demo_mode: bool = False


class AvatarConfig(BaseModel):
    avatar_id: str
    voice_id: str
    quality: str
    language: str
    configured: bool
    demo_video_url: Optional[str] = None


class BoothChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None


class BoothAction(BaseModel):
    name: str
    params: dict


class BoothChatResponse(BaseModel):
    session_id: str
    spoken_text: str
    raw_response: str
    actions: list[BoothAction]
    demo_mode: bool = False
    timestamp: str


class BoothLeadRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., min_length=3, max_length=200)
    company: Optional[str] = Field(default=None, max_length=200)
    role: Optional[str] = Field(default=None, max_length=200)
    interest_topic: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(default=None, max_length=2000)
    session_id: Optional[str] = None
    consent: bool = True


class BoothLeadRouting(BaseModel):
    """Structured slice of what the Lead Management agent decided about this lead."""

    score: Optional[int] = None
    tier: Optional[str] = None  # PRIORITY | HIGH | MEDIUM | LOW
    assigned_team: Optional[str] = None
    priority: Optional[str] = None
    sla_hours: Optional[float] = None
    sla_deadline: Optional[str] = None
    promise_text: Optional[str] = None  # Human-readable "we'll be in touch in X hours"


class BoothLeadResponse(BaseModel):
    lead_id: str
    session_id: str
    status: str
    agent_message: str
    routing: BoothLeadRouting
    captured_at: str


class TranscriptTurn(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None


class TranscriptRequest(BaseModel):
    session_id: str
    turns: list[TranscriptTurn]
    visitor_id: Optional[str] = None


# ─── HeyGen token mint ────────────────────────────────────────────────────────

@router.post("/token", response_model=TokenResponse)
async def mint_streaming_token():
    """
    Exchange the server-side HeyGen API key for a short-lived streaming token
    the browser can use to open the WebRTC session.

    HeyGen endpoint: POST /v1/streaming.create_token
    Docs: https://docs.heygen.com/reference/create-session-token
    """
    if not settings.heygen_api_key:
        logger.warning("HEYGEN_API_KEY not set — returning demo-mode token.")
        return TokenResponse(token="demo-mode", expires_in_seconds=0, demo_mode=True)

    url = f"{settings.heygen_api_base.rstrip('/')}/v1/streaming.create_token"
    headers = {"x-api-key": settings.heygen_api_key, "accept": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as exc:
        logger.exception("HeyGen token mint failed: %s %s", exc.response.status_code, exc.response.text)
        raise HTTPException(status_code=502, detail="HeyGen token mint failed")
    except Exception as exc:
        logger.exception("HeyGen token mint error: %s", exc)
        raise HTTPException(status_code=502, detail="HeyGen unreachable")

    token = (data.get("data") or {}).get("token") or data.get("token")
    if not token:
        logger.error("HeyGen returned no token: %s", data)
        raise HTTPException(status_code=502, detail="HeyGen returned no token")

    return TokenResponse(token=token, expires_in_seconds=3600, demo_mode=False)


@router.get("/config", response_model=AvatarConfig)
async def get_avatar_config():
    """Return the HeyGen avatar configuration the kiosk should use."""
    return AvatarConfig(
        avatar_id=settings.heygen_avatar_id,
        voice_id=settings.heygen_voice_id,
        quality=settings.heygen_quality,
        language=settings.heygen_language,
        configured=bool(settings.heygen_api_key and settings.heygen_avatar_id),
        demo_video_url="/booth-assets/idle/attract-loop.mp4",
    )


# ─── Demo catalog ─────────────────────────────────────────────────────────────

@router.get("/demos")
async def list_demos():
    """Catalog of demo videos and slides the booth side panel can play."""
    return {"demos": DEMOS, "slides": SLIDES}


# ─── Booth chat ───────────────────────────────────────────────────────────────

@router.post("/chat", response_model=BoothChatResponse)
async def booth_chat(request: BoothChatRequest):
    """
    One conversational turn for the booth avatar.

    Routes the visitor utterance through the Booth Host agent, parses any
    [[ACTION:...]] tags out of the reply, and returns:
      - `spoken_text`: clean text to send to HeyGen for lip-synced speech
      - `actions`:     structured actions for the kiosk UI to handle
    """
    session_id = request.session_id or orchestrator.new_session()

    result = orchestrator.run(
        message=request.message,
        session_id=session_id,
        agent_name="booth",
    )

    raw = result.get("response") or ""
    spoken, actions = _parse_actions(raw)

    return BoothChatResponse(
        session_id=session_id,
        spoken_text=spoken,
        raw_response=raw,
        actions=[BoothAction(**a) for a in actions],
        demo_mode=bool(result.get("demo_mode")),
        timestamp=result.get("timestamp") or datetime.now(timezone.utc).isoformat(),
    )


# ─── Lead capture ─────────────────────────────────────────────────────────────

_TEAM_LABELS = {
    "commercial_rm": "a senior Relationship Manager",
    "mortgage_specialist": "a Mortgage Specialist",
    "call_centre_priority": "our priority call centre",
    "call_centre_standard": "our call centre",
    "digital_self_serve": "our digital onboarding team",
}


def _format_promise(sla_hours: Optional[float], team: Optional[str]) -> str:
    """Turn SLA + team into the line a visitor sees on the booth success screen."""
    team_label = _TEAM_LABELS.get(team or "", "our team")
    if sla_hours is None:
        return f"{team_label.capitalize()} will be in touch shortly."
    if sla_hours <= 1:
        return f"{team_label.capitalize()} will reach out within the hour."
    if sla_hours < 24:
        return f"{team_label.capitalize()} will reach out within {int(sla_hours)} hours."
    days = round(sla_hours / 24)
    plural = "" if days == 1 else "s"
    return f"{team_label.capitalize()} will reach out within {days} working day{plural}."


def _extract_routing_from_tool_calls(tool_calls: list[dict]) -> dict[str, Any]:
    """Pull score + routing fields out of the lead agent's tool-call results."""
    extracted: dict[str, Any] = {}
    for call in tool_calls or []:
        name = call.get("tool")
        result = call.get("result") or {}
        if not isinstance(result, dict):
            continue
        if name == "score_lead":
            extracted.setdefault("score", result.get("total_score"))
            extracted.setdefault("tier", result.get("score_tier"))
        elif name == "route_lead":
            extracted.setdefault("assigned_team", result.get("assigned_team"))
            extracted.setdefault("priority", result.get("priority"))
            extracted.setdefault("sla_hours", result.get("sla_hours"))
            extracted.setdefault("sla_deadline", result.get("sla_deadline"))
    return extracted


def _fallback_score_and_route(
    lead_id: str, request: BoothLeadRequest
) -> dict[str, Any]:
    """
    Run the deterministic scoring + routing handlers directly so the booth
    always returns structured guidance — even when Azure OpenAI is offline
    and the LLM never decided to call its tools.
    """
    # A booth visitor who filled in the form is a strong intent signal.
    # We don't know value, so assume a mid-band commercial enquiry — the
    # platform-overview demo crowd skews towards £100k-ish opportunities.
    product = (request.interest_topic or "platform_overview").lower()
    if "mortgage" in product:
        product_type = "mortgage"
        estimated_value = 350_000
    elif "commercial" in product or "business" in product or "lending" in product:
        # Booth visitors who self-identify as commercial-lending are exactly
        # the cohort the platform pitches its sub-1-hour RM routing at.
        product_type = "business_banking"
        estimated_value = 500_000
    elif "loan" in product:
        product_type = "personal_loan"
        estimated_value = 15_000
    else:
        product_type = "business_banking"
        estimated_value = 150_000

    agent = LeadManagementAgent()
    score_result = agent._score_lead(
        lead_id=lead_id,
        product_type=product_type,
        estimated_value_gbp=estimated_value,
        intent_signal="form_submit",
        customer_type="prospect",
        engagement_recency_days=0,
    )
    route_result = agent._route_lead(
        lead_id=lead_id,
        lead_score=score_result["total_score"],
        product_type=product_type,
        estimated_value_gbp=estimated_value,
        customer_type="prospect",
    )
    return {
        "score": score_result["total_score"],
        "tier": score_result["score_tier"],
        "assigned_team": route_result["assigned_team"],
        "priority": route_result["priority"],
        "sla_hours": route_result["sla_hours"],
        "sla_deadline": route_result["sla_deadline"],
    }


@router.post("/lead", response_model=BoothLeadResponse)
async def capture_booth_lead(request: BoothLeadRequest):
    """
    Persist a booth visitor as a Lead via the Lead Management Agent so the
    rest of the CRM / SLA / routing machinery picks them up automatically.

    Returns the agent's structured scoring + routing decision so the kiosk
    can show the visitor a personalised confirmation ("a senior RM will
    reach out within the hour") rather than a generic thank-you.
    """
    if not request.consent:
        raise HTTPException(status_code=400, detail="Visitor consent required to capture lead")

    lead_id = f"booth-{uuid.uuid4().hex[:10]}"
    session_id = orchestrator.new_session()
    summary = (
        f"Capture booth visitor lead: {request.name} ({request.email})"
        + (f" from {request.company}" if request.company else "")
        + (f", role {request.role}" if request.role else "")
        + (f". Interested in: {request.interest_topic}" if request.interest_topic else "")
        + (f". Notes: {request.notes}" if request.notes else "")
    )

    result = orchestrator.run(
        message=summary,
        session_id=session_id,
        agent_name="lead",
        context={
            "source_channel": "trade_show_booth",
            "product_interest": request.interest_topic or "platform_overview",
            "intent_signal": "form_submit",
            "customer_name": request.name,
            "contact_email": request.email,
            "company": request.company,
            "role": request.role,
            "notes": request.notes,
            "booth_session_id": request.session_id,
            "lead_id": lead_id,
        },
    )

    # Prefer the agent's own tool-call decisions if it made them; otherwise
    # run the deterministic scoring handlers so the booth never falls back
    # to a generic "we'll be in touch".
    routing_fields = _extract_routing_from_tool_calls(result.get("tool_calls") or [])
    if not routing_fields.get("sla_hours"):
        routing_fields = {**_fallback_score_and_route(lead_id, request), **routing_fields}

    routing = BoothLeadRouting(
        score=routing_fields.get("score"),
        tier=routing_fields.get("tier"),
        assigned_team=routing_fields.get("assigned_team"),
        priority=routing_fields.get("priority"),
        sla_hours=routing_fields.get("sla_hours"),
        sla_deadline=routing_fields.get("sla_deadline"),
        promise_text=_format_promise(
            routing_fields.get("sla_hours"),
            routing_fields.get("assigned_team"),
        ),
    )

    return BoothLeadResponse(
        lead_id=lead_id,
        session_id=session_id,
        status="captured",
        agent_message=result.get("response") or "",
        routing=routing,
        captured_at=datetime.now(timezone.utc).isoformat(),
    )


# ─── Transcript persistence ───────────────────────────────────────────────────

@router.post("/transcript")
async def save_transcript(request: TranscriptRequest):
    """
    Optional: persist a finished booth conversation. Currently logs only — the
    Booth Host agent already writes per-turn messages through the orchestrator
    via Cosmos, so this is for post-session bulk capture (e.g. exporting to
    analytics).
    """
    logger.info(
        "Booth transcript saved session=%s turns=%d visitor=%s",
        request.session_id, len(request.turns), request.visitor_id or "anon",
    )
    return {
        "session_id": request.session_id,
        "turns_saved": len(request.turns),
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }
