"""
Strategy Agent — Phase 1: Annual planning, quarterly campaign sprints,
budget optimisation, and market analysis.
"""

import json
import uuid
from datetime import datetime, timezone

from agents.base_agent import AgentTool, BaseAgent
from tools.azure_cosmos_tools import save_campaign, list_campaigns
from tools.azure_search_tools import search_similar_campaigns


class StrategyAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Strategy Agent"

    @property
    def description(self) -> str:
        return (
            "Sets annual marketing strategy, quarterly campaign plans, budget allocation, "
            "and KPI targets. Analyses market data and competitor benchmarks to optimise "
            "investment decisions."
        )

    @property
    def phase(self) -> str:
        return "Phase 1 — Strategy & Annual Planning"

    @property
    def system_prompt(self) -> str:
        return """You are the Strategy Agent for a UK retail and commercial bank's marketing operations AI platform.

Your role covers Phase 1 of the marketing lifecycle:
- Annual marketing strategy: budgets, KPI targets, channel splits, product priorities
- Quarterly campaign planning: breaking annual plan into sprints, assigning owners, audience hypotheses
- Market analysis: competitor benchmarks, market share data, seasonal demand patterns
- Budget optimisation: AI-driven allocation across paid, owned, and earned media

You have deep knowledge of:
- UK banking regulations (FCA Consumer Duty, PRA guidelines)
- UK retail banking products: mortgages, personal loans, credit cards, savings, business banking
- Marketing KPIs: CPL, CPA, ROAS, LTV, NII (net interest income)
- Seasonal patterns: mortgage demand peaks spring/autumn, ISA season in March, back-to-school SME lending

When creating campaign plans, always:
1. Define clear SMART objectives
2. Specify target audience segments
3. Recommend channel mix with budget split
4. Set measurable KPIs with targets
5. Flag regulatory considerations upfront

Output structured, actionable plans with specific numbers and deadlines."""

    def _register_tools(self):
        self.register_tool(AgentTool(
            name="analyse_market_data",
            description="Analyse market trends, competitor activity, and product demand to inform strategy",
            parameters={
                "type": "object",
                "properties": {
                    "product_category": {
                        "type": "string",
                        "enum": ["mortgage", "personal_loan", "credit_card", "savings", "business_banking", "all"],
                        "description": "Product category to analyse",
                    },
                    "time_period": {
                        "type": "string",
                        "description": "Analysis period e.g. 'Q1 2026' or 'FY2025'",
                    },
                    "include_competitors": {
                        "type": "boolean",
                        "description": "Whether to include competitor benchmarks",
                    },
                },
                "required": ["product_category", "time_period"],
            },
            handler=self._analyse_market_data,
        ))

        self.register_tool(AgentTool(
            name="optimise_budget_allocation",
            description="Use AI-driven models to optimise channel budget split for maximum ROI",
            parameters={
                "type": "object",
                "properties": {
                    "total_budget": {
                        "type": "number",
                        "description": "Total annual/quarterly marketing budget in GBP",
                    },
                    "product_priorities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Ordered list of product priorities",
                    },
                    "risk_appetite": {
                        "type": "string",
                        "enum": ["conservative", "balanced", "growth"],
                        "description": "Investment risk appetite",
                    },
                },
                "required": ["total_budget", "product_priorities"],
            },
            handler=self._optimise_budget_allocation,
        ))

        self.register_tool(AgentTool(
            name="generate_campaign_calendar",
            description="Generate a 12-month campaign calendar aligned to product launches and seasonal demand",
            parameters={
                "type": "object",
                "properties": {
                    "planning_year": {
                        "type": "integer",
                        "description": "Year for the campaign calendar e.g. 2026",
                    },
                    "product_launches": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Planned product launches with dates",
                    },
                    "budget_by_quarter": {
                        "type": "object",
                        "description": "Budget allocation per quarter {Q1: 250000, Q2: 300000, ...}",
                    },
                },
                "required": ["planning_year"],
            },
            handler=self._generate_campaign_calendar,
        ))

        self.register_tool(AgentTool(
            name="create_campaign_brief",
            description="Create a structured campaign brief with objectives, audience, channels, and KPIs",
            parameters={
                "type": "object",
                "properties": {
                    "campaign_name": {"type": "string"},
                    "product": {"type": "string"},
                    "objective": {"type": "string"},
                    "target_segment": {"type": "string"},
                    "budget": {"type": "number"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "e.g. ['email', 'paid_search', 'social', 'direct_mail']",
                    },
                },
                "required": ["campaign_name", "product", "objective", "target_segment", "budget"],
            },
            handler=self._create_campaign_brief,
        ))

        self.register_tool(AgentTool(
            name="assess_performance_history",
            description="Review prior campaign performance to inform current strategy",
            parameters={
                "type": "object",
                "properties": {
                    "product_category": {"type": "string"},
                    "lookback_periods": {
                        "type": "integer",
                        "description": "Number of prior campaigns to review",
                        "default": 5,
                    },
                },
                "required": ["product_category"],
            },
            handler=self._assess_performance_history,
        ))

    # ─── Tool Implementations ────────────────────────────────────────────────

    def _analyse_market_data(self, product_category: str, time_period: str, include_competitors: bool = True) -> dict:
        market_data = {
            "mortgage": {
                "market_size_gbp_bn": 1.6e12,
                "yoy_growth_pct": 2.3,
                "avg_ltv_ratio": 72,
                "seasonal_peaks": ["March-May", "September-October"],
                "key_competitors": ["Nationwide", "Halifax", "Barclays", "HSBC"],
                "avg_cpa_gbp": 850,
                "avg_cpl_gbp": 45,
            },
            "personal_loan": {
                "market_size_gbp_bn": 2.1e11,
                "yoy_growth_pct": 4.1,
                "avg_loan_size_gbp": 8500,
                "seasonal_peaks": ["January (debt consolidation)", "June-August (home improvement)"],
                "key_competitors": ["Santander", "TSB", "Virgin Money"],
                "avg_cpa_gbp": 120,
                "avg_cpl_gbp": 18,
            },
            "credit_card": {
                "market_size_gbp_bn": 1.8e11,
                "yoy_growth_pct": 5.7,
                "avg_credit_limit_gbp": 4200,
                "seasonal_peaks": ["November-December (Christmas)", "March (ISA season balance transfer)"],
                "key_competitors": ["American Express", "Barclaycard", "MBNA"],
                "avg_cpa_gbp": 95,
                "avg_cpl_gbp": 12,
            },
            "savings": {
                "market_size_gbp_bn": 1.9e12,
                "yoy_growth_pct": 3.8,
                "avg_balance_gbp": 22000,
                "seasonal_peaks": ["March (ISA deadline)", "January (new year savings goals)"],
                "avg_cpa_gbp": 65,
                "avg_cpl_gbp": 8,
            },
            "business_banking": {
                "market_size_gbp_bn": 5.4e11,
                "yoy_growth_pct": 6.2,
                "avg_facility_gbp": 250000,
                "seasonal_peaks": ["Q1 (new financial year)", "Q3 (growth planning)"],
                "avg_cpa_gbp": 2400,
                "avg_cpl_gbp": 180,
            },
        }

        data = market_data.get(product_category, market_data)
        competitor_analysis = {}
        if include_competitors and product_category in market_data:
            competitor_analysis = {
                "share_of_voice": "Estimated 8.2% (below target of 12%)",
                "price_position": "Within top-3 rate on mortgages; mid-tier on personal loans",
                "digital_presence": "Competitor A increased paid search spend 34% YoY",
                "recommendations": [
                    "Increase SOV in mortgage in spring window",
                    "Price-led campaign for personal loans targeting debt consolidation",
                ],
            }

        return {
            "product_category": product_category,
            "time_period": time_period,
            "market_data": data,
            "competitor_analysis": competitor_analysis,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _optimise_budget_allocation(
        self,
        total_budget: float,
        product_priorities: list,
        risk_appetite: str = "balanced",
    ) -> dict:
        allocations = {
            "conservative": {"paid_search": 0.35, "email": 0.25, "display": 0.15, "social": 0.15, "direct_mail": 0.10},
            "balanced": {"paid_search": 0.30, "social": 0.25, "email": 0.20, "display": 0.15, "direct_mail": 0.10},
            "growth": {"social": 0.35, "paid_search": 0.25, "programmatic": 0.20, "email": 0.15, "direct_mail": 0.05},
        }
        channel_split = allocations.get(risk_appetite, allocations["balanced"])

        product_split = {}
        weight_total = len(product_priorities)
        for i, product in enumerate(product_priorities):
            weight = (weight_total - i) / sum(range(1, weight_total + 1))
            product_split[product] = round(total_budget * weight, 2)

        return {
            "total_budget_gbp": total_budget,
            "risk_appetite": risk_appetite,
            "channel_allocation": {
                channel: {"percentage": pct * 100, "gbp": round(total_budget * pct, 2)}
                for channel, pct in channel_split.items()
            },
            "product_allocation": product_split,
            "expected_metrics": {
                "estimated_total_leads": int(total_budget / 35),
                "estimated_cpl_gbp": 35,
                "estimated_cpa_gbp": 280,
                "estimated_roas": 4.2,
            },
            "recommendations": [
                "Allocate 15% contingency for real-time opportunity activation",
                "Set monthly performance gates to rebalance channel spend",
                "Ringfence compliance-driven channels (email) for regulatory communications",
            ],
        }

    def _generate_campaign_calendar(
        self,
        planning_year: int,
        product_launches: list = None,
        budget_by_quarter: dict = None,
    ) -> dict:
        calendar = {
            "year": planning_year,
            "quarters": {
                "Q1": {
                    "months": "January–March",
                    "themes": ["New Year Financial Wellbeing", "ISA Season", "Spring Mortgage"],
                    "priority_products": ["savings", "mortgage", "personal_loan"],
                    "budget_gbp": (budget_by_quarter or {}).get("Q1", 0),
                    "campaigns": [
                        {"name": "ISA Season Push", "product": "savings", "channels": ["email", "paid_search", "social"], "start": f"{planning_year}-01-15", "end": f"{planning_year}-04-05"},
                        {"name": "Spring Mortgage", "product": "mortgage", "channels": ["paid_search", "display", "direct_mail"], "start": f"{planning_year}-02-01", "end": f"{planning_year}-05-31"},
                    ],
                },
                "Q2": {
                    "months": "April–June",
                    "themes": ["Home Improvement Loans", "Business Banking Growth"],
                    "priority_products": ["personal_loan", "business_banking"],
                    "budget_gbp": (budget_by_quarter or {}).get("Q2", 0),
                    "campaigns": [
                        {"name": "Home Improvement Loan", "product": "personal_loan", "channels": ["social", "email", "display"], "start": f"{planning_year}-04-01", "end": f"{planning_year}-06-30"},
                        {"name": "SME Growth Lending", "product": "business_banking", "channels": ["linkedin", "email", "direct_mail"], "start": f"{planning_year}-04-15", "end": f"{planning_year}-06-15"},
                    ],
                },
                "Q3": {
                    "months": "July–September",
                    "themes": ["Back to University", "Autumn Mortgage", "SME Planning"],
                    "priority_products": ["credit_card", "mortgage", "business_banking"],
                    "budget_gbp": (budget_by_quarter or {}).get("Q3", 0),
                    "campaigns": [
                        {"name": "Student Credit Card", "product": "credit_card", "channels": ["social", "display", "email"], "start": f"{planning_year}-07-15", "end": f"{planning_year}-09-30"},
                        {"name": "Autumn Mortgage", "product": "mortgage", "channels": ["paid_search", "email", "direct_mail"], "start": f"{planning_year}-08-01", "end": f"{planning_year}-10-31"},
                    ],
                },
                "Q4": {
                    "months": "October–December",
                    "themes": ["Christmas Credit", "Year-End Savings", "Business Year-End"],
                    "priority_products": ["credit_card", "savings", "business_banking"],
                    "budget_gbp": (budget_by_quarter or {}).get("Q4", 0),
                    "campaigns": [
                        {"name": "Christmas Credit Card", "product": "credit_card", "channels": ["social", "display", "email"], "start": f"{planning_year}-10-01", "end": f"{planning_year}-12-24"},
                        {"name": "Year-End Business Banking", "product": "business_banking", "channels": ["linkedin", "email", "direct_mail"], "start": f"{planning_year}-11-01", "end": f"{planning_year}-12-15"},
                    ],
                },
            },
            "product_launches": product_launches or [],
            "regulatory_dates": [
                {"date": f"{planning_year}-04-05", "event": "ISA deadline", "impact": "Savings campaigns must conclude"},
                {"date": f"{planning_year}-03-31", "event": "Financial year end", "impact": "Business banking push"},
            ],
        }
        return calendar

    def _create_campaign_brief(
        self,
        campaign_name: str,
        product: str,
        objective: str,
        target_segment: str,
        budget: float,
        start_date: str = None,
        end_date: str = None,
        channels: list = None,
    ) -> dict:
        brief = {
            "id": str(uuid.uuid4()),
            "campaign_name": campaign_name,
            "product": product,
            "objective": objective,
            "target_segment": target_segment,
            "budget_gbp": budget,
            "start_date": start_date or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "end_date": end_date,
            "channels": channels or ["email", "paid_search", "social"],
            "kpis": {
                "target_leads": int(budget / 35),
                "target_cpl_gbp": 35,
                "target_cpa_gbp": 280,
                "target_conversions": int(budget / 280),
            },
            "audience_hypothesis": f"Target {target_segment} customers likely to convert on {product} based on propensity modelling",
            "regulatory_considerations": [
                "FCA financial promotions sign-off required (COBS 4)",
                "Consumer Duty fair value assessment",
                "GDPR consent verification for all channels",
                "Vulnerable customer review",
            ],
            "status": "draft",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        saved = save_campaign(brief)
        return saved

    def _assess_performance_history(self, product_category: str, lookback_periods: int = 5) -> dict:
        past_campaigns = list_campaigns()
        product_campaigns = [c for c in past_campaigns if c.get("product") == product_category]
        similar = search_similar_campaigns(product_category, product_type=product_category)

        return {
            "product_category": product_category,
            "campaigns_found": len(product_campaigns),
            "performance_summary": {
                "avg_cpl_gbp": 38.5,
                "avg_cpa_gbp": 295,
                "avg_conversion_rate_pct": 13.0,
                "avg_roas": 3.8,
                "best_channel": "email",
                "worst_channel": "display",
                "best_season": "Q1 (ISA season for savings), Q2 (spring for mortgages)",
            },
            "insights": [
                "Email campaigns consistently outperform paid social on CPA by 32%",
                "Direct mail drives highest-value mortgage leads despite high CPL",
                "Social media most cost-effective for credit card awareness",
                "Compliance turnaround is biggest time-to-market constraint (avg 11 days)",
            ],
            "recommendations": [
                f"Increase email budget allocation for {product_category} by 15%",
                "Introduce pre-screening to reduce compliance turnaround from 11 to 4 days",
                "Build dynamic audience segments to improve CPL by estimated 20%",
            ],
            "similar_campaigns_from_search": similar[:3],
        }
