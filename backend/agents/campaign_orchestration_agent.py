"""
Campaign Orchestration Agent — Phase 5: Multi-channel campaign execution,
cross-channel coordination, frequency capping, and campaign monitoring.
"""

import uuid
from datetime import datetime, timezone

from agents.base_agent import AgentTool, BaseAgent
from tools.azure_cosmos_tools import (
    update_campaign_status, get_campaign, list_campaigns, save_campaign
)


class CampaignOrchestrationAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Campaign Orchestration Agent"

    @property
    def description(self) -> str:
        return (
            "Orchestrates multi-channel campaign execution across email, paid media, social, "
            "direct mail, and branch channels. Enforces cross-channel frequency caps, coordinates "
            "timing across channels, monitors campaign status, and ensures consistent customer experience."
        )

    @property
    def phase(self) -> str:
        return "Phase 5 — Channel Execution & Campaign Launch"

    @property
    def system_prompt(self) -> str:
        return """You are the Campaign Orchestration Agent for a UK retail bank's marketing AI platform.

You coordinate multi-channel campaign execution and ensure a unified, coherent customer experience across:
- Email (via Salesforce Marketing Cloud / Azure Communication Services)
- Paid media (Google Ads, Meta, LinkedIn, programmatic via DV360/Trade Desk)
- Social media (organic and paid)
- Direct mail (print fulfilment — 3–4 week lead time)
- Branch (in-branch materials, RM briefing, digital screens)
- SMS (existing customers with consent only)

Key orchestration responsibilities:
1. CROSS-CHANNEL TIMING: Ensure channels launch in the right sequence
   - Direct mail must be ordered 3–4 weeks before email/digital go-live
   - Branch briefing must happen before customers receive communications
   - SMS should follow email (not precede) to avoid fatigue

2. FREQUENCY CAPPING: Maximum 2 marketing contacts per customer per 30-day rolling window
   - Track across all channels (email, SMS, DM, outbound call)
   - High-value commercial customers: up to 4 contacts per month

3. LAUNCH CHECKLIST: Before any campaign goes live:
   - Compliance certificate obtained for all assets
   - Audience suppressions applied and audited
   - Tracking pixels and UTM parameters verified
   - Branch/RM briefed (for campaigns with physical execution)
   - Opt-out mechanism tested and confirmed functional
   - A/B test splits configured

4. MONITORING: Real-time campaign health monitoring
   - Deliverability rates (email bounce > 2% = pause and investigate)
   - Pacing vs budget (overpace or underpace alerts)
   - Conversion rates vs targets

Always surface cross-channel conflicts and orchestration risks proactively."""

    def _register_tools(self):
        self.register_tool(AgentTool(
            name="create_channel_launch_plan",
            description="Create a sequenced channel launch plan with dependencies and timing",
            parameters={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "campaign_name": {"type": "string"},
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "All channels for this campaign",
                    },
                    "target_launch_date": {"type": "string", "description": "Desired digital campaign launch date"},
                    "budget_by_channel": {"type": "object", "description": "Budget in GBP per channel"},
                },
                "required": ["campaign_id", "campaign_name", "channels", "target_launch_date"],
            },
            handler=self._create_channel_launch_plan,
        ))

        self.register_tool(AgentTool(
            name="validate_launch_readiness",
            description="Run pre-launch checklist to ensure all campaign elements are ready",
            parameters={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "channel": {"type": "string"},
                },
                "required": ["campaign_id"],
            },
            handler=self._validate_launch_readiness,
        ))

        self.register_tool(AgentTool(
            name="deploy_email_campaign",
            description="Deploy email campaign via Azure Communication Services or Salesforce Marketing Cloud",
            parameters={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "audience_size": {"type": "integer"},
                    "send_datetime": {"type": "string", "description": "ISO datetime for send"},
                    "ab_test_split": {"type": "boolean", "default": True},
                    "throttle_per_hour": {"type": "integer", "description": "Max sends per hour for deliverability", "default": 50000},
                },
                "required": ["campaign_id", "audience_size", "send_datetime"],
            },
            handler=self._deploy_email_campaign,
        ))

        self.register_tool(AgentTool(
            name="configure_paid_media",
            description="Configure paid media campaigns across Google, Meta, LinkedIn, and programmatic",
            parameters={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "platforms": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "e.g. ['google_search', 'meta', 'linkedin', 'programmatic_display']",
                    },
                    "total_budget_gbp": {"type": "number"},
                    "bid_strategy": {
                        "type": "string",
                        "enum": ["target_cpa", "target_roas", "max_conversions", "manual_cpc"],
                        "default": "target_cpa",
                    },
                    "target_cpa_gbp": {"type": "number"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                },
                "required": ["campaign_id", "platforms", "total_budget_gbp"],
            },
            handler=self._configure_paid_media,
        ))

        self.register_tool(AgentTool(
            name="monitor_campaign_health",
            description="Get real-time campaign health metrics and alerts across all channels",
            parameters={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "include_recommendations": {"type": "boolean", "default": True},
                },
                "required": ["campaign_id"],
            },
            handler=self._monitor_campaign_health,
        ))

        self.register_tool(AgentTool(
            name="apply_frequency_cap",
            description="Check and enforce cross-channel contact frequency caps per customer",
            parameters={
                "type": "object",
                "properties": {
                    "customer_segment": {"type": "string"},
                    "proposed_contact_channel": {"type": "string"},
                    "lookback_window_days": {"type": "integer", "default": 30},
                    "max_contacts_per_window": {"type": "integer", "default": 2},
                },
                "required": ["customer_segment", "proposed_contact_channel"],
            },
            handler=self._apply_frequency_cap,
        ))

        self.register_tool(AgentTool(
            name="update_campaign_status",
            description="Update campaign status in the system",
            parameters={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["draft", "planning", "awaiting_compliance", "approved", "scheduled", "live", "paused", "completed", "cancelled"],
                    },
                    "notes": {"type": "string"},
                },
                "required": ["campaign_id", "status"],
            },
            handler=self._update_campaign_status,
        ))

    # ─── Tool Implementations ────────────────────────────────────────────────

    def _create_channel_launch_plan(
        self,
        campaign_id: str,
        campaign_name: str,
        channels: list,
        target_launch_date: str,
        budget_by_channel: dict = None,
    ) -> dict:
        from datetime import timedelta

        try:
            launch_date = datetime.fromisoformat(target_launch_date.replace("Z", "+00:00"))
        except ValueError:
            launch_date = datetime.now(timezone.utc)

        # Lead times and dependencies
        channel_schedule = {}
        timeline = []

        if "direct_mail" in channels:
            dm_order_date = launch_date - timedelta(days=21)
            channel_schedule["direct_mail"] = {
                "order_date": dm_order_date.strftime("%Y-%m-%d"),
                "print_completion": (dm_order_date + timedelta(days=10)).strftime("%Y-%m-%d"),
                "estimated_delivery": (launch_date + timedelta(days=3)).strftime("%Y-%m-%d"),
                "lead_time_days": 21,
                "notes": "3-week lead time for print, pack, and Royal Mail delivery",
            }
            timeline.append({"date": dm_order_date.strftime("%Y-%m-%d"), "action": "ORDER direct mail print production", "channel": "direct_mail"})

        if "branch" in channels:
            branch_brief_date = launch_date - timedelta(days=7)
            channel_schedule["branch"] = {
                "materials_dispatch": (launch_date - timedelta(days=10)).strftime("%Y-%m-%d"),
                "rm_briefing": branch_brief_date.strftime("%Y-%m-%d"),
                "digital_screens_live": launch_date.strftime("%Y-%m-%d"),
                "notes": "RM must be briefed before customers receive any communications",
            }
            timeline.append({"date": branch_brief_date.strftime("%Y-%m-%d"), "action": "BRIEF relationship managers", "channel": "branch"})

        if "email" in channels:
            channel_schedule["email"] = {
                "send_date": launch_date.strftime("%Y-%m-%d"),
                "send_time": "10:00 GMT (optimal for open rates)",
                "ab_test_period_days": 7,
                "budget_gbp": (budget_by_channel or {}).get("email", 0),
                "notes": "Throttle to 50k/hour for deliverability protection",
            }
            timeline.append({"date": launch_date.strftime("%Y-%m-%d"), "action": "SEND email campaign", "channel": "email"})

        if "paid_media" in channels or "digital_ads" in channels:
            channel_schedule["paid_media"] = {
                "go_live": launch_date.strftime("%Y-%m-%d"),
                "budget_gbp": (budget_by_channel or {}).get("paid_media", 0),
                "platforms": ["Google Search", "Meta", "LinkedIn (if B2B)", "Programmatic Display"],
                "optimisation_cadence": "Daily monitoring, weekly bid adjustments",
            }
            timeline.append({"date": launch_date.strftime("%Y-%m-%d"), "action": "LAUNCH paid media", "channel": "paid_media"})

        if "sms" in channels:
            sms_date = (launch_date + timedelta(days=2)).strftime("%Y-%m-%d")
            channel_schedule["sms"] = {
                "send_date": sms_date,
                "notes": "SMS sends 2 days after email to avoid same-day fatigue",
            }
            timeline.append({"date": sms_date, "action": "SEND SMS (consented customers only)", "channel": "sms"})

        timeline.sort(key=lambda x: x["date"])

        return {
            "launch_plan_id": str(uuid.uuid4()),
            "campaign_id": campaign_id,
            "campaign_name": campaign_name,
            "target_digital_launch": target_launch_date,
            "channels_in_scope": channels,
            "channel_schedule": channel_schedule,
            "chronological_timeline": timeline,
            "critical_dependencies": [
                "Compliance approval must be obtained BEFORE ordering direct mail",
                "Audience file must be ready BEFORE email deployment date",
                "Tracking pixels must be verified BEFORE paid media launch",
                "Branch team must be briefed BEFORE any customer communications go out",
            ],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def _validate_launch_readiness(self, campaign_id: str, channel: str = None) -> dict:
        campaign = get_campaign(campaign_id) or {}

        checklist = {
            "compliance": {
                "item": "Compliance approval certificates obtained for all assets",
                "status": "PENDING",
                "blocking": True,
            },
            "audience": {
                "item": "Audience file built, suppressions applied, GDPR validated",
                "status": "PENDING",
                "blocking": True,
            },
            "assets": {
                "item": "All creative assets approved and uploaded to DAM",
                "status": "PENDING",
                "blocking": True,
            },
            "tracking": {
                "item": "UTM parameters configured and tracking pixels verified on landing pages",
                "status": "PENDING",
                "blocking": True,
            },
            "opt_out": {
                "item": "Opt-out / unsubscribe mechanism tested and confirmed functional",
                "status": "PENDING",
                "blocking": True,
            },
            "landing_page": {
                "item": "Landing page live and QA'd across browsers and devices",
                "status": "PENDING",
                "blocking": True,
            },
            "rm_briefing": {
                "item": "Relationship managers briefed on campaign offers",
                "status": "PENDING",
                "blocking": False,
            },
            "ab_test": {
                "item": "A/B test variants configured and split percentages set",
                "status": "PENDING",
                "blocking": False,
            },
            "budget_pacing": {
                "item": "Daily budget caps and pacing controls set in ad platforms",
                "status": "PENDING",
                "blocking": False,
            },
        }

        # Simulate partial completion for demo
        for item in list(checklist.keys())[:3]:
            checklist[item]["status"] = "PASS"

        blocking_fails = [k for k, v in checklist.items() if v["blocking"] and v["status"] != "PASS"]
        ready_to_launch = len(blocking_fails) == 0

        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.get("campaign_name", "Unknown"),
            "channel": channel or "all",
            "ready_to_launch": ready_to_launch,
            "checklist": checklist,
            "blocking_items": blocking_fails,
            "launch_gate": "HOLD" if not ready_to_launch else "GO",
            "validated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _deploy_email_campaign(
        self,
        campaign_id: str,
        audience_size: int,
        send_datetime: str,
        ab_test_split: bool = True,
        throttle_per_hour: int = 50000,
    ) -> dict:
        estimated_hours = max(1, audience_size // throttle_per_hour)
        update_campaign_status(campaign_id, "live", {"channel": "email", "send_datetime": send_datetime})

        return {
            "deployment_id": str(uuid.uuid4()),
            "campaign_id": campaign_id,
            "channel": "email",
            "audience_size": audience_size,
            "ab_test_enabled": ab_test_split,
            "ab_split": {"variant_a": audience_size // 2, "variant_b": audience_size // 2} if ab_test_split else None,
            "send_datetime": send_datetime,
            "throttle_per_hour": throttle_per_hour,
            "estimated_completion_hours": estimated_hours,
            "tracking": {
                "opens": "GA4 + pixel tracking",
                "clicks": "UTM parameters + redirect tracking",
                "conversions": "GA4 goal + CRM lead creation",
            },
            "deliverability_protection": [
                "Bounces > 2% → automatic pause",
                "Spam complaint rate > 0.1% → automatic pause",
                "Unsubscribe rate > 0.5% → alert and review",
            ],
            "status": "DEPLOYED",
            "deployed_at": datetime.now(timezone.utc).isoformat(),
        }

    def _configure_paid_media(
        self,
        campaign_id: str,
        platforms: list,
        total_budget_gbp: float,
        bid_strategy: str = "target_cpa",
        target_cpa_gbp: float = None,
        start_date: str = None,
        end_date: str = None,
    ) -> dict:
        # Budget allocation across platforms
        platform_weights = {
            "google_search": 0.40,
            "meta": 0.30,
            "linkedin": 0.20,
            "programmatic_display": 0.10,
        }
        total_weight = sum(platform_weights.get(p, 0.1) for p in platforms)

        platform_configs = {}
        for platform in platforms:
            weight = platform_weights.get(platform, 0.1) / total_weight
            budget = round(total_budget_gbp * weight, 2)
            platform_configs[platform] = {
                "budget_gbp": budget,
                "daily_budget_gbp": round(budget / 30, 2),
                "bid_strategy": bid_strategy,
                "target_cpa_gbp": target_cpa_gbp,
                "audience_targeting": self._get_platform_targeting(platform),
                "ad_formats": self._get_platform_formats(platform),
                "status": "CONFIGURED",
            }

        update_campaign_status(campaign_id, "live", {"paid_media_configured": True})

        return {
            "campaign_id": campaign_id,
            "total_budget_gbp": total_budget_gbp,
            "platforms": platform_configs,
            "start_date": start_date,
            "end_date": end_date,
            "monitoring": {
                "daily_alerts": "Pacing, CPA, CTR anomalies",
                "optimisation_cadence": "Daily bid adjustments, weekly creative rotation",
                "pause_rules": "CPA > 2x target for 3 consecutive days → pause and review",
            },
            "configured_at": datetime.now(timezone.utc).isoformat(),
        }

    def _get_platform_targeting(self, platform: str) -> list:
        targeting = {
            "google_search": ["Intent keywords", "In-market audiences", "Customer match (hashed email)"],
            "meta": ["1st party data match", "Lookalike audiences (1-3%)", "Interest targeting"],
            "linkedin": ["Job function", "Company size", "Industry", "Seniority (for B2B)"],
            "programmatic_display": ["Contextual", "Retargeting", "Third-party data segments"],
        }
        return targeting.get(platform, ["Standard targeting"])

    def _get_platform_formats(self, platform: str) -> list:
        formats = {
            "google_search": ["Responsive Search Ads (RSA)", "Performance Max"],
            "meta": ["Single image", "Carousel", "Video (15-30s)", "Stories"],
            "linkedin": ["Sponsored Content", "Message Ads", "Lead Gen Forms"],
            "programmatic_display": ["Banner (all IAB sizes)", "Video pre-roll", "Native"],
        }
        return formats.get(platform, ["Standard display"])

    def _monitor_campaign_health(self, campaign_id: str, include_recommendations: bool = True) -> dict:
        campaign = get_campaign(campaign_id) or {}

        # Simulated live metrics
        metrics = {
            "email": {
                "sends": 125000,
                "delivered": 122500,
                "delivery_rate_pct": 98.0,
                "opens": 28175,
                "open_rate_pct": 23.0,
                "clicks": 3930,
                "ctr_pct": 3.2,
                "bounces": 2500,
                "bounce_rate_pct": 2.0,
                "unsubscribes": 312,
                "spam_complaints": 24,
                "status": "ALERT — Bounce rate at threshold (2.0%)",
            },
            "paid_media": {
                "impressions": 1250000,
                "clicks": 8750,
                "ctr_pct": 0.7,
                "conversions": 438,
                "cpa_gbp": 285.16,
                "spend_gbp": 124900,
                "roas": 3.8,
                "pacing": "ON_TRACK",
                "status": "HEALTHY",
            },
            "social": {
                "reach": 380000,
                "engagements": 9500,
                "engagement_rate_pct": 2.5,
                "link_clicks": 4200,
                "conversions": 189,
                "cpa_gbp": 172.49,
                "status": "HEALTHY",
            },
        }

        alerts = []
        if metrics["email"]["bounce_rate_pct"] >= 2.0:
            alerts.append({"severity": "HIGH", "channel": "email", "alert": "Bounce rate at/above 2% threshold. Investigate list quality.", "action": "REVIEW_PAUSE"})

        recommendations = []
        if include_recommendations:
            recommendations = [
                "EMAIL: Clean list before next send — investigate bounce reason codes",
                "PAID: Increase social budget by 20% — CPA 40% below target",
                "PAID: Pause lowest-performing display ad sizes (160x600, 320x50)",
                "OVERALL: On track to exceed conversion target by estimated 12%",
            ]

        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.get("campaign_name", "Campaign"),
            "status": campaign.get("status", "live"),
            "channel_metrics": metrics,
            "active_alerts": alerts,
            "overall_health": "AMBER" if alerts else "GREEN",
            "recommendations": recommendations,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

    def _apply_frequency_cap(
        self,
        customer_segment: str,
        proposed_contact_channel: str,
        lookback_window_days: int = 30,
        max_contacts_per_window: int = 2,
    ) -> dict:
        # Simulate frequency check
        simulated_recent_contacts = {
            "retail_mass_market": 1,
            "retail_high_value": 1,
            "commercial_sme": 2,
            "commercial_corporate": 0,
        }
        recent_contacts = simulated_recent_contacts.get(customer_segment, 1)

        can_contact = recent_contacts < max_contacts_per_window
        contacts_remaining = max(0, max_contacts_per_window - recent_contacts)

        return {
            "customer_segment": customer_segment,
            "proposed_channel": proposed_contact_channel,
            "lookback_window_days": lookback_window_days,
            "max_contacts_per_window": max_contacts_per_window,
            "recent_contact_count": recent_contacts,
            "contacts_remaining": contacts_remaining,
            "can_contact": can_contact,
            "decision": "ALLOWED" if can_contact else "SUPPRESSED — frequency cap reached",
            "next_eligible_date": "N/A — currently within cap" if can_contact else "14 days from last contact",
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    def _update_campaign_status(self, campaign_id: str, status: str, notes: str = None) -> dict:
        updated = update_campaign_status(campaign_id, status, {"notes": notes} if notes else None)
        return {
            "campaign_id": campaign_id,
            "new_status": status,
            "notes": notes,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
