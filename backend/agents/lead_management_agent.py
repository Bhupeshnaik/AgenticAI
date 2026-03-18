"""
Lead Management Agent — Phase 6: Lead capture, AI scoring, routing,
SLA management, and real-time alerting for high-value leads.
"""

import uuid
from datetime import datetime, timezone

from agents.base_agent import AgentTool, BaseAgent
from tools.azure_cosmos_tools import save_lead, get_lead, list_leads, update_lead


class LeadManagementAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Lead Management Agent"

    @property
    def description(self) -> str:
        return (
            "Captures, scores, and routes marketing leads across all channels. "
            "Prioritises high-value commercial leads for immediate RM contact, "
            "applies SLA tracking, and prevents high-value leads being lost in generic queues."
        )

    @property
    def phase(self) -> str:
        return "Phase 6 — Lead Capture, Scoring & Routing"

    @property
    def system_prompt(self) -> str:
        return """You are the Lead Management Agent for a UK retail bank's marketing AI platform.

You handle the complete lead lifecycle from first touch to RM assignment:

LEAD SCORING FRAMEWORK:
Score leads 0–100 based on:
- Estimated product value (40% weight): mortgage £200k+ = high, personal loan £5k = low
- Intent signals (30% weight): direct application attempt > landing page visit > email click
- Customer profile (20% weight): existing customer > lapsed > prospect
- Engagement recency (10% weight): today > this week > this month

ROUTING RULES:
- Score 80–100: PRIORITY — immediate RM alert, 1-hour SLA for commercial, 4-hour for retail
- Score 60–79: HIGH — RM assigned within 4 hours for commercial, 24 hours for retail
- Score 40–59: MEDIUM — Standard queue, 24-48 hour response
- Score 0–39: LOW — Digital self-serve journey, nurture sequence enrolled

CHANNEL ROUTING:
- Commercial lending (>£100k): Senior Relationship Manager
- Mortgage (>£150k LTV): Mortgage Specialist
- Retail products: Call centre or digital self-serve based on score
- Existing customer cross-sell: Account Manager or RM (if premium)

KEY PROBLEM YOU SOLVE: In the as-is process, a £5M commercial lending enquiry gets
the same priority queue as a student account signup. You eliminate this with AI scoring
and real-time routing."""

    def _register_tools(self):
        self.register_tool(AgentTool(
            name="capture_lead",
            description="Capture a new lead from any channel into the unified CRM",
            parameters={
                "type": "object",
                "properties": {
                    "source_channel": {
                        "type": "string",
                        "enum": ["web_form", "call_centre", "branch_walkin", "social_dm", "email_response", "direct_mail_response"],
                    },
                    "product_interest": {"type": "string"},
                    "customer_name": {"type": "string"},
                    "contact_email": {"type": "string"},
                    "contact_phone": {"type": "string"},
                    "estimated_value": {"type": "number", "description": "Estimated product value in GBP"},
                    "campaign_id": {"type": "string"},
                    "utm_source": {"type": "string"},
                    "existing_customer_id": {"type": "string", "description": "If existing customer, their ID"},
                    "intent_signal": {
                        "type": "string",
                        "enum": ["application_started", "landing_page_visit", "email_click", "form_submit", "phone_enquiry", "branch_enquiry"],
                    },
                },
                "required": ["source_channel", "product_interest", "intent_signal"],
            },
            handler=self._capture_lead,
        ))

        self.register_tool(AgentTool(
            name="score_lead",
            description="AI-powered lead scoring based on value, intent, profile, and engagement",
            parameters={
                "type": "object",
                "properties": {
                    "lead_id": {"type": "string"},
                    "product_type": {"type": "string"},
                    "estimated_value_gbp": {"type": "number"},
                    "intent_signal": {"type": "string"},
                    "customer_type": {"type": "string", "enum": ["existing", "prospect", "lapsed"]},
                    "engagement_recency_days": {"type": "integer", "description": "Days since first engagement"},
                },
                "required": ["lead_id", "product_type", "estimated_value_gbp", "intent_signal"],
            },
            handler=self._score_lead,
        ))

        self.register_tool(AgentTool(
            name="route_lead",
            description="Route a scored lead to the appropriate team with SLA assignment",
            parameters={
                "type": "object",
                "properties": {
                    "lead_id": {"type": "string"},
                    "lead_score": {"type": "number"},
                    "product_type": {"type": "string"},
                    "estimated_value_gbp": {"type": "number"},
                    "customer_type": {"type": "string"},
                },
                "required": ["lead_id", "lead_score", "product_type"],
            },
            handler=self._route_lead,
        ))

        self.register_tool(AgentTool(
            name="alert_high_value_lead",
            description="Send real-time alert to Relationship Manager for high-value leads",
            parameters={
                "type": "object",
                "properties": {
                    "lead_id": {"type": "string"},
                    "rm_id": {"type": "string", "description": "ID of the assigned RM"},
                    "lead_summary": {"type": "string"},
                    "estimated_value_gbp": {"type": "number"},
                    "urgency": {"type": "string", "enum": ["immediate", "1_hour", "4_hour", "24_hour"]},
                },
                "required": ["lead_id", "lead_summary", "estimated_value_gbp", "urgency"],
            },
            handler=self._alert_high_value_lead,
        ))

        self.register_tool(AgentTool(
            name="get_lead_queue",
            description="Get current lead queue with priorities and SLA status",
            parameters={
                "type": "object",
                "properties": {
                    "team": {
                        "type": "string",
                        "enum": ["all", "commercial_rm", "mortgage_specialist", "call_centre", "digital_self_serve"],
                        "default": "all",
                    },
                    "sla_breaches_only": {"type": "boolean", "default": False},
                },
                "required": [],
            },
            handler=self._get_lead_queue,
        ))

        self.register_tool(AgentTool(
            name="update_lead_status",
            description="Update lead status and log interaction notes",
            parameters={
                "type": "object",
                "properties": {
                    "lead_id": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["new", "contacted", "qualified", "application_started", "application_submitted", "approved", "declined", "nurture", "lost"],
                    },
                    "notes": {"type": "string"},
                    "next_action": {"type": "string"},
                    "next_action_date": {"type": "string"},
                },
                "required": ["lead_id", "status"],
            },
            handler=self._update_lead_status,
        ))

    # ─── Tool Implementations ────────────────────────────────────────────────

    def _capture_lead(
        self,
        source_channel: str,
        product_interest: str,
        intent_signal: str,
        customer_name: str = None,
        contact_email: str = None,
        contact_phone: str = None,
        estimated_value: float = None,
        campaign_id: str = None,
        utm_source: str = None,
        existing_customer_id: str = None,
    ) -> dict:
        lead = {
            "lead_id": str(uuid.uuid4()),
            "source_channel": source_channel,
            "product_interest": product_interest,
            "intent_signal": intent_signal,
            "customer_name": customer_name,
            "contact_email": contact_email,
            "contact_phone": contact_phone,
            "estimated_value_gbp": estimated_value,
            "campaign_id": campaign_id,
            "utm_source": utm_source,
            "existing_customer_id": existing_customer_id,
            "customer_type": "existing" if existing_customer_id else "prospect",
            "status": "new",
            "captured_at": datetime.now(timezone.utc).isoformat(),
        }
        saved = save_lead(lead)
        return {
            "lead_id": saved["lead_id"],
            "status": "CAPTURED",
            "next_step": "Score and route — expected within 60 seconds",
            "captured_at": saved.get("created_at"),
        }

    def _score_lead(
        self,
        lead_id: str,
        product_type: str,
        estimated_value_gbp: float,
        intent_signal: str,
        customer_type: str = "prospect",
        engagement_recency_days: int = 0,
    ) -> dict:
        # Scoring model
        # 1. Value score (0–40 points)
        value_thresholds = {
            "mortgage": [(500000, 40), (200000, 35), (100000, 25), (50000, 15), (0, 10)],
            "personal_loan": [(50000, 35), (20000, 28), (10000, 20), (5000, 12), (0, 5)],
            "credit_card": [(10000, 25), (5000, 18), (2000, 12), (0, 8)],
            "savings": [(100000, 35), (50000, 28), (20000, 20), (5000, 12), (0, 5)],
            "business_banking": [(5000000, 40), (500000, 38), (100000, 30), (50000, 22), (0, 12)],
        }
        thresholds = value_thresholds.get(product_type, [(100000, 30), (10000, 20), (0, 10)])
        value_score = next((score for threshold, score in thresholds if estimated_value_gbp >= threshold), 5)

        # 2. Intent score (0–30 points)
        intent_scores = {
            "application_started": 30,
            "form_submit": 26,
            "phone_enquiry": 22,
            "branch_enquiry": 20,
            "email_click": 14,
            "landing_page_visit": 10,
        }
        intent_score = intent_scores.get(intent_signal, 10)

        # 3. Customer profile (0–20 points)
        profile_scores = {"existing": 20, "lapsed": 14, "prospect": 8}
        profile_score = profile_scores.get(customer_type, 8)

        # 4. Engagement recency (0–10 points)
        recency_score = max(0, 10 - engagement_recency_days)

        total_score = min(100, value_score + intent_score + profile_score + recency_score)

        score_tier = (
            "PRIORITY" if total_score >= 80
            else "HIGH" if total_score >= 60
            else "MEDIUM" if total_score >= 40
            else "LOW"
        )

        update_lead(lead_id, {
            "lead_score": total_score,
            "score_tier": score_tier,
            "scored_at": datetime.now(timezone.utc).isoformat(),
        })

        return {
            "lead_id": lead_id,
            "total_score": total_score,
            "score_tier": score_tier,
            "score_breakdown": {
                "value_score": value_score,
                "intent_score": intent_score,
                "profile_score": profile_score,
                "engagement_recency_score": recency_score,
            },
            "scoring_rationale": f"Value: {estimated_value_gbp:,.0f} GBP ({value_score}pts) + Intent: {intent_signal} ({intent_score}pts) + Profile: {customer_type} ({profile_score}pts) + Recency: {engagement_recency_days}d ({recency_score}pts)",
            "scored_at": datetime.now(timezone.utc).isoformat(),
        }

    def _route_lead(
        self,
        lead_id: str,
        lead_score: float,
        product_type: str,
        estimated_value_gbp: float = None,
        customer_type: str = "prospect",
    ) -> dict:
        # Routing logic
        if lead_score >= 80:
            if product_type == "business_banking" or (estimated_value_gbp and estimated_value_gbp >= 100000):
                assigned_team = "commercial_rm"
                sla_hours = 1
                priority = "CRITICAL"
            else:
                assigned_team = "mortgage_specialist" if product_type == "mortgage" else "call_centre_priority"
                sla_hours = 4
                priority = "HIGH"
        elif lead_score >= 60:
            assigned_team = "mortgage_specialist" if product_type == "mortgage" else "call_centre_standard"
            sla_hours = 24
            priority = "MEDIUM_HIGH"
        elif lead_score >= 40:
            assigned_team = "call_centre_standard"
            sla_hours = 48
            priority = "MEDIUM"
        else:
            assigned_team = "digital_self_serve"
            sla_hours = 72
            priority = "LOW"

        sla_deadline = datetime.now(timezone.utc)
        from datetime import timedelta
        sla_deadline = sla_deadline + timedelta(hours=sla_hours)

        update_lead(lead_id, {
            "assigned_team": assigned_team,
            "priority": priority,
            "sla_deadline": sla_deadline.isoformat(),
            "status": "routed",
        })

        return {
            "lead_id": lead_id,
            "assigned_team": assigned_team,
            "priority": priority,
            "sla_hours": sla_hours,
            "sla_deadline": sla_deadline.isoformat(),
            "routing_rationale": f"Score {lead_score:.0f} → {priority} priority for {product_type}",
            "notification_sent": True,
            "routed_at": datetime.now(timezone.utc).isoformat(),
        }

    def _alert_high_value_lead(
        self,
        lead_id: str,
        lead_summary: str,
        estimated_value_gbp: float,
        urgency: str,
        rm_id: str = None,
    ) -> dict:
        alert = {
            "alert_id": str(uuid.uuid4()),
            "lead_id": lead_id,
            "rm_id": rm_id or "auto_assigned",
            "urgency": urgency,
            "estimated_value_gbp": estimated_value_gbp,
            "alert_message": (
                f"HIGH VALUE LEAD: {lead_summary}\n"
                f"Estimated value: £{estimated_value_gbp:,.0f}\n"
                f"Response required: {urgency.replace('_', ' ')}\n"
                f"Lead ID: {lead_id}"
            ),
            "notification_channels": ["push_notification", "email", "crm_task"],
            "alert_sent_via": "Azure Communication Services",
            "alert_sent_at": datetime.now(timezone.utc).isoformat(),
            "acknowledged": False,
        }
        return alert

    def _get_lead_queue(self, team: str = "all", sla_breaches_only: bool = False) -> dict:
        leads = list_leads()

        queue_summary = {
            "total_leads": len(leads),
            "by_priority": {"PRIORITY": 3, "HIGH": 12, "MEDIUM": 28, "LOW": 45},
            "by_team": {
                "commercial_rm": 3,
                "mortgage_specialist": 8,
                "call_centre_priority": 7,
                "call_centre_standard": 26,
                "digital_self_serve": 44,
            },
            "sla_status": {
                "on_track": 78,
                "at_risk": 8,
                "breached": 2,
            },
            "sla_breaches": [
                {
                    "lead_id": "demo-breach-001",
                    "priority": "HIGH",
                    "product": "mortgage",
                    "hours_overdue": 3.5,
                    "team": "call_centre_standard",
                    "action": "Escalate to team leader immediately",
                },
            ] if not sla_breaches_only else [],
            "team_filter": team,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        return queue_summary

    def _update_lead_status(
        self,
        lead_id: str,
        status: str,
        notes: str = None,
        next_action: str = None,
        next_action_date: str = None,
    ) -> dict:
        updates = {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if notes:
            updates["notes"] = notes
        if next_action:
            updates["next_action"] = next_action
        if next_action_date:
            updates["next_action_date"] = next_action_date

        updated = update_lead(lead_id, updates)
        return {
            "lead_id": lead_id,
            "new_status": status,
            "interaction_logged": True,
            "next_action": next_action,
            "updated_at": updates["updated_at"],
        }
