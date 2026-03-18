"""
Azure Cosmos DB tools for persisting campaigns, leads, and agent state.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CosmosDBClient:
    """Simulated Cosmos DB client — replace with azure-cosmos SDK in production."""

    def __init__(self):
        self._store: dict[str, dict] = {}

    def upsert_item(self, container: str, item: dict) -> dict:
        if "id" not in item:
            item["id"] = str(uuid.uuid4())
        item["_ts"] = datetime.now(timezone.utc).isoformat()
        key = f"{container}:{item['id']}"
        self._store[key] = item
        logger.info("Upserted item %s in %s", item["id"], container)
        return item

    def get_item(self, container: str, item_id: str) -> Optional[dict]:
        return self._store.get(f"{container}:{item_id}")

    def query_items(self, container: str, query: str, parameters: Optional[list] = None) -> list[dict]:
        # Simplified: return all items in the container
        prefix = f"{container}:"
        return [v for k, v in self._store.items() if k.startswith(prefix)]

    def delete_item(self, container: str, item_id: str) -> bool:
        key = f"{container}:{item_id}"
        if key in self._store:
            del self._store[key]
            return True
        return False


# Singleton client
_cosmos_client = CosmosDBClient()


# ─── Campaign Store ─────────────────────────────────────────────────────────

def save_campaign(campaign_data: dict) -> dict:
    """Persist a campaign record to Cosmos DB."""
    if "id" not in campaign_data:
        campaign_data["id"] = str(uuid.uuid4())
    campaign_data["created_at"] = datetime.now(timezone.utc).isoformat()
    campaign_data["status"] = campaign_data.get("status", "draft")
    return _cosmos_client.upsert_item("campaigns", campaign_data)


def get_campaign(campaign_id: str) -> Optional[dict]:
    return _cosmos_client.get_item("campaigns", campaign_id)


def list_campaigns(status_filter: Optional[str] = None) -> list[dict]:
    items = _cosmos_client.query_items("campaigns", "SELECT * FROM c")
    if status_filter:
        items = [i for i in items if i.get("status") == status_filter]
    return items


def update_campaign_status(campaign_id: str, status: str, metadata: Optional[dict] = None) -> dict:
    campaign = get_campaign(campaign_id) or {"id": campaign_id}
    campaign["status"] = status
    campaign["updated_at"] = datetime.now(timezone.utc).isoformat()
    if metadata:
        campaign.update(metadata)
    return _cosmos_client.upsert_item("campaigns", campaign)


# ─── Lead Store ─────────────────────────────────────────────────────────────

def save_lead(lead_data: dict) -> dict:
    if "id" not in lead_data:
        lead_data["id"] = str(uuid.uuid4())
    lead_data["created_at"] = datetime.now(timezone.utc).isoformat()
    return _cosmos_client.upsert_item("leads", lead_data)


def get_lead(lead_id: str) -> Optional[dict]:
    return _cosmos_client.get_item("leads", lead_id)


def list_leads(status_filter: Optional[str] = None) -> list[dict]:
    items = _cosmos_client.query_items("leads", "SELECT * FROM c")
    if status_filter:
        items = [i for i in items if i.get("status") == status_filter]
    return items


def update_lead(lead_id: str, updates: dict) -> dict:
    lead = get_lead(lead_id) or {"id": lead_id}
    lead.update(updates)
    lead["updated_at"] = datetime.now(timezone.utc).isoformat()
    return _cosmos_client.upsert_item("leads", lead)


# ─── Asset Registry ─────────────────────────────────────────────────────────

def save_asset_metadata(asset_data: dict) -> dict:
    if "id" not in asset_data:
        asset_data["id"] = str(uuid.uuid4())
    asset_data["created_at"] = datetime.now(timezone.utc).isoformat()
    return _cosmos_client.upsert_item("assets", asset_data)


def get_asset(asset_id: str) -> Optional[dict]:
    return _cosmos_client.get_item("assets", asset_id)


def list_assets(campaign_id: Optional[str] = None, asset_type: Optional[str] = None) -> list[dict]:
    items = _cosmos_client.query_items("assets", "SELECT * FROM c")
    if campaign_id:
        items = [i for i in items if i.get("campaign_id") == campaign_id]
    if asset_type:
        items = [i for i in items if i.get("asset_type") == asset_type]
    return items


# ─── Compliance Records ──────────────────────────────────────────────────────

def save_compliance_record(record: dict) -> dict:
    if "id" not in record:
        record["id"] = str(uuid.uuid4())
    record["submitted_at"] = datetime.now(timezone.utc).isoformat()
    return _cosmos_client.upsert_item("compliance", record)


def list_compliance_records(campaign_id: Optional[str] = None) -> list[dict]:
    items = _cosmos_client.query_items("compliance", "SELECT * FROM c")
    if campaign_id:
        items = [i for i in items if i.get("campaign_id") == campaign_id]
    return items


# ─── Agent Conversation History ──────────────────────────────────────────────

def save_agent_message(session_id: str, agent_name: str, role: str, content: str) -> dict:
    record = {
        "id": str(uuid.uuid4()),
        "session_id": session_id,
        "agent_name": agent_name,
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return _cosmos_client.upsert_item("messages", record)


def get_session_history(session_id: str) -> list[dict]:
    items = _cosmos_client.query_items("messages", "SELECT * FROM c")
    msgs = [i for i in items if i.get("session_id") == session_id]
    return sorted(msgs, key=lambda x: x.get("timestamp", ""))
