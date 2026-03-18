"""
Azure AI Search tools — semantic search over assets, campaigns, and compliance records.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


class AzureSearchSimulator:
    """Simulates Azure AI Search with vector + keyword search."""

    def __init__(self):
        self._indices: dict[str, list[dict]] = {}

    def index_document(self, index_name: str, document: dict) -> dict:
        if index_name not in self._indices:
            self._indices[index_name] = []
        if "id" not in document:
            document["id"] = str(uuid.uuid4())
        # Remove existing if re-indexing
        self._indices[index_name] = [
            d for d in self._indices[index_name] if d.get("id") != document["id"]
        ]
        document["indexed_at"] = datetime.now(timezone.utc).isoformat()
        self._indices[index_name].append(document)
        return document

    def search(
        self,
        index_name: str,
        query: str,
        filters: Optional[dict] = None,
        top: int = 10,
    ) -> list[dict]:
        docs = self._indices.get(index_name, [])
        results = []
        query_lower = query.lower()
        for doc in docs:
            # Simple keyword match across all string fields
            searchable = " ".join(str(v) for v in doc.values() if isinstance(v, str)).lower()
            score = sum(1 for word in query_lower.split() if word in searchable)
            if score > 0:
                # Apply filters
                if filters:
                    match = all(doc.get(k) == v for k, v in filters.items())
                    if not match:
                        continue
                results.append({**doc, "_score": score})
        results.sort(key=lambda x: x["_score"], reverse=True)
        return results[:top]

    def delete_document(self, index_name: str, doc_id: str) -> bool:
        if index_name not in self._indices:
            return False
        before = len(self._indices[index_name])
        self._indices[index_name] = [
            d for d in self._indices[index_name] if d.get("id") != doc_id
        ]
        return len(self._indices[index_name]) < before


_search_client = AzureSearchSimulator()


# ─── Compliance Knowledge Base ───────────────────────────────────────────────

FCA_RULES_KB = [
    {
        "id": "fca_001",
        "rule_id": "COBS_4.2.1",
        "category": "financial_promotions",
        "title": "Fair, Clear and Not Misleading",
        "description": "A financial promotion must be fair, clear and not misleading.",
        "examples": ["Comparative claims must be fair and accurate", "Risk warnings must be prominent"],
        "keywords": ["misleading", "fair", "clear", "accurate"],
    },
    {
        "id": "fca_002",
        "rule_id": "COBS_4.5.2",
        "category": "representative_apr",
        "title": "Representative APR in Credit Promotions",
        "description": "If a credit promotion includes a rate or amount, it must include a representative APR. The rep APR must be given at least equal prominence.",
        "examples": ["Representative 24.9% APR", "Based on assumed credit limit of £1,200"],
        "keywords": ["APR", "representative", "credit", "interest rate", "borrowing"],
    },
    {
        "id": "fca_003",
        "rule_id": "COBS_4.7",
        "category": "risk_warnings",
        "title": "Risk Warnings for Investments",
        "description": "Investment promotions must include prescribed risk warnings. For mortgages: 'Your home may be repossessed if you do not keep up repayments.'",
        "examples": ["Your home may be repossessed", "Capital at risk"],
        "keywords": ["risk", "warning", "investment", "mortgage", "loss"],
    },
    {
        "id": "fca_004",
        "rule_id": "CONSUMER_DUTY_2023",
        "category": "consumer_duty",
        "title": "Consumer Duty — Fair Value",
        "description": "Products and services must deliver fair value. Marketing must not exploit behavioural biases or create false urgency.",
        "examples": ["No artificial scarcity claims", "Clear total cost of credit"],
        "keywords": ["value", "fair", "consumer duty", "vulnerable", "urgency", "scarcity"],
    },
    {
        "id": "fca_005",
        "rule_id": "COBS_4.2.6",
        "category": "past_performance",
        "title": "Past Performance Disclaimers",
        "description": "Past performance must not be used as a reliable indicator of future results without an appropriate disclaimer.",
        "examples": ["Past performance is not a reliable indicator of future results"],
        "keywords": ["past performance", "historical", "returns", "future"],
    },
    {
        "id": "fca_006",
        "rule_id": "GDPR_UK_2018",
        "category": "data_protection",
        "title": "GDPR Consent for Marketing",
        "description": "Marketing emails and SMS require explicit opt-in consent. Legitimate interest can be used for existing customers within certain limits.",
        "examples": ["Explicit opt-in required", "Opt-out mechanism must be clear"],
        "keywords": ["consent", "opt-in", "opt-out", "GDPR", "data protection", "marketing"],
    },
]


def initialise_compliance_knowledge_base():
    """Load FCA rules into the search index."""
    for rule in FCA_RULES_KB:
        _search_client.index_document("compliance-index", rule)
    logger.info("Loaded %d FCA rules into compliance index", len(FCA_RULES_KB))


def search_fca_rules(query: str, category: Optional[str] = None) -> list[dict]:
    """Search the FCA rules knowledge base."""
    filters = {"category": category} if category else None
    return _search_client.search("compliance-index", query, filters=filters, top=5)


def index_campaign_content(campaign_id: str, content_type: str, content: str, metadata: dict) -> dict:
    """Index campaign content for semantic search."""
    doc = {
        "id": f"{campaign_id}_{content_type}_{uuid.uuid4().hex[:8]}",
        "campaign_id": campaign_id,
        "content_type": content_type,
        "content": content,
        **metadata,
    }
    return _search_client.index_document("campaigns-index", doc)


def search_similar_campaigns(query: str, product_type: Optional[str] = None) -> list[dict]:
    """Find similar past campaigns for reference."""
    filters = {"product_type": product_type} if product_type else None
    return _search_client.search("campaigns-index", query, filters=filters, top=5)


def index_asset(asset_id: str, asset_data: dict) -> dict:
    """Index asset metadata for search."""
    doc = {"id": asset_id, **asset_data}
    return _search_client.index_document("assets-index", doc)


def search_assets(query: str, channel: Optional[str] = None, campaign_id: Optional[str] = None) -> list[dict]:
    """Search the DAM asset index."""
    filters = {}
    if channel:
        filters["channel"] = channel
    if campaign_id:
        filters["campaign_id"] = campaign_id
    return _search_client.search("assets-index", query, filters=filters or None, top=10)


# Initialise knowledge base on import
initialise_compliance_knowledge_base()
