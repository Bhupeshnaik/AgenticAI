"""
Copywriting Agent — Phase 2a: Generates campaign copy across all channels,
A/B variants, tone-of-voice checks, and representative APR calculations.
"""

import uuid
from datetime import datetime, timezone

from agents.base_agent import AgentTool, BaseAgent
from tools.azure_cosmos_tools import get_campaign
from tools.azure_search_tools import search_fca_rules, index_campaign_content


class CopywritingAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Copywriting Agent"

    @property
    def description(self) -> str:
        return (
            "Generates campaign copy for all channels (email, social, display, SMS, direct mail, landing pages). "
            "Creates A/B test variants, adapts copy per channel, verifies tone of voice, "
            "and flags compliance concerns before formal review."
        )

    @property
    def phase(self) -> str:
        return "Phase 2a — Creative Briefing & Copywriting"

    @property
    def system_prompt(self) -> str:
        return """You are the Copywriting Agent for a UK retail bank's marketing AI platform.

Your role is to produce all campaign copy across every channel, aligned to:
- UK banking product specifics (mortgages, loans, credit cards, savings, business banking)
- FCA financial promotions rules (COBS 4 — fair, clear, not misleading)
- Consumer Duty requirements (fair value, good outcomes)
- Brand tone of voice (trustworthy, clear, human, confident — not jargon-heavy)

For every copy request, you MUST:
1. Generate copy variants for each channel requested
2. Include A/B test variants (minimum 3 headline variants, 2 body variants)
3. Verify representative APR is included where credit products are mentioned
4. Check copy for potential FCA concerns before finalising
5. Ensure all character limits are respected (SMS: 160 chars, Twitter: 280 chars)

Channel copy guidelines:
- EMAIL: Subject line (max 60 chars) + preheader (max 90 chars) + body + CTA
- SOCIAL FACEBOOK/INSTAGRAM: Hook in first line, max 125 chars before "more", strong visual CTA
- LINKEDIN: Professional tone, data-led, B2B for business banking
- DISPLAY ADS: Ultra-short — headline max 30 chars, body max 90 chars
- SMS: 160 chars max, no abbreviations (regulatory requirement), clear opt-out
- DIRECT MAIL: Personalised salutation, benefit-led opening, clear CTA, T&C summary
- LANDING PAGE: Hero headline (max 10 words), sub-headline, body paragraphs, CTA button text

Always end with a pre-compliance check summary flagging any potential issues."""

    def _register_tools(self):
        self.register_tool(AgentTool(
            name="generate_copy_variants",
            description="Generate copy for all specified channels with A/B test variants",
            parameters={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string", "description": "Campaign ID to generate copy for"},
                    "product": {"type": "string", "description": "e.g. 'mortgage', 'personal_loan', 'credit_card'"},
                    "key_benefit": {"type": "string", "description": "Primary benefit to lead with"},
                    "offer": {"type": "string", "description": "Specific offer e.g. '2.89% fixed rate for 2 years'"},
                    "target_audience": {"type": "string", "description": "Target segment description"},
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Channels to generate copy for",
                    },
                    "tone": {
                        "type": "string",
                        "enum": ["warm_empathetic", "confident_direct", "professional_b2b", "urgency_driven"],
                        "description": "Tone for this campaign",
                    },
                },
                "required": ["product", "key_benefit", "channels"],
            },
            handler=self._generate_copy_variants,
        ))

        self.register_tool(AgentTool(
            name="calculate_representative_apr",
            description="Calculate and format the representative APR statement for credit product promotions",
            parameters={
                "type": "object",
                "properties": {
                    "product_type": {
                        "type": "string",
                        "enum": ["personal_loan", "credit_card", "mortgage", "overdraft"],
                    },
                    "representative_rate": {"type": "number", "description": "Annual interest rate as percentage"},
                    "loan_amount": {"type": "number", "description": "Representative loan amount in GBP"},
                    "term_months": {"type": "integer", "description": "Loan term in months"},
                    "loan_type": {"type": "string", "enum": ["fixed", "variable"], "default": "fixed"},
                },
                "required": ["product_type", "representative_rate"],
            },
            handler=self._calculate_representative_apr,
        ))

        self.register_tool(AgentTool(
            name="adapt_copy_for_channel",
            description="Adapt master copy to a specific channel's requirements and character limits",
            parameters={
                "type": "object",
                "properties": {
                    "master_copy": {"type": "string", "description": "The master copy to adapt"},
                    "target_channel": {
                        "type": "string",
                        "enum": ["sms", "twitter", "display_ad", "email_subject", "branch_poster", "instagram_caption"],
                    },
                    "key_message": {"type": "string", "description": "Core message that must be retained"},
                },
                "required": ["master_copy", "target_channel"],
            },
            handler=self._adapt_copy_for_channel,
        ))

        self.register_tool(AgentTool(
            name="pre_screen_for_compliance",
            description="Pre-screen copy for common FCA compliance issues before formal review",
            parameters={
                "type": "object",
                "properties": {
                    "copy_text": {"type": "string", "description": "The copy text to screen"},
                    "product_type": {"type": "string", "description": "Financial product type"},
                    "channel": {"type": "string", "description": "Channel this copy will be used in"},
                },
                "required": ["copy_text", "product_type"],
            },
            handler=self._pre_screen_for_compliance,
        ))

        self.register_tool(AgentTool(
            name="generate_ab_test_plan",
            description="Generate a structured A/B test plan with hypotheses and success criteria",
            parameters={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "element_to_test": {
                        "type": "string",
                        "enum": ["subject_line", "headline", "cta", "hero_image", "send_time", "offer"],
                    },
                    "channel": {"type": "string"},
                    "target_metric": {"type": "string", "description": "e.g. 'open_rate', 'ctr', 'conversion_rate'"},
                    "audience_size": {"type": "integer"},
                },
                "required": ["element_to_test", "channel", "target_metric"],
            },
            handler=self._generate_ab_test_plan,
        ))

    # ─── Tool Implementations ────────────────────────────────────────────────

    def _generate_copy_variants(
        self,
        product: str,
        key_benefit: str,
        channels: list,
        campaign_id: str = None,
        offer: str = None,
        target_audience: str = None,
        tone: str = "confident_direct",
    ) -> dict:
        copy_deck = {
            "copy_id": str(uuid.uuid4()),
            "campaign_id": campaign_id,
            "product": product,
            "key_benefit": key_benefit,
            "offer": offer,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "channels": {},
        }

        offer_str = f" — {offer}" if offer else ""

        if "email" in channels:
            copy_deck["channels"]["email"] = {
                "subject_line_variants": [
                    f"Your {product.replace('_', ' ')} rate just got better{offer_str}",
                    f"Exclusive: {key_benefit} — only for you",
                    f"We've found a better {product.replace('_', ' ')} for you",
                    f"Don't miss out: {offer or key_benefit}",
                    f"Is your money working as hard as you are?",
                ],
                "preheader_variants": [
                    f"See how we can help you {key_benefit.lower()} today.",
                    f"Find out why thousands of customers switched to us.",
                ],
                "body_variant_a": (
                    f"Dear [First Name],\n\n"
                    f"We know choosing the right {product.replace('_', ' ')} matters. "
                    f"That's why we've designed an offer that puts you first.\n\n"
                    f"**{key_benefit}**{offer_str}\n\n"
                    f"Apply in minutes online — no hidden fees, no surprises.\n\n"
                    f"[Apply Now]\n\n"
                    f"Representative APR: [APR_PLACEHOLDER]. T&Cs apply."
                ),
                "body_variant_b": (
                    f"Hi [First Name],\n\n"
                    f"We've run the numbers — and we think you could be getting more from your {product.replace('_', ' ')}.\n\n"
                    f"Here's what we're offering:\n"
                    f"✓ {key_benefit}\n"
                    f"✓ No arrangement fees\n"
                    f"✓ Quick online decision\n\n"
                    f"[Get Started Today]\n\n"
                    f"Representative APR: [APR_PLACEHOLDER]. Subject to status."
                ),
                "cta_variants": ["Apply Now", "Get Your Rate", "See If You Qualify", "Claim Your Offer"],
            }

        if "sms" in channels:
            sms_base = f"[Bank]: {key_benefit}{offer_str}. Apply: [LINK] Opt out: STOP"
            copy_deck["channels"]["sms"] = {
                "variant_a": sms_base[:160],
                "variant_b": f"[Bank]: Exclusive {product.replace('_', ' ')} offer for you. {offer or key_benefit}. [LINK] Stop: STOP"[:160],
                "character_count_a": len(sms_base[:160]),
                "note": "GDPR: Only sent to opted-in customers. Opt-out mechanism mandatory.",
            }

        if "social" in channels or "facebook" in channels or "instagram" in channels:
            copy_deck["channels"]["social"] = {
                "facebook": {
                    "headline_variants": [
                        f"{key_benefit} — Is it time to switch?",
                        f"Discover our award-winning {product.replace('_', ' ')}",
                        f"{offer or key_benefit} — apply today",
                    ],
                    "body": f"Thousands of customers have already made the switch. Find out why. {offer_str}\n\n✅ Quick online application\n✅ Decision in minutes\n✅ UK-based support\n\nRepresentative APR: [APR_PLACEHOLDER]. Subject to status and eligibility.",
                    "cta_button": "Learn More",
                },
                "instagram": {
                    "caption_variant_a": f"💰 {key_benefit}. Because your money should work harder for you.{offer_str}\n\nLink in bio. Representative APR [APR_PLACEHOLDER]. T&Cs apply. #PersonalFinance #Banking",
                    "caption_variant_b": f"Ready to take control of your finances? 🏦 {offer or key_benefit}\n\nApply online in minutes. Link in bio.\n\n#FinancialWellbeing #UKBanking",
                },
                "linkedin": {
                    "body": f"Is your business getting the banking support it deserves?\n\nWe're helping UK businesses {key_benefit.lower()}. {offer_str}\n\nWith dedicated relationship managers and flexible facilities tailored to your sector, we're built for business growth.\n\n→ Speak to a specialist today\n\n[Learn More]\n\n#BusinessBanking #SME #UKBusiness",
                },
            }

        if "display" in channels:
            copy_deck["channels"]["display"] = {
                "headline_variants": [
                    key_benefit[:30],
                    (offer or key_benefit)[:30],
                    f"Better {product.replace('_', ' ')}"[:30],
                ],
                "body_variants": [
                    f"Apply online in minutes. {offer_str}"[:90],
                    f"No hidden fees. Quick decision."[:90],
                ],
                "cta": "Apply Now",
                "disclaimer": "Representative APR [APR_PLACEHOLDER]. Subject to status.",
            }

        if "direct_mail" in channels:
            copy_deck["channels"]["direct_mail"] = {
                "letter_variant_a": (
                    f"Dear [Full Name],\n\n"
                    f"As a valued customer, we want to make sure you're getting the best from your banking.\n\n"
                    f"We've identified an opportunity that could help you {key_benefit.lower()}.\n\n"
                    f"**Our {product.replace('_', ' ')} offer:**\n{offer_str}\n\n"
                    f"To find out if you're eligible, simply call [PHONE] or visit [URL] and quote reference [REF_CODE].\n\n"
                    f"Yours sincerely,\n[RM Name]\n\n"
                    f"Representative APR: [APR_PLACEHOLDER]. This offer is available until [EXPIRY_DATE]. Subject to status."
                ),
            }

        if "landing_page" in channels:
            copy_deck["channels"]["landing_page"] = {
                "hero_headline_variants": [
                    key_benefit[:60],
                    f"{product.replace('_', ' ').title()} that works for you"[:60],
                    (offer or key_benefit)[:60],
                ],
                "sub_headline": f"Apply online in minutes. Quick decision. No hidden fees.",
                "body_paragraphs": [
                    f"We know that finding the right {product.replace('_', ' ')} can feel overwhelming. That's why we've made it simple.",
                    f"Our {product.replace('_', ' ')} gives you {key_benefit.lower()}, with the support of our UK-based team every step of the way.",
                    "Thousands of customers have already made the switch. Here's what they said about us.",
                ],
                "cta_primary": "Apply Now — it only takes 10 minutes",
                "cta_secondary": "See rates and eligibility",
                "form_fields": ["First name", "Last name", "Email", "Phone", "Postcode", "Product interest"],
                "seo_title": f"{product.replace('_', ' ').title()} — {key_benefit[:40]} | [Bank Name]",
                "seo_description": f"Apply for our {product.replace('_', ' ')} today. {key_benefit}. {offer_str}. Quick online application.",
            }

        # Index in search
        if campaign_id:
            index_campaign_content(campaign_id, "copy_deck", str(copy_deck), {"product": product})

        return copy_deck

    def _calculate_representative_apr(
        self,
        product_type: str,
        representative_rate: float,
        loan_amount: float = None,
        term_months: int = None,
        loan_type: str = "fixed",
    ) -> dict:
        defaults = {
            "personal_loan": {"amount": 10000, "term": 60},
            "credit_card": {"amount": 1200, "term": 12},
            "mortgage": {"amount": 200000, "term": 300},
            "overdraft": {"amount": 1000, "term": 12},
        }
        d = defaults.get(product_type, {"amount": 10000, "term": 60})
        amount = loan_amount or d["amount"]
        term = term_months or d["term"]

        # Simple monthly payment calculation
        monthly_rate = representative_rate / 100 / 12
        if monthly_rate > 0:
            monthly_payment = amount * (monthly_rate * (1 + monthly_rate) ** term) / ((1 + monthly_rate) ** term - 1)
        else:
            monthly_payment = amount / term
        total_repayable = monthly_payment * term
        total_interest = total_repayable - amount

        legal_statement = (
            f"Representative {representative_rate}% APR ({loan_type}). "
            f"Based on a loan of £{amount:,.0f} over {term // 12} year{'s' if term // 12 != 1 else ''}. "
            f"Monthly repayment: £{monthly_payment:,.2f}. "
            f"Total amount repayable: £{total_repayable:,.2f} (including £{total_interest:,.2f} interest). "
            f"Subject to status and eligibility."
        )

        return {
            "product_type": product_type,
            "representative_apr_pct": representative_rate,
            "loan_type": loan_type,
            "assumed_loan_amount_gbp": amount,
            "assumed_term_months": term,
            "monthly_repayment_gbp": round(monthly_payment, 2),
            "total_repayable_gbp": round(total_repayable, 2),
            "total_interest_gbp": round(total_interest, 2),
            "legal_statement": legal_statement,
            "fca_requirement": "Must be displayed with at least equal prominence to the advertised rate",
        }

    def _adapt_copy_for_channel(self, master_copy: str, target_channel: str, key_message: str = None) -> dict:
        limits = {
            "sms": 160,
            "twitter": 280,
            "display_ad": 90,
            "email_subject": 60,
            "branch_poster": 25,
            "instagram_caption": 2200,
        }
        limit = limits.get(target_channel, 300)
        words = master_copy.split()
        adapted = master_copy[:limit].rsplit(" ", 1)[0] if len(master_copy) > limit else master_copy
        if key_message and key_message not in adapted:
            adapted = key_message[:limit]

        return {
            "target_channel": target_channel,
            "character_limit": limit,
            "adapted_copy": adapted,
            "character_count": len(adapted),
            "within_limit": len(adapted) <= limit,
            "truncated": len(master_copy) > limit,
        }

    def _pre_screen_for_compliance(self, copy_text: str, product_type: str, channel: str = None) -> dict:
        issues = []
        warnings = []
        copy_lower = copy_text.lower()

        credit_products = ["personal_loan", "credit_card", "mortgage", "overdraft"]
        if product_type in credit_products:
            if "apr" not in copy_lower and "%" not in copy_text:
                issues.append({
                    "severity": "HIGH",
                    "rule": "COBS 4.5.2",
                    "issue": "No representative APR found. Credit promotions must include a representative APR.",
                    "action": "Add representative APR statement with equal prominence to the advertised rate.",
                })

        misleading_terms = ["guaranteed", "best rate", "lowest rate", "risk-free", "guaranteed approval"]
        for term in misleading_terms:
            if term in copy_lower:
                issues.append({
                    "severity": "HIGH",
                    "rule": "COBS 4.2.1",
                    "issue": f"Potentially misleading claim: '{term}'",
                    "action": f"Remove or qualify '{term}' — absolute claims must be verifiable and not mislead.",
                })

        urgency_terms = ["limited time", "act now", "hurry", "don't miss out", "last chance"]
        for term in urgency_terms:
            if term in copy_lower:
                warnings.append({
                    "severity": "MEDIUM",
                    "rule": "Consumer Duty 2023",
                    "issue": f"Urgency language detected: '{term}'",
                    "action": "Ensure urgency is genuine and not exploiting behavioural biases. Consider removing if artificial.",
                })

        if product_type == "mortgage" and "repossess" not in copy_lower:
            issues.append({
                "severity": "HIGH",
                "rule": "COBS 4.7",
                "issue": "Mortgage promotion missing mandatory risk warning.",
                "action": "Add: 'Your home may be repossessed if you do not keep up repayments on your mortgage.'",
            })

        fca_rules = search_fca_rules(copy_text[:200])
        relevant_rules = [r["rule_id"] for r in fca_rules[:3]]

        return {
            "copy_excerpt": copy_text[:200],
            "product_type": product_type,
            "channel": channel,
            "pre_screen_result": "FAIL" if issues else ("WARN" if warnings else "PASS"),
            "issues": issues,
            "warnings": warnings,
            "relevant_fca_rules": relevant_rules,
            "recommendation": (
                "Do not submit to compliance without resolving HIGH severity issues."
                if issues else
                "Review MEDIUM warnings before submission. Ready for compliance pre-review."
            ),
            "screened_at": datetime.now(timezone.utc).isoformat(),
        }

    def _generate_ab_test_plan(
        self,
        element_to_test: str,
        channel: str,
        target_metric: str,
        campaign_id: str = None,
        audience_size: int = 50000,
    ) -> dict:
        sample_per_variant = audience_size // 2
        min_detectable_effect = {
            "open_rate": 2.0,
            "ctr": 0.5,
            "conversion_rate": 0.3,
        }.get(target_metric, 1.0)

        return {
            "test_id": str(uuid.uuid4()),
            "campaign_id": campaign_id,
            "element_to_test": element_to_test,
            "channel": channel,
            "target_metric": target_metric,
            "hypothesis": f"Changing {element_to_test} will improve {target_metric} by at least {min_detectable_effect}%",
            "variants": {
                "control": f"Original {element_to_test} (Control)",
                "variant_a": f"Alternative {element_to_test} — Variant A",
            },
            "audience_split": {"control": 50, "variant_a": 50},
            "sample_size_per_variant": sample_per_variant,
            "minimum_detectable_effect_pct": min_detectable_effect,
            "confidence_level": 95,
            "estimated_runtime_days": max(7, int(50000 / audience_size * 14)),
            "success_criteria": f"{target_metric} improvement >= {min_detectable_effect}% at 95% confidence",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
