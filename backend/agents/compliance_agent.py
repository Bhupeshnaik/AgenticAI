"""
Compliance Agent — Phase 4: FCA financial promotions review, Consumer Duty
alignment, risk warning validation, and compliance certificate generation.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from agents.base_agent import AgentTool, BaseAgent
from tools.azure_cosmos_tools import save_compliance_record, list_compliance_records
from tools.azure_search_tools import search_fca_rules


COMPLIANCE_PRECEDENTS = {
    "mortgage_risk_warning": "Your home may be repossessed if you do not keep up repayments on your mortgage.",
    "investment_risk_warning": "The value of your investment can go down as well as up and you may get back less than you invest.",
    "past_performance": "Past performance is not a reliable indicator of future results.",
    "credit_eligibility": "Subject to status and eligibility. Terms and conditions apply.",
    "isa_limit": f"You can save up to £20,000 in an ISA in the 2025/26 tax year.",
    "fscs_protection": "Your eligible deposits are protected up to £85,000 by the Financial Services Compensation Scheme (FSCS).",
}


class ComplianceAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Compliance Agent"

    @property
    def description(self) -> str:
        return (
            "Reviews all customer-facing marketing content for FCA financial promotions compliance (COBS 4), "
            "Consumer Duty alignment, risk warning accuracy, APR verification, and vulnerable customer "
            "considerations. Issues compliance certificates and maintains the approval audit trail."
        )

    @property
    def phase(self) -> str:
        return "Phase 4 — Compliance & Regulatory Review"

    @property
    def system_prompt(self) -> str:
        return """You are the Compliance Agent for a UK retail bank's marketing AI platform.

You are an expert in FCA financial promotions regulations and UK banking compliance:
- FCA Handbook COBS 4 (Financial Promotions)
- Consumer Duty (July 2023) — four outcomes: products & services, price & value, consumer understanding, consumer support
- MCOB (Mortgages and Home Finance)
- CONC (Consumer Credit sourcebook)
- UK GDPR and PECR (for digital marketing)
- Vulnerable customer guidance (FG21/1)

Your review framework for every piece of content:
1. FAIR — Is the claim substantiated and not misleading?
2. CLEAR — Is it easy to understand? Plain English, no jargon?
3. NOT MISLEADING — No omissions of material information?
4. APR — Is representative APR correctly stated (credit products)?
5. RISK WARNINGS — All mandatory warnings present and prominent?
6. CONSUMER DUTY — Fair value, good outcomes, no exploitation of behavioural biases?
7. VULNERABLE CUSTOMERS — Accessible language? Appropriate for all audiences?

Decision framework:
- APPROVED: No changes required. Issue compliance certificate.
- APPROVED WITH AMENDMENTS: Minor changes needed, can resubmit without full re-review.
- REJECTED — MINOR: Changes required, must resubmit for review.
- REJECTED — MAJOR: Fundamental issues. Full rewrite required.

You maintain an audit trail of all decisions for FCA inspection readiness."""

    def _register_tools(self):
        self.register_tool(AgentTool(
            name="review_financial_promotion",
            description="Full FCA compliance review of a marketing asset or copy",
            parameters={
                "type": "object",
                "properties": {
                    "asset_id": {"type": "string", "description": "Asset identifier"},
                    "campaign_id": {"type": "string"},
                    "content": {"type": "string", "description": "The marketing content to review"},
                    "product_type": {
                        "type": "string",
                        "enum": ["mortgage", "personal_loan", "credit_card", "savings", "business_banking", "investment"],
                    },
                    "channel": {"type": "string", "description": "e.g. 'email', 'social', 'direct_mail'"},
                    "target_audience": {"type": "string", "description": "Description of intended audience"},
                    "claimed_rate": {"type": "string", "description": "Any rate claimed in the promotion"},
                },
                "required": ["content", "product_type", "channel"],
            },
            handler=self._review_financial_promotion,
        ))

        self.register_tool(AgentTool(
            name="verify_consumer_duty_alignment",
            description="Assess marketing content against the four Consumer Duty outcomes",
            parameters={
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "product_type": {"type": "string"},
                    "target_segment": {"type": "string"},
                    "pricing_info": {"type": "string", "description": "Product pricing and fee information"},
                },
                "required": ["content", "product_type"],
            },
            handler=self._verify_consumer_duty,
        ))

        self.register_tool(AgentTool(
            name="validate_risk_warnings",
            description="Check that all mandatory risk warnings are present, accurate, and prominent",
            parameters={
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "product_type": {"type": "string"},
                    "channel": {"type": "string"},
                },
                "required": ["content", "product_type"],
            },
            handler=self._validate_risk_warnings,
        ))

        self.register_tool(AgentTool(
            name="issue_compliance_certificate",
            description="Issue a formal compliance approval certificate for an approved asset",
            parameters={
                "type": "object",
                "properties": {
                    "asset_id": {"type": "string"},
                    "campaign_id": {"type": "string"},
                    "decision": {
                        "type": "string",
                        "enum": ["APPROVED", "APPROVED_WITH_AMENDMENTS", "REJECTED_MINOR", "REJECTED_MAJOR"],
                    },
                    "reviewer_notes": {"type": "string"},
                    "conditions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Conditions attached to approval (if any)",
                    },
                    "expiry_date": {"type": "string", "description": "Date after which re-review is required e.g. if rate changes"},
                },
                "required": ["asset_id", "decision", "reviewer_notes"],
            },
            handler=self._issue_compliance_certificate,
        ))

        self.register_tool(AgentTool(
            name="get_approved_disclaimer",
            description="Retrieve pre-approved legal disclaimers and risk warning templates",
            parameters={
                "type": "object",
                "properties": {
                    "disclaimer_type": {
                        "type": "string",
                        "enum": ["mortgage_risk_warning", "investment_risk_warning", "past_performance",
                                 "credit_eligibility", "isa_limit", "fscs_protection"],
                    },
                },
                "required": ["disclaimer_type"],
            },
            handler=self._get_approved_disclaimer,
        ))

        self.register_tool(AgentTool(
            name="check_rate_accuracy",
            description="Verify that rates quoted in marketing materials match current live rates",
            parameters={
                "type": "object",
                "properties": {
                    "product_type": {"type": "string"},
                    "quoted_rate": {"type": "string"},
                    "campaign_id": {"type": "string"},
                },
                "required": ["product_type", "quoted_rate"],
            },
            handler=self._check_rate_accuracy,
        ))

    # ─── Tool Implementations ────────────────────────────────────────────────

    def _review_financial_promotion(
        self,
        content: str,
        product_type: str,
        channel: str,
        asset_id: str = None,
        campaign_id: str = None,
        target_audience: str = None,
        claimed_rate: str = None,
    ) -> dict:
        findings = []
        content_lower = content.lower()

        # 1. Fair, clear, not misleading
        absolute_claims = ["best", "cheapest", "lowest", "guaranteed", "risk-free", "no risk"]
        for claim in absolute_claims:
            if claim in content_lower:
                findings.append({
                    "severity": "HIGH",
                    "category": "Misleading Claim",
                    "rule": "COBS 4.2.1",
                    "finding": f"Absolute claim '{claim}' requires substantiation or removal.",
                    "suggested_amendment": f"Replace '{claim}' with a qualified statement or verified comparison.",
                })

        # 2. APR for credit products
        credit_products = ["personal_loan", "credit_card", "mortgage", "overdraft"]
        if product_type in credit_products:
            if "representative" not in content_lower and "rep." not in content_lower:
                if "%" in content or claimed_rate:
                    findings.append({
                        "severity": "HIGH",
                        "category": "Missing Representative APR",
                        "rule": "COBS 4.5.2 / Consumer Credit Act",
                        "finding": "Rate mentioned without representative APR.",
                        "suggested_amendment": "Add: 'Representative X% APR (fixed/variable). [Full APR statement]'",
                    })

        # 3. Risk warnings
        if product_type == "mortgage":
            if "repossessed" not in content_lower:
                findings.append({
                    "severity": "HIGH",
                    "category": "Missing Mandatory Risk Warning",
                    "rule": "MCOB 3A.4",
                    "finding": "Mortgage promotion missing mandatory risk warning about repossession.",
                    "suggested_amendment": COMPLIANCE_PRECEDENTS["mortgage_risk_warning"],
                })

        # 4. Consumer Duty — urgency and behavioural bias
        urgency_terms = ["act now", "hurry", "running out", "don't miss", "last chance", "selling fast"]
        for term in urgency_terms:
            if term in content_lower:
                findings.append({
                    "severity": "MEDIUM",
                    "category": "Consumer Duty — Behavioural Bias",
                    "rule": "Consumer Duty FG22/5",
                    "finding": f"Urgency language '{term}' may exploit behavioural biases.",
                    "suggested_amendment": "Remove unless the offer genuinely expires. State the actual expiry date instead.",
                })

        # 5. Vulnerable customers
        complex_jargon = ["apr", "ltv", "lti", "bps", "erc", "svr"]
        jargon_found = [j for j in complex_jargon if f" {j}" in content_lower]
        if jargon_found:
            findings.append({
                "severity": "LOW",
                "category": "Vulnerable Customer — Plain Language",
                "rule": "FG21/1 Vulnerability Guidance",
                "finding": f"Financial jargon detected: {jargon_found}. May not be accessible to all customers.",
                "suggested_amendment": "Define abbreviations on first use or replace with plain language.",
            })

        # Search FCA knowledge base for relevant rules
        fca_matches = search_fca_rules(content[:300], category=None)

        high_count = sum(1 for f in findings if f["severity"] == "HIGH")
        medium_count = sum(1 for f in findings if f["severity"] == "MEDIUM")

        if high_count > 0:
            decision = "REJECTED_MINOR" if high_count <= 2 else "REJECTED_MAJOR"
        elif medium_count > 2:
            decision = "REJECTED_MINOR"
        elif medium_count > 0:
            decision = "APPROVED_WITH_AMENDMENTS"
        else:
            decision = "APPROVED"

        record = {
            "review_id": str(uuid.uuid4()),
            "asset_id": asset_id,
            "campaign_id": campaign_id,
            "product_type": product_type,
            "channel": channel,
            "decision": decision,
            "findings_count": {"HIGH": high_count, "MEDIUM": medium_count, "LOW": len(findings) - high_count - medium_count},
            "findings": findings,
            "relevant_fca_rules": [r.get("rule_id") for r in fca_matches[:3]],
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
        }
        save_compliance_record(record)
        return record

    def _verify_consumer_duty(
        self,
        content: str,
        product_type: str,
        target_segment: str = None,
        pricing_info: str = None,
    ) -> dict:
        outcomes = {
            "products_and_services": {
                "outcome": "Products & Services",
                "assessment": "Marketing should only promote products appropriate for the target segment.",
                "passed": True,
                "notes": [],
            },
            "price_and_value": {
                "outcome": "Price & Value",
                "assessment": "The promotion should not obscure total cost or create misleading value perceptions.",
                "passed": True,
                "notes": [],
            },
            "consumer_understanding": {
                "outcome": "Consumer Understanding",
                "assessment": "Communications should be clear and understandable by the target audience.",
                "passed": True,
                "notes": [],
            },
            "consumer_support": {
                "outcome": "Consumer Support",
                "assessment": "Customers must be able to get help and support easily.",
                "passed": True,
                "notes": [],
            },
        }

        content_lower = content.lower()

        # Price & Value checks
        if "fee" not in content_lower and "cost" not in content_lower and product_type in ["personal_loan", "credit_card"]:
            outcomes["price_and_value"]["passed"] = False
            outcomes["price_and_value"]["notes"].append("Total cost of credit not clearly stated.")

        # Consumer understanding
        complex_words = len([w for w in content.split() if len(w) > 12])
        if complex_words > 5:
            outcomes["consumer_understanding"]["notes"].append(f"{complex_words} complex words detected — simplify for broad audience.")

        # Consumer support
        if "contact" not in content_lower and "call" not in content_lower and "help" not in content_lower:
            outcomes["consumer_support"]["notes"].append("No support contact information visible. Consider adding.")

        overall_pass = all(o["passed"] for o in outcomes.values())

        return {
            "assessment_id": str(uuid.uuid4()),
            "product_type": product_type,
            "consumer_duty_outcomes": outcomes,
            "overall_result": "PASS" if overall_pass else "NEEDS_REVIEW",
            "assessed_at": datetime.now(timezone.utc).isoformat(),
        }

    def _validate_risk_warnings(self, content: str, product_type: str, channel: str = None) -> dict:
        required_warnings = {
            "mortgage": [
                {"warning": COMPLIANCE_PRECEDENTS["mortgage_risk_warning"], "check": "repossessed", "rule": "MCOB 3A.4"},
            ],
            "investment": [
                {"warning": COMPLIANCE_PRECEDENTS["investment_risk_warning"], "check": "go down as well as up", "rule": "COBS 4.7"},
                {"warning": COMPLIANCE_PRECEDENTS["past_performance"], "check": "past performance", "rule": "COBS 4.6"},
            ],
            "savings": [
                {"warning": COMPLIANCE_PRECEDENTS["fscs_protection"], "check": "fscs", "rule": "FSCS guidance"},
            ],
            "personal_loan": [
                {"warning": COMPLIANCE_PRECEDENTS["credit_eligibility"], "check": "subject to status", "rule": "CONC 3.5"},
            ],
            "credit_card": [
                {"warning": COMPLIANCE_PRECEDENTS["credit_eligibility"], "check": "subject to status", "rule": "CONC 3.5"},
            ],
        }

        content_lower = content.lower()
        required = required_warnings.get(product_type, [])
        results = []

        for req in required:
            present = req["check"].lower() in content_lower
            results.append({
                "warning_type": req["warning"][:80] + "...",
                "rule": req["rule"],
                "present": present,
                "status": "PASS" if present else "FAIL",
                "action": None if present else f"Add mandatory warning: '{req['warning']}'",
            })

        all_pass = all(r["status"] == "PASS" for r in results)

        return {
            "product_type": product_type,
            "channel": channel,
            "warnings_required": len(required),
            "warnings_found": sum(1 for r in results if r["status"] == "PASS"),
            "validation_result": "PASS" if all_pass else "FAIL",
            "details": results,
            "validated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _issue_compliance_certificate(
        self,
        asset_id: str,
        decision: str,
        reviewer_notes: str,
        campaign_id: str = None,
        conditions: list = None,
        expiry_date: str = None,
    ) -> dict:
        cert_id = f"COMP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        certificate = {
            "certificate_id": cert_id,
            "asset_id": asset_id,
            "campaign_id": campaign_id,
            "decision": decision,
            "reviewer_notes": reviewer_notes,
            "conditions": conditions or [],
            "approved": decision in ["APPROVED", "APPROVED_WITH_AMENDMENTS"],
            "expiry_date": expiry_date,
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "issued_by": "Compliance Agent (AI-assisted) — requires human sign-off for live use",
            "audit_trail_ref": f"AUD-{cert_id}",
            "fca_inspection_ready": True,
            "re_review_trigger": "Rate changes, T&C amendments, or product feature changes require re-review.",
        }
        save_compliance_record({"type": "certificate", **certificate})
        return certificate

    def _get_approved_disclaimer(self, disclaimer_type: str) -> dict:
        text = COMPLIANCE_PRECEDENTS.get(disclaimer_type, "Disclaimer not found.")
        return {
            "disclaimer_type": disclaimer_type,
            "approved_text": text,
            "usage_note": "This is a pre-approved disclaimer template. Do not modify without legal review.",
            "last_reviewed": "2026-01-01",
            "applicable_channels": "All customer-facing channels",
        }

    def _check_rate_accuracy(self, product_type: str, quoted_rate: str, campaign_id: str = None) -> dict:
        live_rates = {
            "mortgage_2yr_fixed": "4.19%",
            "mortgage_5yr_fixed": "4.39%",
            "personal_loan_typical": "6.9% APR",
            "credit_card_purchase": "22.9% APR",
            "savings_easy_access": "4.75% AER",
            "savings_1yr_fixed": "5.10% AER",
            "business_loan_typical": "7.5% over base rate",
        }

        rate_key = f"{product_type}_typical"
        live_rate = live_rates.get(rate_key, live_rates.get(product_type, "Rate not in system"))

        match = quoted_rate.replace(" ", "").lower() in live_rate.replace(" ", "").lower()

        return {
            "product_type": product_type,
            "quoted_rate": quoted_rate,
            "live_rate_from_system": live_rate,
            "rate_match": match,
            "status": "VERIFIED" if match else "MISMATCH — REVIEW REQUIRED",
            "action": None if match else f"Update quoted rate to match live rate: {live_rate}",
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "note": "Always verify against live pricing system before publication.",
        }
