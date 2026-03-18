"""
Analytics Agent — Phase 8: Campaign performance reporting, multi-touch attribution,
ROI analysis, and data-driven budget recommendations.
"""

import uuid
from datetime import datetime, timezone

from agents.base_agent import AgentTool, BaseAgent
from tools.azure_cosmos_tools import list_campaigns, list_leads


class AnalyticsAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Analytics Agent"

    @property
    def description(self) -> str:
        return (
            "Consolidates campaign performance data across all channels, applies multi-touch attribution "
            "models, calculates true ROI by campaign and channel, and generates actionable insights for "
            "budget reallocation. Closes the loop between marketing spend and originated revenue."
        )

    @property
    def phase(self) -> str:
        return "Phase 8 — Measurement, Attribution & Optimisation"

    @property
    def system_prompt(self) -> str:
        return """You are the Analytics Agent for a UK retail bank's marketing AI platform.

You solve the most critical measurement problem in the as-is process: the broken attribution chain
where marketing spend cannot be linked to originated revenue.

YOUR CAPABILITIES:

1. CROSS-CHANNEL REPORTING: Pull and consolidate metrics from:
   - Email (Salesforce Marketing Cloud / Adobe Campaign)
   - Paid media (Google Ads, Meta Ads Manager, DV360)
   - Web analytics (GA4 / Adobe Analytics)
   - CRM (Salesforce — leads, opportunities, conversions)
   - Call centre (interaction logs with campaign tags)
   - Branch (enquiry data)

2. MULTI-TOUCH ATTRIBUTION: Three attribution models:
   - Last-touch (current as-is baseline)
   - Linear (equal credit across all touchpoints)
   - Data-driven / Shapley value (ML-based, most accurate)
   The data-driven model shows that display campaigns are systematically undervalued
   in last-touch models by an average of 35%.

3. CLOSED-LOOP ATTRIBUTION: Link marketing leads (CRM) to originated products (core banking)
   via:
   - Application reference matching
   - Customer ID reconciliation
   - Product opening date vs. campaign date range

4. ROI CALCULATION: True marketing ROI using:
   - Marketing-attributed originations (by product, by channel)
   - Net Interest Income (NII) from originated products over 24 months
   - Total marketing cost (media, production, compliance, people)

5. PREDICTIVE OPTIMISATION: AI-driven budget recommendations for next quarter
   based on channel efficiency, market seasonality, and portfolio targets.

Always present findings with: the metric, vs target, vs prior period, and a recommended action."""

    def _register_tools(self):
        self.register_tool(AgentTool(
            name="aggregate_channel_metrics",
            description="Pull and consolidate performance metrics across all campaign channels",
            parameters={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "date_range": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string"},
                            "end_date": {"type": "string"},
                        },
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Channels to include — omit for all",
                    },
                },
                "required": ["campaign_id"],
            },
            handler=self._aggregate_channel_metrics,
        ))

        self.register_tool(AgentTool(
            name="calculate_attribution",
            description="Apply multi-touch attribution models to distribute conversion credit across touchpoints",
            parameters={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "attribution_model": {
                        "type": "string",
                        "enum": ["last_touch", "first_touch", "linear", "time_decay", "data_driven"],
                        "default": "data_driven",
                    },
                    "conversion_event": {
                        "type": "string",
                        "enum": ["lead", "application_started", "application_completed", "product_opened"],
                        "default": "product_opened",
                    },
                },
                "required": ["campaign_id"],
            },
            handler=self._calculate_attribution,
        ))

        self.register_tool(AgentTool(
            name="calculate_campaign_roi",
            description="Calculate true marketing ROI linking spend to originated product revenue",
            parameters={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "include_nii_projection": {
                        "type": "boolean",
                        "description": "Include 24-month NII projection from originated products",
                        "default": True,
                    },
                    "include_cost_breakdown": {"type": "boolean", "default": True},
                },
                "required": ["campaign_id"],
            },
            handler=self._calculate_campaign_roi,
        ))

        self.register_tool(AgentTool(
            name="generate_performance_report",
            description="Generate a complete campaign performance report for stakeholders",
            parameters={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "report_type": {
                        "type": "string",
                        "enum": ["in_flight_weekly", "end_of_campaign", "cmo_executive_summary", "channel_deep_dive"],
                    },
                    "audience": {
                        "type": "string",
                        "enum": ["cmo", "campaign_manager", "channel_team", "finance"],
                        "default": "campaign_manager",
                    },
                },
                "required": ["campaign_id", "report_type"],
            },
            handler=self._generate_performance_report,
        ))

        self.register_tool(AgentTool(
            name="recommend_budget_reallocation",
            description="AI-driven recommendations for budget reallocation based on performance data",
            parameters={
                "type": "object",
                "properties": {
                    "current_budget_by_channel": {
                        "type": "object",
                        "description": "Current budget allocation {channel: gbp_amount}",
                    },
                    "performance_data": {
                        "type": "object",
                        "description": "Performance metrics by channel",
                    },
                    "optimisation_objective": {
                        "type": "string",
                        "enum": ["minimise_cpa", "maximise_volume", "maximise_revenue", "maximise_roas"],
                        "default": "maximise_revenue",
                    },
                    "total_budget_gbp": {"type": "number"},
                },
                "required": ["total_budget_gbp", "optimisation_objective"],
            },
            handler=self._recommend_budget_reallocation,
        ))

        self.register_tool(AgentTool(
            name="measure_incrementality",
            description="Estimate campaign incrementality — would customers have converted without the campaign?",
            parameters={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "holdout_group_size_pct": {
                        "type": "number",
                        "description": "Percentage of audience held out as control group",
                        "default": 10,
                    },
                },
                "required": ["campaign_id"],
            },
            handler=self._measure_incrementality,
        ))

    # ─── Tool Implementations ────────────────────────────────────────────────

    def _aggregate_channel_metrics(
        self,
        campaign_id: str,
        date_range: dict = None,
        channels: list = None,
    ) -> dict:
        # Simulated consolidated metrics across all channels
        all_channel_metrics = {
            "email": {
                "sends": 125000,
                "deliveries": 122500,
                "opens": 28175,
                "clicks": 3930,
                "conversions": 487,
                "revenue_attributed_gbp": 2850000,
                "cost_gbp": 2500,
                "cpl_gbp": 5.13,
                "cpa_gbp": 5.13,
                "roas": 1140.0,
            },
            "paid_search": {
                "impressions": 850000,
                "clicks": 21250,
                "ctr_pct": 2.5,
                "conversions": 638,
                "revenue_attributed_gbp": 4850000,
                "cost_gbp": 85000,
                "cpl_gbp": 133.23,
                "cpa_gbp": 133.23,
                "roas": 57.1,
            },
            "paid_social": {
                "impressions": 2100000,
                "clicks": 14700,
                "ctr_pct": 0.7,
                "conversions": 353,
                "revenue_attributed_gbp": 1820000,
                "cost_gbp": 35000,
                "cpl_gbp": 99.15,
                "cpa_gbp": 99.15,
                "roas": 52.0,
            },
            "programmatic_display": {
                "impressions": 5200000,
                "clicks": 10400,
                "ctr_pct": 0.2,
                "conversions": 156,
                "revenue_attributed_gbp": 780000,
                "cost_gbp": 28000,
                "cpl_gbp": 179.49,
                "cpa_gbp": 179.49,
                "roas": 27.9,
            },
            "direct_mail": {
                "pieces_sent": 45000,
                "responses": 1350,
                "response_rate_pct": 3.0,
                "conversions": 405,
                "revenue_attributed_gbp": 6200000,
                "cost_gbp": 67500,
                "cpl_gbp": 50.0,
                "cpa_gbp": 166.67,
                "roas": 91.9,
            },
        }

        if channels:
            filtered = {k: v for k, v in all_channel_metrics.items() if k in channels}
        else:
            filtered = all_channel_metrics

        # Aggregate totals
        total_cost = sum(v["cost_gbp"] for v in filtered.values())
        total_revenue = sum(v["revenue_attributed_gbp"] for v in filtered.values())
        total_conversions = sum(v["conversions"] for v in filtered.values())

        return {
            "campaign_id": campaign_id,
            "date_range": date_range or {"start": "Campaign start", "end": "Campaign end"},
            "channel_metrics": filtered,
            "totals": {
                "total_cost_gbp": total_cost,
                "total_revenue_attributed_gbp": total_revenue,
                "total_conversions": total_conversions,
                "blended_cpa_gbp": round(total_cost / total_conversions, 2) if total_conversions else 0,
                "blended_roas": round(total_revenue / total_cost, 1) if total_cost else 0,
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _calculate_attribution(
        self,
        campaign_id: str,
        attribution_model: str = "data_driven",
        conversion_event: str = "product_opened",
    ) -> dict:
        # Simulated attribution results
        last_touch = {"email": 0.05, "paid_search": 0.35, "paid_social": 0.12, "display": 0.02, "direct_mail": 0.18, "branch": 0.28}
        linear = {"email": 0.15, "paid_search": 0.25, "paid_social": 0.18, "display": 0.10, "direct_mail": 0.17, "branch": 0.15}
        data_driven = {"email": 0.18, "paid_search": 0.22, "paid_social": 0.19, "display": 0.14, "direct_mail": 0.16, "branch": 0.11}

        models = {"last_touch": last_touch, "linear": linear, "data_driven": data_driven}
        selected = models.get(attribution_model, data_driven)

        total_conversions = 2039
        attribution_by_channel = {
            channel: {
                "credit_pct": round(pct * 100, 1),
                "attributed_conversions": int(total_conversions * pct),
                "attributed_revenue_gbp": int(total_conversions * pct * 8200),
            }
            for channel, pct in selected.items()
        }

        insights = []
        if attribution_model == "data_driven":
            insights = [
                "Display advertising is undervalued by last-touch model by 600% — it assists 14% of all conversions but gets 2% credit under last-touch",
                "Email has outsized early-journey impact — opens are 5x more likely in first 24 hours of retargeting activation",
                "Branch interactions convert 3.2x better than digital channels when preceded by 2+ digital touchpoints",
                "Direct mail drives the highest-value customers (avg £152k mortgage vs £98k digital-only)",
            ]

        return {
            "campaign_id": campaign_id,
            "attribution_model": attribution_model,
            "conversion_event": conversion_event,
            "total_conversions": total_conversions,
            "attribution_by_channel": attribution_by_channel,
            "model_comparison": {
                "last_touch_winner": "paid_search",
                "data_driven_winner": "email",
                "biggest_discrepancy": "display — undervalued by 7x in last-touch vs data-driven",
            },
            "insights": insights,
            "recommendation": "Switch from last-touch to data-driven attribution for budget decisions — estimated 18% CPA improvement",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _calculate_campaign_roi(
        self,
        campaign_id: str,
        include_nii_projection: bool = True,
        include_cost_breakdown: bool = True,
    ) -> dict:
        cost_breakdown = {
            "media_spend_gbp": 215500,
            "content_and_creative_gbp": 28000,
            "compliance_review_gbp": 4500,
            "data_and_analytics_gbp": 3200,
            "people_cost_gbp": 15000,
            "fulfilment_direct_mail_gbp": 12000,
            "technology_tools_gbp": 2800,
        }
        total_cost = sum(cost_breakdown.values())

        originated_products = {
            "mortgages_originated": 48,
            "avg_mortgage_value_gbp": 198000,
            "personal_loans_originated": 312,
            "avg_loan_value_gbp": 9800,
            "credit_cards_issued": 580,
            "avg_credit_limit_gbp": 4200,
            "savings_accounts_opened": 890,
            "avg_savings_balance_gbp": 18500,
        }

        revenue = {
            "mortgage_revenue_attributed_gbp": originated_products["mortgages_originated"] * originated_products["avg_mortgage_value_gbp"],
            "loan_revenue_attributed_gbp": originated_products["personal_loans_originated"] * originated_products["avg_loan_value_gbp"],
            "credit_card_revenue_attributed_gbp": originated_products["credit_cards_issued"] * originated_products["avg_credit_limit_gbp"],
            "savings_revenue_attributed_gbp": originated_products["savings_accounts_opened"] * originated_products["avg_savings_balance_gbp"],
        }
        total_revenue = sum(revenue.values())

        nii_projection = None
        if include_nii_projection:
            nii_projection = {
                "24_month_nii_gbp": total_revenue * 0.028,
                "assumption": "2.8% average NII margin on originated balances over 24 months",
                "lifetime_value_estimate_gbp": total_revenue * 0.08,
                "payback_period_months": round(total_cost / (total_revenue * 0.028 / 24), 1),
            }

        return {
            "campaign_id": campaign_id,
            "total_marketing_cost_gbp": total_cost,
            "cost_breakdown": cost_breakdown if include_cost_breakdown else None,
            "originated_products": originated_products,
            "revenue_attributed": revenue,
            "total_revenue_attributed_gbp": total_revenue,
            "roi_pct": round((total_revenue - total_cost) / total_cost * 100, 1),
            "roas": round(total_revenue / total_cost, 1),
            "nii_projection": nii_projection,
            "vs_target": {
                "target_roas": 4.0,
                "actual_roas": round(total_revenue / total_cost, 1),
                "target_met": total_revenue / total_cost >= 4.0,
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _generate_performance_report(
        self,
        campaign_id: str,
        report_type: str,
        audience: str = "campaign_manager",
    ) -> dict:
        base_metrics = {
            "campaign_id": campaign_id,
            "report_type": report_type,
            "audience": audience,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        if report_type == "cmo_executive_summary":
            base_metrics["report"] = {
                "headline_result": "Campaign exceeded targets — 127% of conversion target achieved",
                "key_metrics": {
                    "Total Spend": "£281,000",
                    "Total Originations": "1,830 products",
                    "Marketing-Attributed Revenue": "£16.7M",
                    "ROAS": "59.4x",
                    "CPA": "£153.55",
                    "vs. Target CPA (£280)": "+83% better",
                },
                "what_worked": ["Email performance strongest on CPA (£5.13)", "Direct mail drove highest-value mortgage leads", "Personalised nurture journey 89% better than generic"],
                "what_to_improve": ["Display attribution still on last-touch — switch to data-driven", "Branch attribution largely manual — needs digital tagging"],
                "recommendation": "Increase email and nurture investment by 20% in Q3. Redirect 30% of programmatic display to paid social.",
            }

        elif report_type == "in_flight_weekly":
            base_metrics["report"] = {
                "week_number": 3,
                "pacing": "ON_TRACK — 94% of budget spent, 108% of conversions achieved",
                "alerts": ["Email bounce rate at 2.0% threshold — list clean required", "Paid social CPA 40% below target — increase budget"],
                "optimisation_actions_this_week": [
                    "Paused 3 underperforming display creative variants",
                    "Increased Meta budget by £8,000 — CPA £172 vs £280 target",
                    "Refreshed email subject line for segment C — open rate improved from 18% to 26%",
                ],
                "forecast_to_end": "Projected 115% of conversion target at current trajectory",
            }

        elif report_type == "end_of_campaign":
            base_metrics["report"] = {
                "summary": "Campaign delivered 127% of target at 45% lower CPA than target",
                "full_metrics": "See aggregated channel metrics report",
                "attribution_model": "Data-driven (Shapley value)",
                "lessons_learned": [
                    "Personalised nurture doubled conversion rate — apply to all future campaigns",
                    "Direct mail lead time (3 weeks) requires earlier production trigger",
                    "Compliance turnaround reduced from 11 days to 4 days using AI pre-screening",
                ],
                "next_campaign_recommendations": [
                    "Increase email and nurture budget 20%",
                    "Reduce programmatic display by 30% (high CPM, lower attributed contribution)",
                    "Introduce retargeting audience sync on Day 1 (vs Day 3 this campaign)",
                ],
            }

        return base_metrics

    def _recommend_budget_reallocation(
        self,
        total_budget_gbp: float,
        optimisation_objective: str = "maximise_revenue",
        current_budget_by_channel: dict = None,
        performance_data: dict = None,
    ) -> dict:
        # Channel efficiency scores for UK banking (ROAS-based)
        channel_efficiency = {
            "email": {"roas": 1140, "scalability": "LOW — limited by list size and consent"},
            "paid_search": {"roas": 57, "scalability": "HIGH — scale with budget"},
            "paid_social": {"roas": 52, "scalability": "HIGH — strong performance, expand lookalikes"},
            "direct_mail": {"roas": 92, "scalability": "MEDIUM — 3-week lead time"},
            "programmatic_display": {"roas": 28, "scalability": "HIGH — but brand, not direct response"},
            "linkedin": {"roas": 38, "scalability": "MEDIUM — B2B only, high CPM"},
        }

        objectives = {
            "minimise_cpa": {"email": 0.05, "paid_search": 0.40, "paid_social": 0.30, "direct_mail": 0.15, "programmatic_display": 0.05, "linkedin": 0.05},
            "maximise_volume": {"email": 0.08, "paid_search": 0.35, "paid_social": 0.35, "direct_mail": 0.10, "programmatic_display": 0.07, "linkedin": 0.05},
            "maximise_revenue": {"email": 0.10, "paid_search": 0.30, "paid_social": 0.25, "direct_mail": 0.22, "programmatic_display": 0.05, "linkedin": 0.08},
            "maximise_roas": {"email": 0.15, "paid_search": 0.35, "paid_social": 0.28, "direct_mail": 0.12, "programmatic_display": 0.03, "linkedin": 0.07},
        }

        recommended_split = objectives.get(optimisation_objective, objectives["maximise_revenue"])

        recommendations = {
            channel: {
                "recommended_budget_gbp": round(total_budget_gbp * pct, 2),
                "current_budget_gbp": (current_budget_by_channel or {}).get(channel, 0),
                "change_pct": round(
                    ((total_budget_gbp * pct) / max((current_budget_by_channel or {}).get(channel, 1), 1) - 1) * 100, 1
                ),
                "efficiency": channel_efficiency.get(channel, {}).get("roas", "N/A"),
                "scalability": channel_efficiency.get(channel, {}).get("scalability", "N/A"),
            }
            for channel, pct in recommended_split.items()
        }

        return {
            "optimisation_objective": optimisation_objective,
            "total_budget_gbp": total_budget_gbp,
            "recommended_allocation": recommendations,
            "expected_improvement": {
                "cpa_reduction_pct": 18,
                "volume_increase_pct": 22,
                "revenue_increase_pct": 15,
            },
            "key_moves": [
                "Increase paid social spend (high ROAS, highly scalable)",
                "Maintain direct mail for high-value mortgage segment",
                "Reduce programmatic display to brand-only role",
                "Expand email list via consent-gathering programme",
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _measure_incrementality(self, campaign_id: str, holdout_group_size_pct: float = 10) -> dict:
        return {
            "campaign_id": campaign_id,
            "methodology": "Randomised holdout group — 10% of eligible audience not contacted",
            "holdout_size_pct": holdout_group_size_pct,
            "results": {
                "treatment_group_conversion_rate_pct": 7.2,
                "holdout_group_conversion_rate_pct": 3.1,
                "incremental_conversion_rate_pct": 4.1,
                "incrementality_pct": 57,
                "organic_conversions_pct": 43,
            },
            "interpretation": (
                "57% of conversions were incremental (caused by the campaign). "
                "43% would have converted anyway through organic search, direct, or branch. "
                "The campaign drove 2,039 total conversions; 1,162 were truly incremental."
            ),
            "true_incremental_cpa_gbp": round(281000 / 1162, 2),
            "vs_reported_cpa_gbp": round(281000 / 2039, 2),
            "recommendation": "Use incremental CPA (£241.82) for true budget efficiency decisions, not blended CPA (£137.81).",
            "measured_at": datetime.now(timezone.utc).isoformat(),
        }
