"""
Multi-Agent Orchestrator — routes user requests to the appropriate agent(s),
supports sequential and parallel agent execution, and manages session state.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from agents import (
    StrategyAgent,
    CopywritingAgent,
    ComplianceAgent,
    AssetProductionAgent,
    SegmentationAgent,
    CampaignOrchestrationAgent,
    LeadManagementAgent,
    NurtureAgent,
    AnalyticsAgent,
)
from tools.azure_cosmos_tools import save_agent_message, get_session_history

logger = logging.getLogger(__name__)


# ─── Agent Registry ──────────────────────────────────────────────────────────

AGENT_REGISTRY = {
    "strategy": StrategyAgent,
    "copywriting": CopywritingAgent,
    "compliance": ComplianceAgent,
    "asset": AssetProductionAgent,
    "segmentation": SegmentationAgent,
    "campaign": CampaignOrchestrationAgent,
    "lead": LeadManagementAgent,
    "nurture": NurtureAgent,
    "analytics": AnalyticsAgent,
}

# Phase to agent mapping
PHASE_AGENT_MAP = {
    "phase_1": ["strategy"],
    "phase_2": ["copywriting", "asset"],
    "phase_3": ["segmentation"],
    "phase_4": ["compliance"],
    "phase_5": ["campaign"],
    "phase_6": ["lead"],
    "phase_7": ["nurture"],
    "phase_8": ["analytics"],
}

# Routing keywords to agent
ROUTING_KEYWORDS = {
    "strategy": ["strategy", "annual plan", "budget", "kpi", "planning", "campaign brief", "quarterly", "market analysis"],
    "copywriting": ["copy", "headline", "subject line", "email body", "cta", "social post", "sms text", "write", "content", "messaging"],
    "compliance": ["compliance", "fca", "approve", "review", "risk warning", "apr", "cobs", "consumer duty", "certificate", "sign-off"],
    "asset": ["asset", "image", "design", "format", "dam", "variant", "pdf", "brochure", "visual", "banner", "poster"],
    "segmentation": ["audience", "segment", "targeting", "suppression", "gdpr", "list", "propensity", "data file"],
    "campaign": ["launch", "deploy", "campaign live", "frequency cap", "orchestrate", "channel plan", "paid media", "email send"],
    "lead": ["lead", "scoring", "routing", "crm", "sla", "enquiry", "prospect", "hot lead"],
    "nurture": ["nurture", "journey", "drip", "follow-up", "abandoned", "retargeting", "next best action", "personalise"],
    "analytics": ["analytics", "report", "performance", "roi", "attribution", "roas", "cpa", "metrics", "dashboard"],
}


class MultiAgentOrchestrator:
    """
    Routes user requests to the appropriate specialist agent(s).
    Maintains separate agent instances per session for conversation continuity.
    """

    def __init__(self):
        self._sessions: dict[str, dict] = {}  # session_id -> {agent_name: agent_instance}

    def _get_or_create_agent(self, session_id: str, agent_name: str):
        if session_id not in self._sessions:
            self._sessions[session_id] = {}
        if agent_name not in self._sessions[session_id]:
            agent_class = AGENT_REGISTRY.get(agent_name)
            if agent_class:
                self._sessions[session_id][agent_name] = agent_class()
        return self._sessions[session_id].get(agent_name)

    def _route_to_agent(self, message: str, preferred_agent: Optional[str] = None) -> str:
        """Determine which agent should handle this message."""
        if preferred_agent and preferred_agent in AGENT_REGISTRY:
            return preferred_agent

        message_lower = message.lower()
        scores = {agent: 0 for agent in AGENT_REGISTRY}

        for agent_name, keywords in ROUTING_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    scores[agent_name] += 1

        # Default to strategy if no strong match
        best_agent = max(scores, key=scores.get)
        if scores[best_agent] == 0:
            best_agent = "strategy"

        return best_agent

    def run(
        self,
        message: str,
        session_id: str,
        agent_name: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> dict:
        """
        Route a message to the appropriate agent and return the response.
        """
        selected_agent_name = self._route_to_agent(message, agent_name)
        agent = self._get_or_create_agent(session_id, selected_agent_name)

        if not agent:
            return {
                "error": f"Agent '{selected_agent_name}' not found",
                "available_agents": list(AGENT_REGISTRY.keys()),
            }

        # Log user message
        save_agent_message(session_id, selected_agent_name, "user", message)

        # Execute agent
        result = agent.run(message, context=context)
        result["routed_to"] = selected_agent_name
        result["session_id"] = session_id

        # Log agent response
        save_agent_message(session_id, selected_agent_name, "assistant", result.get("response", ""))

        return result

    def run_workflow(
        self,
        workflow_name: str,
        initial_data: dict,
        session_id: Optional[str] = None,
    ) -> dict:
        """
        Run a multi-agent workflow — a predefined sequence of agent calls.
        Returns aggregated results from all agents.
        """
        session_id = session_id or str(uuid.uuid4())
        workflows = {
            "campaign_launch": self._workflow_campaign_launch,
            "compliance_review": self._workflow_compliance_review,
            "audience_build": self._workflow_audience_build,
            "full_campaign": self._workflow_full_campaign,
            "performance_review": self._workflow_performance_review,
        }

        workflow_fn = workflows.get(workflow_name)
        if not workflow_fn:
            return {"error": f"Unknown workflow: {workflow_name}. Available: {list(workflows.keys())}"}

        return workflow_fn(initial_data, session_id)

    def _workflow_campaign_launch(self, data: dict, session_id: str) -> dict:
        """Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 workflow."""
        results = {"workflow": "campaign_launch", "session_id": session_id, "steps": []}

        # Step 1: Strategy
        strategy_agent = self._get_or_create_agent(session_id, "strategy")
        step1 = strategy_agent.run(
            f"Create a campaign brief for: {data.get('campaign_description', 'new product campaign')}",
            context=data,
        )
        results["steps"].append({"step": 1, "agent": "strategy", "result": step1})

        # Step 2: Copywriting
        copy_agent = self._get_or_create_agent(session_id, "copywriting")
        step2 = copy_agent.run(
            f"Generate copy for {data.get('product', 'the product')} campaign targeting {data.get('target_segment', 'target segment')}",
            context={"campaign_brief": step1.get("response", "")},
        )
        results["steps"].append({"step": 2, "agent": "copywriting", "result": step2})

        # Step 3: Compliance pre-screen
        compliance_agent = self._get_or_create_agent(session_id, "compliance")
        step3 = compliance_agent.run(
            f"Pre-screen the following copy for FCA compliance: {step2.get('response', '')[:500]}",
            context={"product_type": data.get("product_type", "personal_loan")},
        )
        results["steps"].append({"step": 3, "agent": "compliance", "result": step3})

        # Step 4: Segmentation
        seg_agent = self._get_or_create_agent(session_id, "segmentation")
        step4 = seg_agent.run(
            f"Build audience segment for {data.get('target_segment', 'target segment')} campaign",
            context=data,
        )
        results["steps"].append({"step": 4, "agent": "segmentation", "result": step4})

        results["status"] = "COMPLETED"
        results["completed_at"] = datetime.now(timezone.utc).isoformat()
        return results

    def _workflow_compliance_review(self, data: dict, session_id: str) -> dict:
        """Full compliance review workflow."""
        compliance_agent = self._get_or_create_agent(session_id, "compliance")
        result = compliance_agent.run(
            f"Full compliance review of: {data.get('content', '')}",
            context=data,
        )
        return {"workflow": "compliance_review", "session_id": session_id, "result": result}

    def _workflow_audience_build(self, data: dict, session_id: str) -> dict:
        """Full audience build: segmentation → GDPR → suppression."""
        seg_agent = self._get_or_create_agent(session_id, "segmentation")
        result = seg_agent.run(
            f"Build complete audience with suppressions for {data.get('campaign_id', 'campaign')}",
            context=data,
        )
        return {"workflow": "audience_build", "session_id": session_id, "result": result}

    def _workflow_full_campaign(self, data: dict, session_id: str) -> dict:
        """End-to-end campaign workflow — all 8 phases."""
        results = {"workflow": "full_campaign", "session_id": session_id, "phases": {}}

        phase_prompts = {
            "strategy": f"Create annual/quarterly campaign plan for {data.get('product', 'product')}",
            "copywriting": f"Generate all campaign copy for {data.get('product', 'product')} targeting {data.get('segment', 'customers')}",
            "asset": f"Generate asset variant manifest for {data.get('product', 'product')} campaign",
            "segmentation": f"Build target audience for {data.get('product', 'product')} campaign",
            "compliance": f"Review all content for FCA compliance",
            "campaign": f"Create multi-channel launch plan for {data.get('product', 'product')} campaign",
            "lead": f"Set up lead scoring and routing for {data.get('product', 'product')} campaign",
            "nurture": f"Design nurture journey for non-converting leads",
            "analytics": f"Set up performance tracking and attribution for {data.get('product', 'product')} campaign",
        }

        for agent_name, prompt in phase_prompts.items():
            agent = self._get_or_create_agent(session_id, agent_name)
            result = agent.run(prompt, context=data)
            results["phases"][agent_name] = result

        results["status"] = "COMPLETED"
        results["completed_at"] = datetime.now(timezone.utc).isoformat()
        return results

    def _workflow_performance_review(self, data: dict, session_id: str) -> dict:
        """Performance review + optimisation recommendations."""
        analytics_agent = self._get_or_create_agent(session_id, "analytics")
        result = analytics_agent.run(
            f"Generate full performance report and budget recommendations for campaign {data.get('campaign_id', '')}",
            context=data,
        )
        return {"workflow": "performance_review", "session_id": session_id, "result": result}

    def get_all_agent_capabilities(self) -> list[dict]:
        """Return capabilities of all registered agents."""
        capabilities = []
        for name, agent_class in AGENT_REGISTRY.items():
            agent = agent_class()
            cap = agent.get_capabilities()
            cap["agent_key"] = name
            capabilities.append(cap)
        return capabilities

    def get_session_history(self, session_id: str) -> list[dict]:
        return get_session_history(session_id)

    def new_session(self) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {}
        return session_id

    def reset_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]


# Singleton orchestrator
orchestrator = MultiAgentOrchestrator()
