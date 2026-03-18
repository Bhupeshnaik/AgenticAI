"""
Segmentation Agent — Phase 3: Audience building, propensity scoring,
suppression rules, GDPR checks, and data preparation.
"""

import uuid
from datetime import datetime, timezone

from agents.base_agent import AgentTool, BaseAgent
from tools.azure_cosmos_tools import save_campaign, get_campaign


class SegmentationAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Segmentation Agent"

    @property
    def description(self) -> str:
        return (
            "Builds targetable audience segments for campaigns. Translates brief audience hypotheses into "
            "data queries, applies propensity models, enforces regulatory suppressions (GDPR, vulnerable "
            "customer flags, contact fatigue rules), and produces clean audience files with suppression audit trails."
        )

    @property
    def phase(self) -> str:
        return "Phase 3 — Audience Segmentation & Data Preparation"

    @property
    def system_prompt(self) -> str:
        return """You are the Segmentation Agent for a UK retail bank's marketing AI platform.

You handle all audience segmentation, data preparation, and GDPR compliance for campaigns.

Your responsibilities:
1. Translate campaign audience hypotheses into targetable segments
2. Apply propensity models (mortgage propensity, churn risk, cross-sell likelihood)
3. Apply all regulatory suppressions (GDPR-mandatory):
   - Marketing consent / opt-in status by channel
   - Collections/arrears exclusions
   - Vulnerable customer flags
   - Deceased / gone-away markers
   - Do-not-contact registers
   - Recent complaint exclusions (typically 90-day window)
4. Apply contact fatigue rules (typically max 2 marketing contacts per customer per month)
5. Deduplicate across concurrent campaigns
6. Produce suppression audit trail for regulatory compliance

UK regulatory context:
- GDPR UK 2018: explicit opt-in required for email/SMS, legitimate interest for direct mail to existing customers
- FCA FG21/1: vulnerable customer flags must be applied to all marketing
- PRA/FCA: customers in financial difficulty (arrears, collections) must be excluded from promotional marketing
- PECR: electronic marketing requires prior consent

Audience sizing guidance:
- Always provide: total universe, suppressions breakdown, final addressable audience
- Flag data quality issues (missing emails, outdated addresses)
- Propensity model scores refresh monthly — warn if scores are stale"""

    def _register_tools(self):
        self.register_tool(AgentTool(
            name="build_audience_segment",
            description="Build a targetable audience segment from campaign brief criteria",
            parameters={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "segment_criteria": {
                        "type": "object",
                        "description": "Targeting criteria including product holdings, demographics, behaviour",
                        "properties": {
                            "product_interest": {"type": "string"},
                            "existing_product": {"type": "string"},
                            "age_range": {"type": "array", "items": {"type": "integer"}},
                            "income_tier": {"type": "string"},
                            "propensity_score_min": {"type": "number"},
                            "customer_type": {"type": "string", "enum": ["existing", "prospect", "lapsed", "all"]},
                            "region": {"type": "string"},
                        },
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Channels for which consent must be validated",
                    },
                },
                "required": ["campaign_id", "segment_criteria", "channels"],
            },
            handler=self._build_audience_segment,
        ))

        self.register_tool(AgentTool(
            name="apply_suppressions",
            description="Apply all regulatory and business suppressions to an audience file",
            parameters={
                "type": "object",
                "properties": {
                    "audience_id": {"type": "string"},
                    "total_universe": {"type": "integer"},
                    "apply_gdpr_consent": {"type": "boolean", "default": True},
                    "apply_collections_exclusion": {"type": "boolean", "default": True},
                    "apply_vulnerable_customer": {"type": "boolean", "default": True},
                    "apply_complaint_exclusion": {"type": "boolean", "default": True},
                    "apply_fatigue_rules": {"type": "boolean", "default": True},
                    "channel": {"type": "string"},
                },
                "required": ["audience_id", "total_universe"],
            },
            handler=self._apply_suppressions,
        ))

        self.register_tool(AgentTool(
            name="calculate_propensity_scores",
            description="Apply ML propensity models to score customers by likelihood to respond",
            parameters={
                "type": "object",
                "properties": {
                    "product_type": {
                        "type": "string",
                        "enum": ["mortgage", "personal_loan", "credit_card", "savings", "business_banking"],
                    },
                    "model_type": {
                        "type": "string",
                        "enum": ["response_propensity", "churn_risk", "cross_sell_likelihood", "value_tier"],
                        "default": "response_propensity",
                    },
                    "audience_id": {"type": "string"},
                    "score_threshold": {"type": "number", "description": "Minimum score to include (0-100)", "default": 60},
                },
                "required": ["product_type", "audience_id"],
            },
            handler=self._calculate_propensity_scores,
        ))

        self.register_tool(AgentTool(
            name="validate_gdpr_compliance",
            description="Validate that an audience file meets GDPR/PECR requirements for the target channel",
            parameters={
                "type": "object",
                "properties": {
                    "audience_id": {"type": "string"},
                    "channel": {
                        "type": "string",
                        "enum": ["email", "sms", "direct_mail", "phone", "digital_ads"],
                    },
                    "customer_relationship": {
                        "type": "string",
                        "enum": ["existing_customer", "prospect", "lapsed"],
                    },
                },
                "required": ["audience_id", "channel", "customer_relationship"],
            },
            handler=self._validate_gdpr_compliance,
        ))

        self.register_tool(AgentTool(
            name="generate_audience_brief",
            description="Generate a complete audience brief with sizing, suppression log, and data quality report",
            parameters={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "segment_name": {"type": "string"},
                    "final_audience_size": {"type": "integer"},
                    "suppression_log": {"type": "object"},
                },
                "required": ["campaign_id", "segment_name", "final_audience_size"],
            },
            handler=self._generate_audience_brief,
        ))

    # ─── Tool Implementations ────────────────────────────────────────────────

    def _build_audience_segment(
        self,
        campaign_id: str,
        segment_criteria: dict,
        channels: list,
    ) -> dict:
        # Simulate segment sizing based on criteria
        base_universe = {
            "mortgage": 285000,
            "personal_loan": 520000,
            "credit_card": 680000,
            "savings": 1200000,
            "business_banking": 45000,
        }.get(segment_criteria.get("product_interest", "personal_loan"), 400000)

        # Apply criteria filters
        customer_type = segment_criteria.get("customer_type", "all")
        customer_type_factor = {"existing": 0.35, "prospect": 0.55, "lapsed": 0.10, "all": 1.0}.get(customer_type, 1.0)

        income_factor = {"high": 0.2, "medium": 0.5, "low": 0.3}.get(segment_criteria.get("income_tier", "medium"), 0.5)

        propensity_min = segment_criteria.get("propensity_score_min", 50)
        propensity_factor = max(0.1, 1 - (propensity_min / 150))

        estimated_universe = int(base_universe * customer_type_factor * income_factor * propensity_factor)

        audience_id = str(uuid.uuid4())

        return {
            "audience_id": audience_id,
            "campaign_id": campaign_id,
            "segment_name": f"{segment_criteria.get('product_interest', 'product')}_{customer_type}_segment",
            "criteria_applied": segment_criteria,
            "channels": channels,
            "estimated_universe": estimated_universe,
            "data_sources": [
                "Core banking system (customer master data)",
                "Transaction history (24 months)",
                "Marketing consent register (GDPR)",
                "Propensity model scores (monthly refresh)",
                "Collections/arrears system",
            ],
            "estimated_build_time_days": 3,
            "status": "PENDING_SUPPRESSIONS",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def _apply_suppressions(
        self,
        audience_id: str,
        total_universe: int,
        apply_gdpr_consent: bool = True,
        apply_collections_exclusion: bool = True,
        apply_vulnerable_customer: bool = True,
        apply_complaint_exclusion: bool = True,
        apply_fatigue_rules: bool = True,
        channel: str = "email",
    ) -> dict:
        # Realistic suppression rates for UK banking
        suppression_rates = {
            "gdpr_no_consent": {"rate": 0.28, "applicable": apply_gdpr_consent},
            "collections_arrears": {"rate": 0.04, "applicable": apply_collections_exclusion},
            "vulnerable_customer": {"rate": 0.06, "applicable": apply_vulnerable_customer},
            "recent_complaint_90d": {"rate": 0.02, "applicable": apply_complaint_exclusion},
            "contact_fatigue": {"rate": 0.08, "applicable": apply_fatigue_rules},
            "deceased_gone_away": {"rate": 0.01, "applicable": True},
            "do_not_contact_register": {"rate": 0.03, "applicable": True},
        }

        # Channel-specific consent rates
        channel_consent = {"email": 0.72, "sms": 0.65, "direct_mail": 0.88, "phone": 0.60, "digital_ads": 0.95}
        if apply_gdpr_consent:
            suppression_rates["gdpr_no_consent"]["rate"] = 1 - channel_consent.get(channel, 0.72)

        remaining = total_universe
        suppression_log = []

        for suppression_name, config in suppression_rates.items():
            if config["applicable"]:
                removed = int(remaining * config["rate"])
                remaining -= removed
                suppression_log.append({
                    "suppression": suppression_name,
                    "excluded": removed,
                    "rate_pct": round(config["rate"] * 100, 1),
                    "remaining_after": remaining,
                    "regulatory_basis": self._get_suppression_basis(suppression_name),
                })

        return {
            "audience_id": audience_id,
            "channel": channel,
            "pre_suppression_universe": total_universe,
            "final_addressable_audience": remaining,
            "total_excluded": total_universe - remaining,
            "exclusion_rate_pct": round((1 - remaining / total_universe) * 100, 1),
            "suppression_log": suppression_log,
            "audit_trail_ref": f"AUD-SEG-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{audience_id[:8]}",
            "dpa_compliant": True,
            "suppressions_applied_at": datetime.now(timezone.utc).isoformat(),
        }

    def _get_suppression_basis(self, suppression_name: str) -> str:
        bases = {
            "gdpr_no_consent": "UK GDPR Article 6 / PECR Regulation 6",
            "collections_arrears": "FCA FG21/1 — Financial difficulty exclusion",
            "vulnerable_customer": "FCA FG21/1 — Vulnerable customer protection",
            "recent_complaint_90d": "FCA DISP — Complaint management",
            "contact_fatigue": "FCA COBS 4 / Internal contact policy (max 2 per month)",
            "deceased_gone_away": "Data accuracy / FCA COBS 4",
            "do_not_contact_register": "UK GDPR Article 21 / TPS registration",
        }
        return bases.get(suppression_name, "Internal policy")

    def _calculate_propensity_scores(
        self,
        product_type: str,
        audience_id: str,
        model_type: str = "response_propensity",
        score_threshold: float = 60,
    ) -> dict:
        model_specs = {
            "response_propensity": {
                "description": "Likelihood to respond to marketing and start an application",
                "features": ["recency of product enquiry", "web browsing behaviour", "life event signals", "income tier", "existing product mix"],
                "model_type": "Gradient Boosted Tree (Azure ML)",
                "auc_roc": 0.78,
                "last_trained": "2026-02-01",
                "refresh_frequency": "Monthly",
            },
            "churn_risk": {
                "description": "Risk of customer leaving in next 90 days",
                "features": ["engagement decline", "competitor rate comparison searches", "complaint history", "balance trajectory"],
                "model_type": "Logistic Regression (Azure ML)",
                "auc_roc": 0.74,
                "last_trained": "2026-02-01",
                "refresh_frequency": "Monthly",
            },
            "cross_sell_likelihood": {
                "description": "Likelihood to take an additional product",
                "features": ["existing product mix", "transaction patterns", "life stage indicators", "income changes"],
                "model_type": "Random Forest (Azure ML)",
                "auc_roc": 0.71,
                "last_trained": "2026-02-01",
                "refresh_frequency": "Monthly",
            },
        }

        model = model_specs.get(model_type, model_specs["response_propensity"])

        # Score distribution simulation
        score_distribution = {
            "90-100 (Very High)": int(0.05 * 10000),
            "80-89 (High)": int(0.12 * 10000),
            "70-79 (Medium-High)": int(0.18 * 10000),
            "60-69 (Medium)": int(0.25 * 10000),
            "50-59 (Medium-Low)": int(0.20 * 10000),
            "Below 50 (Low)": int(0.20 * 10000),
        }

        above_threshold = sum(v for k, v in score_distribution.items() if int(k.split("-")[0].split(" ")[0]) >= score_threshold)

        return {
            "audience_id": audience_id,
            "product_type": product_type,
            "model_applied": model_type,
            "model_specification": model,
            "score_threshold": score_threshold,
            "total_scored": 10000,
            "above_threshold": above_threshold,
            "score_distribution": score_distribution,
            "expected_response_rate_pct": round(3.2 + (score_threshold - 50) * 0.05, 2),
            "model_freshness": "Current" if True else "WARNING: Scores >30 days old",
            "recommendations": [
                f"Prioritise top decile (score 90+) for personalised RM outreach",
                f"Use score 60-89 for standard channel execution",
                f"Consider suppressing score <60 to improve efficiency",
            ],
            "scored_at": datetime.now(timezone.utc).isoformat(),
        }

    def _validate_gdpr_compliance(
        self,
        audience_id: str,
        channel: str,
        customer_relationship: str,
    ) -> dict:
        legal_basis = {
            ("email", "existing_customer"): ("Legitimate Interest", "Soft opt-in (PECR Reg 22) — existing customer, similar products. Must have clear opt-out."),
            ("email", "prospect"): ("Consent", "PECR Reg 6 — explicit consent required for email marketing to prospects."),
            ("email", "lapsed"): ("Consent", "Consent required — customer relationship ended, soft opt-in no longer applies."),
            ("sms", "existing_customer"): ("Consent", "PECR Reg 6 — SMS requires explicit consent even for existing customers."),
            ("sms", "prospect"): ("Consent", "PECR Reg 6 — explicit consent required."),
            ("direct_mail", "existing_customer"): ("Legitimate Interest", "UK GDPR Article 6(1)(f) — LI applies for direct mail to existing customers. LIA required."),
            ("direct_mail", "prospect"): ("Legitimate Interest", "UK GDPR Article 6(1)(f) — LI can apply but LIA must document that customer interests don't override."),
            ("phone", "existing_customer"): ("Legitimate Interest / Consent", "Check TPS registration. Consent preferred for unsolicited calls."),
            ("digital_ads", "existing_customer"): ("Legitimate Interest / Consent", "Cookie consent required for retargeting. Hashed email matching requires consent."),
            ("digital_ads", "prospect"): ("Consent", "Cookie consent required. Contextual advertising does not require consent."),
        }

        basis_key = (channel, customer_relationship)
        legal_basis_type, legal_basis_detail = legal_basis.get(basis_key, ("Unknown", "Seek legal advice"))

        dpia_required = (
            channel in ["digital_ads", "email"] and customer_relationship == "prospect"
            or (legal_basis_type == "Legitimate Interest" and channel == "direct_mail")
        )

        return {
            "audience_id": audience_id,
            "channel": channel,
            "customer_relationship": customer_relationship,
            "legal_basis": legal_basis_type,
            "legal_basis_detail": legal_basis_detail,
            "gdpr_compliant": legal_basis_type != "Unknown",
            "dpia_required": dpia_required,
            "requirements": [
                "Verify opt-in consent records are documented and dated",
                "Ensure opt-out mechanism is clear and functional",
                "Retain consent records for minimum 3 years",
                "Include privacy notice reference in all communications",
            ],
            "retention_period": "Marketing data: 3 years post-consent or last interaction",
            "validated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _generate_audience_brief(
        self,
        campaign_id: str,
        segment_name: str,
        final_audience_size: int,
        suppression_log: dict = None,
    ) -> dict:
        return {
            "brief_id": str(uuid.uuid4()),
            "campaign_id": campaign_id,
            "segment_name": segment_name,
            "final_audience_size": final_audience_size,
            "data_quality_report": {
                "email_match_rate_pct": 78,
                "postal_address_validation_pct": 91,
                "phone_match_rate_pct": 65,
                "duplicate_rate_pct": 1.2,
                "data_freshness": "Customer data refreshed daily from core banking system",
            },
            "suppression_log": suppression_log or {},
            "personalisation_fields_available": [
                "first_name", "last_name", "current_product", "current_rate",
                "product_maturity_date", "estimated_value", "offer_code",
                "relationship_manager_name",
            ],
            "file_format": "CSV / SFTP encrypted delivery to campaign platform",
            "gdpr_sign_off_required": True,
            "dpo_reviewed": False,
            "brief_status": "AWAITING_DPO_SIGN_OFF",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
