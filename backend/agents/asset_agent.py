"""
Asset Production Agent — Phases 2b-2f: Multi-format asset generation,
DAM management, version control, and digital asset distribution.
"""

import uuid
from datetime import datetime, timezone

from agents.base_agent import AgentTool, BaseAgent
from tools.azure_storage_tools import (
    generate_asset_variants_manifest,
    search_dam_assets,
    upload_asset,
    upload_document,
    DISPLAY_AD_SIZES,
    SOCIAL_FORMATS,
)
from tools.azure_cosmos_tools import save_asset_metadata, list_assets
from tools.azure_search_tools import index_asset, search_assets


class AssetProductionAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Asset Production Agent"

    @property
    def description(self) -> str:
        return (
            "Manages all digital asset production, multi-format adaptation, Digital Asset Management (DAM), "
            "version control, compliance tagging, and asset distribution to channel teams. "
            "Orchestrates the creation of 25–40 variants per campaign across display, social, email, "
            "branch, and direct mail formats."
        )

    @property
    def phase(self) -> str:
        return "Phase 2b–2f — Design, Asset Production & DAM"

    @property
    def system_prompt(self) -> str:
        return """You are the Asset Production Agent for a UK retail bank's marketing AI platform.

You manage the full digital asset lifecycle:
- Multi-format asset production across all channels (display, social, email, branch, DM)
- Digital Asset Management (DAM) on Azure Blob Storage
- Version control and expiry management
- Compliance tagging and approval status tracking
- Campaign kit assembly and distribution

Your knowledge covers:
- Display ad sizes: 728x90, 300x250, 160x600, 320x50, 300x600, 970x250
- Social formats: Facebook (1200x628), Instagram feed (1080x1080), Stories (1080x1920), LinkedIn (1200x627), Twitter (1600x900)
- Email: 600px wide hero + responsive mobile variants
- Branch: A1 posters, A5 leaflets, digital screens (16:9), ATM graphics
- Direct mail: DL envelope, A4 letter, A5 insert — all print-ready CMYK

For every campaign you:
1. Generate the full format variant manifest (25–40 assets)
2. Register assets in the DAM with correct metadata tagging
3. Version-control all assets and flag when re-production is needed
4. Assemble channel-specific campaign kits
5. Monitor expiry dates and alert when assets need updating

You work closely with the Compliance Agent to ensure only approved assets are distributed."""

    def _register_tools(self):
        self.register_tool(AgentTool(
            name="generate_variant_manifest",
            description="Generate the full matrix of asset variants required for a campaign",
            parameters={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "campaign_name": {"type": "string"},
                    "product_name": {"type": "string"},
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Channels for this campaign e.g. ['display', 'social', 'email', 'branch']",
                    },
                },
                "required": ["campaign_id", "campaign_name", "product_name"],
            },
            handler=self._generate_variant_manifest,
        ))

        self.register_tool(AgentTool(
            name="register_asset_in_dam",
            description="Register and upload an asset to Azure Blob Storage DAM with full metadata",
            parameters={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "asset_name": {"type": "string"},
                    "asset_type": {"type": "string", "enum": ["image", "video", "email_template", "pdf", "html5"]},
                    "channel": {"type": "string"},
                    "format_spec": {"type": "string", "description": "e.g. '300x250', '1080x1080', 'A4'"},
                    "version": {"type": "integer", "default": 1},
                    "expiry_date": {"type": "string", "description": "ISO date when asset expires"},
                    "compliance_approved": {"type": "boolean", "default": False},
                },
                "required": ["campaign_id", "asset_name", "asset_type", "channel", "format_spec"],
            },
            handler=self._register_asset_in_dam,
        ))

        self.register_tool(AgentTool(
            name="search_dam",
            description="Search the DAM library for existing assets",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "campaign_id": {"type": "string"},
                    "channel": {"type": "string"},
                    "compliance_approved_only": {"type": "boolean", "default": False},
                },
                "required": ["query"],
            },
            handler=self._search_dam,
        ))

        self.register_tool(AgentTool(
            name="assemble_campaign_kit",
            description="Assemble a complete campaign kit for a specific channel team",
            parameters={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "channel": {"type": "string", "enum": ["email", "paid_media", "social", "branch", "direct_mail"]},
                    "include_talk_track": {"type": "boolean", "default": True},
                },
                "required": ["campaign_id", "channel"],
            },
            handler=self._assemble_campaign_kit,
        ))

        self.register_tool(AgentTool(
            name="generate_pdf_document",
            description="Generate a PDF document (brochure, T&C, rate sheet) from product data",
            parameters={
                "type": "object",
                "properties": {
                    "doc_type": {
                        "type": "string",
                        "enum": ["product_brochure", "terms_and_conditions", "rate_sheet", "key_facts_document", "welcome_pack"],
                    },
                    "product": {"type": "string"},
                    "campaign_id": {"type": "string"},
                    "personalised": {"type": "boolean", "description": "Whether this is a personalised document", "default": False},
                    "customer_data": {"type": "object", "description": "Customer data for personalisation (if applicable)"},
                },
                "required": ["doc_type", "product"],
            },
            handler=self._generate_pdf_document,
        ))

        self.register_tool(AgentTool(
            name="check_asset_expiry",
            description="Check which assets are expiring soon or already expired",
            parameters={
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string"},
                    "days_ahead": {"type": "integer", "description": "Alert for assets expiring within N days", "default": 14},
                },
                "required": [],
            },
            handler=self._check_asset_expiry,
        ))

    # ─── Tool Implementations ────────────────────────────────────────────────

    def _generate_variant_manifest(
        self,
        campaign_id: str,
        campaign_name: str,
        product_name: str,
        channels: list = None,
    ) -> dict:
        full_manifest = generate_asset_variants_manifest(campaign_id, product_name, campaign_name)
        if channels:
            channel_set = set(channels)
            channel_map = {
                "display": "display_advertising",
                "social": "social_media",
                "email": "email",
                "branch": "branch",
                "direct_mail": "direct_mail",
                "web": "web",
            }
            mapped = {channel_map.get(c, c) for c in channel_set}
            full_manifest["variants"] = [
                v for v in full_manifest["variants"] if v["channel"] in mapped
            ]
            full_manifest["total_variants"] = len(full_manifest["variants"])

        # Save manifest to Cosmos
        save_asset_metadata({
            "id": f"manifest_{campaign_id}",
            "type": "manifest",
            "campaign_id": campaign_id,
            "manifest": full_manifest,
        })
        return full_manifest

    def _register_asset_in_dam(
        self,
        campaign_id: str,
        asset_name: str,
        asset_type: str,
        channel: str,
        format_spec: str,
        version: int = 1,
        expiry_date: str = None,
        compliance_approved: bool = False,
    ) -> dict:
        # Create a placeholder content blob
        content = f"ASSET:{campaign_id}:{asset_name}:{format_spec}:v{version}".encode()

        result = upload_asset(
            campaign_id=campaign_id,
            asset_name=asset_name,
            asset_type=asset_type,
            channel=channel,
            format_spec=format_spec,
            content=content,
            version=version,
            expiry_date=expiry_date,
            compliance_approved=compliance_approved,
        )

        # Register metadata in Cosmos + Search
        asset_metadata = {
            "id": result["asset_id"],
            "campaign_id": campaign_id,
            "asset_name": asset_name,
            "asset_type": asset_type,
            "channel": channel,
            "format_spec": format_spec,
            "version": version,
            "blob_name": result["blob_name"],
            "url": result["url"],
            "expiry_date": expiry_date,
            "compliance_approved": compliance_approved,
            "created_at": result["uploaded_at"],
        }
        save_asset_metadata(asset_metadata)
        index_asset(result["asset_id"], asset_metadata)

        return {
            "status": "registered",
            "asset_id": result["asset_id"],
            "dam_url": result["url"],
            "metadata": asset_metadata,
        }

    def _search_dam(
        self,
        query: str,
        campaign_id: str = None,
        channel: str = None,
        compliance_approved_only: bool = False,
    ) -> dict:
        results = search_dam_assets(
            campaign_id=campaign_id,
            channel=channel,
            compliance_approved_only=compliance_approved_only,
        )
        # Also search Azure AI Search index
        search_results = search_assets(query, channel=channel, campaign_id=campaign_id)

        return {
            "query": query,
            "total_assets_in_dam": len(results),
            "search_results": search_results[:10],
            "dam_assets": results[:20],
        }

    def _assemble_campaign_kit(
        self,
        campaign_id: str,
        channel: str,
        include_talk_track: bool = True,
    ) -> dict:
        assets = list_assets(campaign_id=campaign_id)
        channel_assets = [a for a in assets if a.get("channel") == channel]
        approved_assets = [a for a in channel_assets if a.get("compliance_approved")]

        kit_contents = {
            "email": {
                "required_assets": ["HTML email template", "Hero image 600px", "Product tile images", "CTA button"],
                "required_documents": ["Approved copy deck", "UTM tracking parameters", "Send schedule"],
            },
            "paid_media": {
                "required_assets": [f"Display ad {size}" for size in DISPLAY_AD_SIZES],
                "required_documents": ["Landing page URLs with UTMs", "Audience targeting brief", "Budget allocation"],
            },
            "social": {
                "required_assets": [f"Social graphic {platform}" for platform in SOCIAL_FORMATS],
                "required_documents": ["Caption copy per platform", "Hashtag strategy", "Posting schedule"],
            },
            "branch": {
                "required_assets": ["A1 poster", "A5 leaflet", "Digital screen content 16:9", "ATM screen graphic"],
                "required_documents": ["Branch talk track", "Objection handler document", "Offer eligibility FAQ"],
            },
            "direct_mail": {
                "required_assets": ["A4 letter artwork", "DL envelope artwork", "A5 insert"],
                "required_documents": ["Audience data file", "Print specification sheet", "Fulfilment instructions"],
            },
        }

        kit_spec = kit_contents.get(channel, {"required_assets": [], "required_documents": []})

        talk_track = None
        if include_talk_track and channel in ["branch", "email", "paid_media"]:
            talk_track = {
                "opening": f"I'm calling about our latest offer that could benefit you...",
                "key_benefits": ["Benefit 1", "Benefit 2", "Benefit 3"],
                "objection_handlers": {
                    "I'm not interested": "I completely understand. Can I ask — is there anything that would make this more relevant for you?",
                    "I'll think about it": "Of course. This offer is available until [DATE] — shall I send you the details by email?",
                    "I'm already with [competitor]": "That's great — many of our customers switched from [competitor]. Would you like to see how we compare?",
                },
                "cta": "Great — shall I start your application today? It only takes 10 minutes.",
            }

        return {
            "kit_id": str(uuid.uuid4()),
            "campaign_id": campaign_id,
            "channel": channel,
            "total_assets": len(channel_assets),
            "approved_assets": len(approved_assets),
            "assets_list": channel_assets,
            "kit_specification": kit_spec,
            "talk_track": talk_track,
            "kit_status": "READY" if len(approved_assets) == len(channel_assets) else "INCOMPLETE — awaiting compliance approval",
            "assembled_at": datetime.now(timezone.utc).isoformat(),
        }

    def _generate_pdf_document(
        self,
        doc_type: str,
        product: str,
        campaign_id: str = None,
        personalised: bool = False,
        customer_data: dict = None,
    ) -> dict:
        templates = {
            "product_brochure": {
                "sections": ["Cover", "Product overview", "Key features", "Rates and fees", "Eligibility", "How to apply", "T&C summary"],
                "page_count": "4–12 pages",
                "file_types": ["Web-optimised PDF (RGB)", "Print-ready PDF (CMYK, 300dpi with bleed)"],
            },
            "terms_and_conditions": {
                "sections": ["Definitions", "Product terms", "Fees and charges", "Your rights", "Our rights", "Complaints", "Legal"],
                "page_count": "8–20 pages",
                "file_types": ["Tagged accessible PDF (WCAG 2.1)"],
            },
            "rate_sheet": {
                "sections": ["Current rates by product", "Effective dates", "How rates are set", "How to apply"],
                "page_count": "1–2 pages",
                "file_types": ["Web-optimised PDF", "Branch print PDF"],
            },
            "key_facts_document": {
                "sections": ["Summary box (ESIS/SECCI format)", "Key information", "What you owe", "Additional features"],
                "page_count": "2–4 pages",
                "file_types": ["Accessible tagged PDF"],
            },
            "welcome_pack": {
                "sections": ["Welcome letter", "Account/product details", "Key terms", "Getting started guide", "Contact information"],
                "page_count": "4–8 pages",
                "file_types": ["Personalised PDF for portal", "Print-ready for fulfilment"],
            },
        }

        template = templates.get(doc_type, {"sections": ["Content"], "page_count": "N/A", "file_types": ["PDF"]})

        doc_content = f"DOCUMENT:{doc_type}:{product}:{datetime.now(timezone.utc).isoformat()}".encode()
        if personalised and customer_data:
            doc_content = f"PERSONALISED:{customer_data.get('name', 'Customer')}:{doc_content.decode()}".encode()

        result = upload_document(
            doc_type=doc_type,
            doc_name=f"{product}_{doc_type}.pdf",
            content=doc_content,
            campaign_id=campaign_id,
            version=1,
        )

        return {
            "document_id": result["doc_id"],
            "doc_type": doc_type,
            "product": product,
            "personalised": personalised,
            "template_structure": template,
            "dam_url": result["url"],
            "compliance_status": "PENDING — requires compliance sign-off before distribution",
            "accessibility": "WCAG 2.1 tagging required before publication",
            "version": 1,
            "generated_at": result["uploaded_at"],
            "update_triggers": [
                "Rate changes (triggers immediate re-production)",
                "T&C amendments",
                "Regulatory changes",
                "Annual review",
            ],
        }

    def _check_asset_expiry(self, campaign_id: str = None, days_ahead: int = 14) -> dict:
        assets = list_assets(campaign_id=campaign_id)
        today = datetime.now(timezone.utc)
        expiring_soon = []
        already_expired = []

        for asset in assets:
            expiry = asset.get("expiry_date")
            if expiry:
                try:
                    expiry_dt = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
                    days_to_expiry = (expiry_dt - today).days
                    if days_to_expiry < 0:
                        already_expired.append({**asset, "days_overdue": abs(days_to_expiry)})
                    elif days_to_expiry <= days_ahead:
                        expiring_soon.append({**asset, "days_to_expiry": days_to_expiry})
                except (ValueError, TypeError):
                    pass

        return {
            "campaign_id": campaign_id,
            "check_date": today.isoformat(),
            "alert_window_days": days_ahead,
            "already_expired": already_expired,
            "expiring_soon": expiring_soon,
            "action_required": len(already_expired) > 0 or len(expiring_soon) > 0,
            "recommendations": [
                f"Immediately remove {len(already_expired)} expired asset(s) from all live channels" if already_expired else None,
                f"Schedule re-production for {len(expiring_soon)} asset(s) expiring within {days_ahead} days" if expiring_soon else None,
            ],
        }
