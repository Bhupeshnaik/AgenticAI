"""
Azure Blob Storage tools — Digital Asset Management (DAM) layer.
Stores, versions, and retrieves all campaign assets.
"""

import base64
import json
import logging
import mimetypes
import uuid
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


# ─── In-memory DAM for local dev (swap for azure-storage-blob in prod) ──────

class BlobStorageSimulator:
    def __init__(self):
        self._blobs: dict[str, dict] = {}  # path -> {data, metadata}

    def upload_blob(self, container: str, blob_name: str, data: bytes, metadata: Optional[dict] = None) -> str:
        path = f"{container}/{blob_name}"
        self._blobs[path] = {
            "data": base64.b64encode(data).decode(),
            "metadata": metadata or {},
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "size_bytes": len(data),
            "content_type": mimetypes.guess_type(blob_name)[0] or "application/octet-stream",
        }
        url = f"https://bankmarketingai.blob.core.windows.net/{path}"
        logger.info("Uploaded blob: %s (%d bytes)", path, len(data))
        return url

    def download_blob(self, container: str, blob_name: str) -> Optional[bytes]:
        path = f"{container}/{blob_name}"
        blob = self._blobs.get(path)
        if blob:
            return base64.b64decode(blob["data"])
        return None

    def list_blobs(self, container: str, prefix: Optional[str] = None) -> list[dict]:
        results = []
        for path, blob in self._blobs.items():
            if path.startswith(container):
                if prefix is None or path.startswith(f"{container}/{prefix}"):
                    results.append({
                        "name": path[len(container) + 1:],
                        "url": f"https://bankmarketingai.blob.core.windows.net/{path}",
                        "size_bytes": blob["size_bytes"],
                        "content_type": blob["content_type"],
                        "metadata": blob["metadata"],
                        "uploaded_at": blob["uploaded_at"],
                    })
        return results

    def delete_blob(self, container: str, blob_name: str) -> bool:
        path = f"{container}/{blob_name}"
        if path in self._blobs:
            del self._blobs[path]
            return True
        return False

    def blob_exists(self, container: str, blob_name: str) -> bool:
        return f"{container}/{blob_name}" in self._blobs


_storage = BlobStorageSimulator()


# ─── DAM Functions ───────────────────────────────────────────────────────────

DISPLAY_AD_SIZES = [
    "728x90", "300x250", "160x600", "320x50", "300x600", "970x250"
]

SOCIAL_FORMATS = {
    "facebook": "1200x628",
    "instagram_feed": "1080x1080",
    "instagram_stories": "1080x1920",
    "linkedin": "1200x627",
    "twitter": "1600x900",
    "reels": "1080x1920",
}

EMAIL_FORMATS = ["hero_600px", "product_tile", "cta_button", "mobile_optimised"]

BRANCH_FORMATS = ["A1_poster", "A5_leaflet", "digital_screen_16x9", "window_vinyl", "ATM_screen"]

DIRECT_MAIL_FORMATS = ["DL_envelope", "A4_letter", "A5_insert", "self_mailer"]


def upload_asset(
    campaign_id: str,
    asset_name: str,
    asset_type: str,
    channel: str,
    format_spec: str,
    content: bytes,
    version: int = 1,
    expiry_date: Optional[str] = None,
    compliance_approved: bool = False,
) -> dict:
    """Upload a single asset to Azure Blob Storage DAM."""
    asset_id = str(uuid.uuid4())
    blob_name = f"{campaign_id}/{asset_type}/{channel}/{format_spec}/{asset_id}_v{version}_{asset_name}"
    metadata = {
        "campaign_id": campaign_id,
        "asset_id": asset_id,
        "asset_type": asset_type,
        "channel": channel,
        "format_spec": format_spec,
        "version": str(version),
        "expiry_date": expiry_date or "",
        "compliance_approved": str(compliance_approved),
    }
    url = _storage.upload_blob("digital-assets", blob_name, content, metadata)
    return {
        "asset_id": asset_id,
        "blob_name": blob_name,
        "url": url,
        "metadata": metadata,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }


def generate_asset_variants_manifest(campaign_id: str, product_name: str, campaign_name: str) -> dict:
    """
    Generate a manifest of all required asset variants for a campaign.
    Returns the full format matrix that needs to be produced.
    """
    variants = []

    for size in DISPLAY_AD_SIZES:
        variants.append({
            "channel": "display_advertising",
            "format": size,
            "file_type": "HTML5/JPG/PNG",
            "dimensions": size,
            "notes": "Static + animated variants required",
        })

    for platform, dimensions in SOCIAL_FORMATS.items():
        variants.append({
            "channel": "social_media",
            "format": platform,
            "file_type": "JPG/PNG/MP4",
            "dimensions": dimensions,
            "notes": f"Platform: {platform}",
        })

    for fmt in EMAIL_FORMATS:
        variants.append({
            "channel": "email",
            "format": fmt,
            "file_type": "JPG/PNG",
            "dimensions": "600px wide",
            "notes": "Mobile-optimised required",
        })

    for fmt in BRANCH_FORMATS:
        variants.append({
            "channel": "branch",
            "format": fmt,
            "file_type": "PDF/PNG",
            "dimensions": "Print-ready CMYK",
            "notes": "High-res 300dpi",
        })

    for fmt in DIRECT_MAIL_FORMATS:
        variants.append({
            "channel": "direct_mail",
            "format": fmt,
            "file_type": "PDF",
            "dimensions": "Print-ready CMYK with bleed",
            "notes": "Personalisation fields required",
        })

    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign_name,
        "product_name": product_name,
        "total_variants": len(variants),
        "variants": variants,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def search_dam_assets(
    campaign_id: Optional[str] = None,
    channel: Optional[str] = None,
    asset_type: Optional[str] = None,
    compliance_approved_only: bool = False,
) -> list[dict]:
    """Search the DAM library with optional filters."""
    blobs = _storage.list_blobs("digital-assets")
    results = []
    for blob in blobs:
        meta = blob.get("metadata", {})
        if campaign_id and meta.get("campaign_id") != campaign_id:
            continue
        if channel and meta.get("channel") != channel:
            continue
        if asset_type and meta.get("asset_type") != asset_type:
            continue
        if compliance_approved_only and meta.get("compliance_approved") != "True":
            continue
        results.append(blob)
    return results


def get_asset_version_history(campaign_id: str, asset_type: str, channel: str) -> list[dict]:
    """Return all versions of an asset type for version control audit."""
    blobs = _storage.list_blobs("digital-assets", prefix=f"{campaign_id}/{asset_type}/{channel}")
    return sorted(blobs, key=lambda x: x.get("uploaded_at", ""))


def mark_asset_as_expired(blob_name: str) -> bool:
    """Mark an asset as expired (for regulatory compliance)."""
    # In production, update blob metadata via SDK
    logger.info("Marking asset as expired: %s", blob_name)
    return True


def upload_document(
    doc_type: str,
    doc_name: str,
    content: bytes,
    campaign_id: Optional[str] = None,
    version: int = 1,
) -> dict:
    """Upload a document (PDF, brochure, T&C) to the documents container."""
    doc_id = str(uuid.uuid4())
    blob_name = f"{doc_type}/{doc_id}_v{version}_{doc_name}"
    metadata = {
        "doc_id": doc_id,
        "doc_type": doc_type,
        "campaign_id": campaign_id or "",
        "version": str(version),
    }
    url = _storage.upload_blob("documents", blob_name, content, metadata)
    return {
        "doc_id": doc_id,
        "blob_name": blob_name,
        "url": url,
        "doc_type": doc_type,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
