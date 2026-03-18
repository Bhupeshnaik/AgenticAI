# Bank Marketing Operations — As-Is Process Map

## Complete End-to-End Marketing Operations for a UK Bank

**Document Purpose:** This document provides a detailed as-is mapping of the full marketing operations lifecycle within a UK retail and commercial bank. It covers all 8 phases from strategy through measurement, with detailed sub-processes for media and asset production. Each stage identifies the user personas involved, their specific activities, data requirements, deliverables produced, pain points, and typical durations.

**Total personas involved:** 28+ distinct roles across the end-to-end process
**Typical elapsed time (major campaign):** 8–16 weeks from strategy to campaign-live, plus 2–4 weeks for post-campaign analysis
**Total assets per campaign:** 40–55 individual assets (images, PDFs, videos, emails, landing pages)

---

## Phase 1: Strategy & Annual Planning

### 1a. Annual Marketing Strategy

**Objective:** Define targets, budgets, and product marketing priorities for the year.

#### Personas Involved

| Persona | Role in This Phase |
|---|---|
| CMO / Head of Marketing | Sets overall marketing vision, owns budget, presents to board |
| Product Heads (Retail, Commercial, Cards) | Define product launch calendar, revenue targets by product line |
| CFO / Finance Business Partner | Approves marketing investment, sets ROI expectations |
| Head of Digital | Advises on digital channel capacity, technology constraints |

#### Activities

- Review prior year campaign performance vs. origination targets
- Align marketing calendar to product launches (new mortgage rates, SME lending push, card promotions)
- Set channel budget split across paid, owned, and earned media
- Define KPIs: cost per lead (CPL), cost per acquisition (CPA), marketing-attributed revenue
- Benchmark against competitor marketing activity and market share data
- Prepare board-level marketing investment paper

#### Data Needs

- Prior year campaign ROI data (by product, by channel)
- Product P&L by segment
- Market share benchmarks (e.g., CACI, Mintel, internal MI)
- Competitor pricing intelligence
- Customer base demographics and segmentation
- Channel cost benchmarks (CPM, CPC, CAC by channel)
- Regulatory pipeline (upcoming FCA consultations, Consumer Duty requirements)

#### Deliverables

- Annual marketing plan (PowerPoint deck, 30–50 slides)
- Channel budget allocation spreadsheet
- Campaign calendar (Gantt chart / Excel, 12-month view)
- KPI dashboard targets (agreed with Finance)
- Board marketing investment paper

#### Pain Points

- 6–8 week planning cycle — too slow to respond to market changes
- Budget allocation based on gut feel and last year's numbers, not predictive models
- Spreadsheet-based planning with no scenario modelling capability
- Product and marketing teams frequently misaligned on priorities
- No automated link between market data and planning tools

#### Duration

- 6–10 weeks annually
- Quarterly refresh: 2–3 weeks

---

### 1b. Quarterly Campaign Planning

**Objective:** Break annual plan into quarterly execution sprints with assigned owners and campaign briefs.

#### Personas Involved

| Persona | Role in This Phase |
|---|---|
| Marketing Campaign Manager | Owns individual campaign execution, writes briefs |
| Product Marketing Manager | Provides product positioning, messaging hierarchy, competitive context |
| Marketing Ops Lead | Assesses execution capacity, platform constraints, data availability |
| Analytics Lead | Provides performance data, propensity model outputs, segment sizing |

#### Activities

- Break annual plan into quarterly campaign sprints
- Prioritise campaigns by expected revenue impact and strategic importance
- Assign campaign owners and cross-functional teams
- Define audience hypotheses (who to target, why, expected response rate)
- Create campaign briefs with objectives, target segments, channels, and success criteria
- Estimate resource requirements (creative, data, compliance, channel execution)

#### Data Needs

- YTD performance vs. plan
- Pipeline conversion rates by product
- Seasonal demand patterns (e.g., mortgage activity peaks in spring)
- Product launch roadmap (upcoming rate changes, new products)
- Available inventory (promotional rate offers, promo codes, limited-time deals)

#### Deliverables

- Campaign brief per initiative (Word document, typically 3–5 pages)
- Quarterly campaign backlog (managed in Jira, Asana, or Excel)
- Audience hypothesis document
- Channel mix recommendation per campaign

#### Pain Points

- Briefs are Word documents emailed around with no single source of truth
- Campaign priorities shift mid-quarter with no formal change control process
- No standardised brief template — quality varies by campaign manager
- Capacity planning is manual and frequently inaccurate

#### Duration

- 2–3 weeks per quarter

---

## Phase 2: Campaign Design & Creative Production

### 2a. Creative Briefing & Copywriting

**Objective:** Produce all campaign copy across channels, aligned to brand and product requirements.

#### Personas Involved

| Persona | Role in This Phase |
|---|---|
| Campaign Manager (Brief Owner) | Writes creative brief, manages feedback cycle |
| Copywriter (Internal or Agency) | Produces all copy variants across channels |
| Brand Manager | Ensures tone of voice and brand guideline compliance |
| Product SME (Rates, Features) | Provides accurate product information, rate calculations |

#### Activities

- Write campaign copy: headlines, body copy, CTAs, email subject lines
- Create multiple variants for A/B testing (typically 3–5 headline variants, 2–3 body variants)
- Develop product messaging hierarchy (primary benefit, secondary benefits, proof points)
- Write T&C summaries and representative APR examples
- Produce copy for each channel:
  - Email (HTML template copy, preheader text)
  - Web landing page (hero headline, body, form labels, CTA)
  - Social media posts (per platform: LinkedIn, Facebook, Instagram, Twitter/X)
  - Display advertising (short-form copy per ad size)
  - Branch poster / point-of-sale (headline + key offer)
  - SMS (160-character limit)
  - Direct mail letter (personalised salutation, body, CTA)

#### Data Needs

- Product feature specs and current rates
- Brand tone of voice guidelines
- Prior A/B test results (winning subject lines, CTA performance)
- Representative APR calculations (verified by product pricing team)
- FCA financial promotions rules (COBS 4)
- Competitor messaging analysis

#### Deliverables

- Copy deck (all variants, all channels — typically a Word document or Google Sheet)
- Subject line variants (5–10 options)
- Landing page wireframe with copy
- Social post copy (per platform, including hashtags and character counts)
- SMS copy (160-character limit, multiple variants)
- Direct mail letter copy

#### Pain Points

- 3–5 revision cycles between copywriter, brand manager, and product SME
- No automated compliance pre-check — copy goes to compliance "blind"
- Copy is manually adapted per channel (not generated from a single source of truth)
- No dynamic content capability — same message for all customers in a segment
- Agency turnaround for copy: 5–7 days, plus 2–3 days per revision cycle

#### Duration

- 5–10 business days

---

### 2b. Design & Asset Production

**Objective:** Produce all visual assets across channels from approved copy.

#### Personas Involved

| Persona | Role in This Phase |
|---|---|
| Graphic Designer / Agency Creative | Produces visual assets from brief |
| UX Designer (Digital Assets) | Designs landing pages, web components, app interstitials |
| Email Developer (HTML Templates) | Builds responsive HTML email templates |
| Video Producer (If Applicable) | Scripts and produces video content |

#### Activities

- Produce visual assets: hero banners, display ad creative (all sizes), email HTML templates, social media graphics, branch POS materials, direct mail artwork
- Build landing pages in CMS (Adobe Experience Manager, Sitecore, or WordPress)
- Develop responsive email templates in Salesforce Marketing Cloud or Adobe Campaign
- Create print-ready PDFs for direct mail fulfilment
- Ensure all assets meet brand guidelines (logos, colours, fonts, imagery style)
- Ensure accessibility compliance (WCAG 2.1 — alt text, contrast ratios, screen reader compatibility)

#### Data Needs

- Brand guidelines (logos, colour palette, typography, imagery style)
- Image library / DAM access
- Channel specification sheets (ad sizes, email width, social image dimensions)
- CMS template constraints and component library
- Accessibility standards (WCAG 2.1)

#### Deliverables

- Display ad creative (6–8 sizes per campaign)
- Email HTML template (responsive, tested across 20+ email clients)
- Landing page (live in CMS staging environment)
- Social media assets (per platform and format)
- Branch POS materials (posters, leaflets, digital screen content)
- Direct mail artwork (print-ready, CMYK)
- Video assets (if applicable)

#### Pain Points

- Each channel format produced separately — no dynamic creative optimisation
- Agency turnaround: 7–14 business days for full asset set
- Version control nightmare across 20+ asset variants
- No automated resizing or format adaptation
- Rate or T&C changes require re-production of ALL assets

#### Duration

- 7–15 business days

---

### 2c. Image & Visual Asset Production

**Objective:** Source, create, and adapt images across all required formats and channels.

#### 2c-i. Image Sourcing & Creation

##### Personas Involved

| Persona | Role in This Phase |
|---|---|
| Art Director / Creative Lead | Sets visual direction, approves imagery |
| Graphic Designer | Creates illustrations, infographics, retouches photography |
| Photography Agency | Executes commissioned photo shoots |
| Stock Image Researcher | Sources and licenses stock photography |
| Brand Manager (Approver) | Ensures imagery meets brand and D&I standards |

##### Activities

- Source hero images: commission photography for major campaigns (diverse talent, branch settings, lifestyle shots) or license from stock libraries (Getty, Shutterstock, Adobe Stock)
- Research and select images aligned to campaign brief and brand guidelines
- Create original illustrations, icons, and infographics for product explainers
- Retouch and colour-correct all images
- Ensure diversity and inclusion representation standards are met
- Clear model release and usage rights for all commissioned photography

##### Data Needs

- Brand image style guide
- Diversity & inclusion representation guidelines
- Stock library licences and budget allocation
- Model release / usage rights database
- DAM (digital asset management) library of existing approved images
- Prior campaign image performance data (click-through by image type)

##### Deliverables

- Hero images (high-resolution master files, typically 300dpi TIFF/PSD)
- Product illustrations / infographics (vector SVG + raster PNG)
- Icon sets (SVG, PNG at multiple resolutions)
- Image usage rights log (licence type, expiry date, usage restrictions)

---

#### 2c-ii. Multi-Format Image Adaptation

##### Personas Involved

| Persona | Role in This Phase |
|---|---|
| Production Designer (Resize Specialist) | Adapts master creative to all required formats |
| Agency Studio / Artworker | Produces format variants at scale |

##### Activities

Adapt master creative into all required formats. This is one of the most labour-intensive steps in the entire marketing process:

**Display Advertising Formats:**
- 728x90 (leaderboard)
- 300x250 (medium rectangle)
- 160x600 (wide skyscraper)
- 320x50 (mobile banner)
- 300x600 (half page)
- 970x250 (billboard)
- Typically 6–8 sizes per campaign

**Social Media Formats:**
- Facebook: 1200x628 (link share)
- Instagram: 1080x1080 (feed), 1080x1920 (stories)
- LinkedIn: 1200x627 (sponsored content)
- Twitter/X: 1600x900 (summary card)
- Stories/Reels: 1080x1920 (vertical video/image)

**Email Formats:**
- Hero banner: 600px wide
- Product tiles: various sizes
- CTA buttons
- Mobile-optimised variants

**Web / App Formats:**
- Landing page hero (desktop + mobile responsive)
- Product cards
- Promotional banners (homepage, category pages)
- App interstitials

**Branch / Out-of-Home Formats:**
- A1 posters
- A5 leaflets
- Digital screen content (16:9)
- Window vinyl
- ATM screen graphics

**Direct Mail Formats:**
- DL envelope artwork
- A4 letter (personalised)
- A5 insert
- Self-mailer — all print-ready CMYK with bleed marks

##### Deliverables

- 25–40 image variants per campaign
- All files tagged and uploaded to DAM
- Format specification checklist (signed off by production manager)

##### Pain Points

- A single campaign generates 25–40 image variants, each manually produced
- A rate change means re-creating ALL variants across all formats
- No automated resizing or dynamic text overlay capability
- Agency charges per-format, driving up production costs
- Turnaround: 5–10 business days for full format set
- Version control across 40 files is chaotic — wrong version goes live regularly

##### Duration

- 5–10 business days for full format set

---

### 2d. PDF Generation & Document Production

**Objective:** Produce all PDF documents including product brochures, T&Cs, rate sheets, and personalised customer correspondence.

#### 2d-i. Static PDF Production (Brochures, Guides, T&Cs)

##### Personas Involved

| Persona | Role in This Phase |
|---|---|
| Graphic Designer (InDesign Specialist) | Produces layouts in Adobe InDesign |
| Copywriter | Provides content for brochures and guides |
| Product Manager (Content Owner) | Owns accuracy of product information |
| Compliance Officer (Sign-Off) | Approves all customer-facing content |
| Web Team | Uploads approved PDFs to website document library |

##### Activities

- Produce product brochures (mortgage guide, business loan overview, card comparison)
- Create terms & conditions documents, fee schedules, rate sheets
- Build compliance-mandated disclosure documents
- All built in Adobe InDesign
- Export as print-ready PDF (CMYK, bleed marks) and web-optimised PDF (RGB, compressed)
- Apply accessibility tagging for WCAG compliance (tagged PDF, alt text, reading order)
- Manage version control: every rate or T&C change triggers a full re-production cycle

##### Document Types Produced

| Document Type | Description | Update Frequency |
|---|---|---|
| Product Brochures | 4–12 page PDF per product (mortgage, loans, cards, savings, business banking) | Quarterly or on rate change |
| T&Cs / Key Facts Documents (KFDs) | Legally mandated format, summary boxes, full terms. Must match live product exactly | On any product change |
| Rate Sheets | Current rates for all products. Published to website and distributed to branches | Weekly or on-demand |
| Guides & How-Tos | First-time buyer guide, business loan checklist, switching guide. Evergreen content | Refreshed annually |

##### Data Needs

- Current product rates and fees (from pricing system)
- Legal T&Cs (latest approved version from legal team)
- Representative APR calculations
- FCA disclosure requirements
- Brand templates (Adobe InDesign .indt files)
- WCAG 2.1 accessibility standards
- Version history / change log

##### Deliverables

- Print-ready PDF (CMYK, with bleed and crop marks)
- Web-optimised PDF (RGB, compressed, tagged for accessibility)
- Accessibility-compliant PDF (tagged, with alt text and reading order)
- Published to website / document library
- Branch distribution (print run via fulfilment house)

##### Pain Points

- Rate change = every brochure and rate sheet must be re-produced, re-approved, and re-uploaded
- A single rate change can trigger 15–20 PDF updates across the product range
- No dynamic PDF generation from a data source — all manual InDesign work
- Accessibility compliance is manual and frequently incomplete
- Outdated PDFs remaining on the website are a significant regulatory risk
- No automated link between the pricing system and document production
- Designer dependency creates bottleneck — typically 1–2 designers handle all document production

##### Duration

- 3–7 business days per document
- Rate change cascade: 2–3 weeks to update all affected documents

---

#### 2d-ii. Personalised Document Generation (Letters, Offers, Application Packs)

##### Personas Involved

| Persona | Role in This Phase |
|---|---|
| Document Composition Team | Manages templates and batch generation |
| Print Fulfilment Vendor | Handles print, pack, and post |
| CRM / Marketing Ops | Provides audience data files |
| Compliance (Template Approval) | Approves all letter templates |
| Data Protection Officer | Ensures GDPR compliance for personalised data usage |

##### Activities

- Generate personalised PDFs at scale: pre-approval letters, offer documents, welcome packs, annual statements, direct mail letters
- Merge customer data (name, address, product details, rates, limits) into approved templates
- Use document composition tools (OpenText Exstream, Quadient Inspire, or legacy mainframe print systems)
- Apply conditional logic (different paragraphs for different products, rate tiers, customer segments)
- Generate print-ready output for fulfilment house (AFP, PostScript, or PDF format)
- Generate digital PDF for email attachment or online portal/document vault
- Archive every generated document for regulatory retention (minimum 6 years, often longer)

##### Data Needs

- Customer personal data (name, address, date of birth)
- Product-specific data (rate, credit limit, loan term, monthly payment)
- Approved letter/offer templates (in composition tool format)
- Conditional logic rules (which paragraphs for which products/segments)
- Postal address file (PAF validated for Royal Mail)
- Regulatory retention rules (by document type)
- Digital delivery preferences (post vs. email vs. portal)

##### Deliverables

- Personalised PDF letters (batch — typically thousands per run)
- Print-ready output file (AFP/PostScript/PDF for fulfilment house)
- Digital PDF for portal or email delivery
- Document archive (regulatory retention — indexed, searchable)
- Fulfilment house delivery manifest

##### Pain Points

- Legacy document composition tools (often 10–15 years old, specialist skills required)
- Template changes require specialist developer — no self-serve for marketing
- Batch-only processing — no real-time single-document generation capability
- Print and digital versions maintained separately (duplicate effort)
- Archive and retrieval is slow and often unreliable
- Personalisation limited to mail-merge fields, not dynamic content blocks or AI-driven personalisation

##### Duration

- Template change: 2–4 weeks (including compliance re-approval)
- Batch run: 1–3 business days
- Print fulfilment: 5–10 business days (print, pack, post)

---

### 2e. Video & Rich Media Production

**Objective:** Produce explainer videos, social media content, and branch digital screen assets.

#### Personas Involved

| Persona | Role in This Phase |
|---|---|
| Video Producer / Agency | Manages end-to-end video production |
| Motion Graphics Designer | Creates animations, animated infographics |
| Scriptwriter | Writes video scripts aligned to campaign messaging |
| Voiceover Artist | Records narration |
| Compliance Officer (Script Approval) | Reviews and approves script before production |
| Social Media Manager (Format Specs) | Specifies platform requirements and best practices |

#### Activities

- Script product explainer videos (60–90 seconds)
- Produce social media shorts (15–30 seconds)
- Create branch digital screen loops (10–15 seconds, no audio)
- Produce motion graphics and animate infographics
- Record voiceover narration
- Edit for each platform format
- Add captions/subtitles for accessibility compliance
- Compliance review of all scripts before production begins
- Separate compliance approval for final cut

#### Format Variants Per Video

| Platform | Aspect Ratio | Duration | Notes |
|---|---|---|---|
| YouTube / Web | 16:9, 1080p | 60–90s | With separate captions file (.srt) |
| Instagram / TikTok | 9:16 (vertical) | 15–30s | Burned-in captions, hook in first 3 seconds |
| LinkedIn / Facebook | 1:1 or 4:5 | 30–60s | Silent-first design, prominent text overlays |
| Branch Digital Screens | 16:9 loop | 10–15s | No audio, large text, high contrast |

#### Data Needs

- Approved script / storyboard
- Product information (rates, features, eligibility)
- Brand motion guidelines (animation style, transitions, colour usage)
- Platform format specifications
- Music / audio licensing
- Accessibility / caption requirements

#### Deliverables

- Master video file (ProRes / H.264)
- Platform-specific exports (4–6 per video)
- Caption / subtitle files (.srt, .vtt)
- Thumbnail images (per platform)
- Branch screen content package

#### Pain Points

- Video production is expensive (£5,000–£15,000 per video) and slow (3–6 weeks)
- Rate changes make videos stale immediately — no dynamic text overlay capability
- Each platform format is a separate edit (not automated)
- Compliance reviews the script AND the final cut — double approval gate
- No AI-assisted video generation or automated resizing/reformatting
- Captioning is manual

#### Duration

- 3–6 weeks per video (end-to-end)
- Format adaptation: 2–3 additional business days

---

### 2f. Digital Asset Management & Distribution

**Objective:** Organise, version-control, and distribute all approved campaign assets to stakeholders.

#### Personas Involved

| Persona | Role in This Phase |
|---|---|
| DAM Administrator | Manages asset library, tagging taxonomy, access permissions |
| Marketing Ops Lead | Assembles campaign kits for channel teams |
| Brand Manager | Ensures only approved, current assets are in circulation |
| Campaign Manager (Kit Requestor) | Requests assembled campaign kits for execution |
| Branch Ops (Kit Consumer) | Receives and distributes materials to branch staff |
| External Agency (Asset Uploader) | Uploads produced assets to bank's DAM |

#### Activities

- Upload all approved assets to DAM (Adobe Experience Manager, Bynder, Brandfolder, or shared drive)
- Tag with metadata: campaign name, product, channel, format, approval date, expiry date, usage rights
- Assemble campaign kits for each channel team:
  - **Email kit:** HTML template + images + copy
  - **Paid media kit:** Creative per ad size + landing page URLs
  - **Branch kit:** Posters + leaflets + talk tracks + objection handlers
  - **Direct mail kit:** Artwork + data file + print spec
- Manage version control — supersede old versions when rates/T&Cs change
- Set expiry dates and automated alerts for time-limited offers
- Distribute kits to stakeholders via email or internal portal

#### Data Needs

- All approved creative assets (from phases 2a–2e)
- Compliance approval certificates (per asset)
- Metadata taxonomy / tagging schema
- Campaign calendar (for expiry dates)
- Usage rights / licence expiry dates (for stock imagery and commissioned photography)
- Distribution lists (who gets what kit for which campaign)

#### Deliverables

- Organised DAM library (tagged, versioned, searchable)
- Campaign kit per channel (assembled and distributed)
- Asset expiry alert schedule
- Version audit trail
- Usage rights tracker

#### Pain Points

- Many banks still use shared drives (SharePoint / network folders) rather than a proper DAM
- No automated tagging or intelligent search
- Expired assets found live on the website months after campaign end
- Campaign kits assembled manually by marketing ops — takes 1–2 days per campaign
- Agencies upload to their own systems, not the bank's DAM — creating fragmented asset storage
- No single source of truth for "current approved version"
- Branch staff can't find assets and create their own non-compliant materials

#### Duration

- Kit assembly: 1–2 business days per campaign
- DAM maintenance: ongoing, approximately 0.5 FTE

---

### 2g. Landing Page & Web Content Production

**Objective:** Build campaign landing pages, lead capture forms, and update product pages on the bank's website.

#### Personas Involved

| Persona | Role in This Phase |
|---|---|
| Web Content Manager | Builds pages in CMS, manages content calendar |
| UX Designer | Designs page layouts, user flows, form designs |
| Front-End Developer (If Custom Build) | Implements custom components beyond CMS templates |
| SEO Specialist | Optimises metadata, content structure, schema markup |
| Compliance Officer (Web Content Sign-Off) | Approves all customer-facing web content |
| Analytics Team (Tracking Setup) | Configures GA4 events, conversion pixels, UTM parameters |

#### Activities

- Build campaign landing pages in CMS (Adobe Experience Manager, Sitecore, WordPress)
- Implement approved copy and images
- Set up lead capture forms with required fields and validation
- Configure tracking: GA4 events, conversion pixels, UTM parameter capture
- Implement A/B test variants (headline, CTA, hero image)
- Set up SEO metadata (title, description, schema markup)
- QA across browsers and devices (Chrome, Safari, Firefox, Edge; iOS, Android; desktop, tablet, mobile)
- Stage for compliance review, then publish
- Update product pages with campaign messaging
- Link from homepage banners and navigation

#### Data Needs

- Approved copy and images (from phases 2a and 2c)
- CMS template / component library
- Form field requirements (what data to capture, mandatory vs. optional)
- Tracking / pixel configuration (GA4 measurement IDs, Meta Pixel, Google Ads tag)
- SEO keyword research
- A/B test plan (hypothesis, variants, success metric, sample size)
- CRM form integration configuration (lead routing rules)

#### Deliverables

- Live landing page (staged, compliance-reviewed, then published)
- Lead capture form (integrated with CRM for automated lead creation)
- Tracking confirmation (GA4 events firing, conversion pixels verified)
- A/B test live in optimisation tool (Optimizely, VWO, or Google Optimize)
- Updated product pages

#### Pain Points

- CMS publishing requires developer involvement for anything beyond basic template fills
- Landing page build takes 5–10 business days
- No dynamic content personalisation on web pages (everyone sees the same content)
- Form-to-CRM integration is fragile and breaks silently (leads lost)
- SEO is an afterthought, not embedded in the content creation workflow
- A/B testing tools (Optimizely, VWO) are separate from CMS — duplicate effort and content drift

#### Duration

- Landing page: 5–10 business days
- Product page updates: 2–3 business days

---

## Phase 3: Audience Segmentation & Data Preparation

### 3a. Segment Definition & List Build

**Objective:** Translate campaign audience hypotheses into targetable data files with all required suppressions applied.

#### Personas Involved

| Persona | Role in This Phase |
|---|---|
| CRM / Database Marketing Analyst | Writes SQL queries, builds segments, applies suppressions |
| Data Engineer | Manages data pipelines, data quality, extract processes |
| Campaign Manager (Requestor) | Defines audience hypothesis, reviews segment counts |
| Data Protection Officer (DPO) | Ensures GDPR compliance, approves DPIAs for new data usage |

#### Activities

- Translate campaign brief audience hypothesis into SQL queries against data warehouse / CDP
- Build propensity models or use existing ones (e.g., mortgage propensity, churn risk, cross-sell likelihood)
- Apply marketing consent filters (opt-in status, channel preference)
- Apply regulatory suppressions:
  - Customers in collections or arrears
  - Vulnerable customer flags
  - Recent complaint flags
  - Deceased / gone-away markers
  - Do-not-contact registers
- Deduplicate across concurrent campaigns (contact fatigue rules — e.g., max 2 marketing contacts per customer per month)
- Produce final audience file with personalisation fields (name, product holding, segment, offer code)

#### Data Needs

- Customer master data (from core banking system)
- Transaction history (12–24 months)
- Product holdings and balances
- Marketing consent / opt-in flags (GDPR compliant)
- Channel preferences (email, post, SMS, phone)
- Propensity model scores
- Collections / arrears flags
- Vulnerable customer register
- Recent contact history (for fatigue rules)
- Credit bureau data (for pre-approval campaigns)

#### Deliverables

- Audience file (CSV or SFTP drop to email/direct mail platforms)
- Segment count summary (total audience, breakdown by sub-segment)
- Suppression log (audit trail of all exclusions applied, with reasons)
- Data quality report (match rates, missing fields, duplicate rates)
- DPIA (Data Protection Impact Assessment — if new data usage)

#### Pain Points

- Analyst dependency creates a 3–5 business day bottleneck per list build
- Static snapshot segments (not real-time or dynamic)
- Suppression rules are tribal knowledge — not documented or automated
- No self-serve capability for campaign managers
- Data quality issues (missing email addresses, outdated postal addresses) discovered too late
- Propensity models refreshed infrequently (monthly or quarterly, not real-time)

#### Duration

- 3–7 business days per audience build

---

## Phase 4: Compliance & Regulatory Review

### 4a. Financial Promotions Compliance

**Objective:** Obtain FCA-compliant sign-off for all customer-facing marketing content.

#### Personas Involved

| Persona | Role in This Phase |
|---|---|
| Compliance Officer (Financial Promotions) | Reviews content against FCA rules, provides feedback |
| Legal Counsel | Reviews T&Cs, disclaimers, contractual language |
| Product Pricing Team | Verifies rates, APR calculations, fee accuracy |
| Campaign Manager (Submitter) | Submits materials, manages revision cycle |
| Senior Manager (s166 Accountable) | Provides final sign-off as the accountable individual |

#### Activities

- Review all customer-facing content against FCA COBS 4 (financial promotions rules)
- Verify representative APR examples are accurate and up-to-date
- Check risk warnings and disclaimers are prominent and not obscured
- Assess Consumer Duty fair value alignment
- Review for clarity, fairness, and not being misleading
- Check vulnerable customer considerations
- Verify all T&Cs are current and match the live product
- Sign-off chain: compliance officer → legal counsel → senior manager
- Track all versions and redline comments (typically in Word with Track Changes)

#### Data Needs

- Current product rates and charges (verified against pricing system)
- FCA Handbook COBS 4 rules
- Consumer Duty outcomes framework
- Prior compliance decisions (precedent library)
- Competitor promotion samples (for benchmarking)
- Current T&Cs and legal disclaimers
- Vulnerable customer policy

#### Deliverables

- Compliance approval certificate (per asset)
- Redlined copy with amendments (Word document with Track Changes)
- Financial promotion approval log (centralised register)
- Risk warning templates (approved, reusable)
- Audit trail document (for FCA inspection readiness)

#### Pain Points

- **This is the single biggest bottleneck in the entire marketing process**
- 5–15 business days per asset, often extending to 20+ with revisions
- Manual Word document redlining — no digital workflow tool
- Compliance team reviews 50–100 promotions per month with only 3–4 staff
- 2–4 revision cycles per asset on average
- No pre-screening tool to catch common issues before formal submission
- Inconsistent decisions across different compliance reviewers
- Rate changes require re-approval of ALL live marketing materials
- No automated link between pricing system changes and compliance re-review triggers

#### Duration

- 5–15 business days per asset
- Often 20+ business days with revisions
- Rate change re-approval cascade: 2–4 weeks

---

## Phase 5: Channel Execution & Campaign Launch

### 5a. Email & CRM Execution

**Objective:** Build, test, and deploy email campaigns through the marketing automation platform.

#### Personas Involved

| Persona | Role in This Phase |
|---|---|
| Email Marketing Specialist | Builds campaigns in ESP, manages send schedule |
| Marketing Automation Admin | Configures automation rules, journey flows |
| QA Tester | Tests email rendering across clients and devices |

#### Activities

- Build email in Salesforce Marketing Cloud or Adobe Campaign
- Import audience file (from Phase 3)
- Set up A/B test splits (subject line, content, send time)
- Configure send schedule and throttling (to protect deliverability)
- Test rendering across 20+ email clients using Litmus or Email on Acid
- Set up tracking pixels and UTM parameters
- Execute send
- Monitor deliverability, bounce rates, and spam complaints in first 24 hours

#### Data Needs

- Approved audience file (with personalisation fields)
- Approved HTML email template
- Personalisation merge fields (first name, product, offer code)
- Send schedule (date, time, timezone)
- UTM tracking parameters (source, medium, campaign, content)
- Suppression / unsubscribe list (real-time)

#### Deliverables

- Campaign live in ESP (email service provider)
- Send confirmation report
- Deliverability report (24-hour post-send)

---

### 5b. Paid Media / Digital Advertising

**Objective:** Launch and optimise digital advertising campaigns across paid channels.

#### Personas Involved

| Persona | Role in This Phase |
|---|---|
| Paid Media Manager | Manages campaign setup, budget allocation, optimisation |
| Programmatic Buyer / Agency | Executes programmatic display and video buying |
| Social Media Manager | Manages paid social campaigns |

#### Activities

- Upload creative to Google Ads, Meta Business Manager, programmatic DSP (DV360, The Trade Desk)
- Build custom audiences: 1st party data match (hashed email lists), lookalike audiences, interest-based targeting
- Set bid strategies, daily/campaign budgets, dayparting schedules
- Launch campaigns
- Monitor pacing, CPM, CPC, CTR daily
- Optimise bids and creative rotation daily/weekly
- Pause underperforming variants, increase budget on winners

#### Data Needs

- Approved display / video creative (all sizes)
- Customer match lists (hashed email addresses for 1st party targeting)
- Conversion pixel / tag setup (on landing pages and application forms)
- Budget and bid parameters
- Landing page URLs (with UTM parameters)

#### Deliverables

- Live campaigns across all ad platforms
- Daily performance dashboard
- Weekly optimisation report

---

### 5c. Direct Mail & Branch Execution

**Objective:** Execute physical marketing campaigns through print fulfilment and branch distribution.

#### Personas Involved

| Persona | Role in This Phase |
|---|---|
| Direct Mail Coordinator | Manages fulfilment house relationship, production schedule |
| Print Fulfilment Vendor | Handles print, pack, and post operations |
| Branch Operations Manager | Distributes materials to branch network |
| Relationship Managers (RMs) | Delivers campaign offers in customer conversations |

#### Activities

- Send print-ready artwork and audience address file to fulfilment house
- Coordinate print, pack, and post (including Royal Mail delivery schedule)
- Distribute branch materials (posters, leaflets, talk tracks) via internal comms
- Brief RMs on campaign offers and eligibility criteria
- Update in-branch digital screens with campaign content

#### Data Needs

- Postal address file (PAF validated for Royal Mail)
- Print specifications (paper weight, finish, size, fold)
- Branch distribution list (which branches get which materials)
- RM talk track / objection handler document

#### Deliverables

- Mail drop confirmation (proof of posting)
- Branch kit distributed (with confirmation from branch ops)
- RM briefing completed (attendance record)

#### Pain Points (Across All Channels)

- Siloed execution — no unified orchestration layer
- Each channel has its own platform, schedule, and audience file
- RM often learns about campaigns late (after customers have already received emails)
- No cross-channel frequency cap (customer may receive email, SMS, and direct mail on the same day)
- Direct mail has 3–4 week lead time (vs. email which can be deployed in hours)
- No dynamic creative — same message for every customer in the segment

#### Duration

- Email: 1–2 business days
- Paid media: 2–3 business days for setup
- Direct mail: 3–4 weeks (print + post)

---

## Phase 6: Lead Capture, Scoring & Routing

### 6a. Lead Capture & Ingestion

**Objective:** Capture all campaign responses from all channels into a unified CRM record.

#### Personas Involved

| Persona | Role in This Phase |
|---|---|
| Marketing Ops Analyst | Manages lead ingestion, deduplication, tagging |
| Web / Digital Team | Maintains lead capture forms and tracking |
| Call Centre Manager | Ensures inbound calls are tagged to campaigns |
| Branch Front Desk | Captures walk-in enquiries in CRM |

#### Activities

- Capture leads from:
  - Web forms (product pages, campaign landing pages)
  - Call centre inbound (IVR tagged to campaign source)
  - Branch walk-ins (manual CRM entry by staff)
  - Online applications (started but not completed — abandon capture)
  - Social media enquiries (DMs, comments)
- Ingest into CRM (Salesforce)
- Deduplicate against existing customer base
- Tag with campaign source and UTM parameters
- Enrich with available data (existing product holdings, segment)

#### Data Needs

- Web form submissions (real-time via API or batch)
- Call centre interaction logs (with campaign tagging)
- Branch footfall / enquiry log
- Online application abandon data (from application platform)
- UTM / campaign source tagging
- Existing customer match data (for deduplication)

#### Deliverables

- Unified lead record in CRM (one record per prospect, regardless of source)
- Lead source attribution tag (which campaign, which channel)
- Daily lead volume report

---

### 6b. Lead Scoring & Routing

**Objective:** Qualify leads by value and intent, route to the appropriate team for follow-up.

#### Personas Involved

| Persona | Role in This Phase |
|---|---|
| Marketing Ops Analyst (Manual Triage) | Scores and assigns leads manually |
| Sales / RM Team Leader | Manages lead queue, assigns to individual RMs |
| Commercial Lending RM | Handles high-value commercial leads |
| Retail Product Specialist | Handles retail product enquiries |

#### Activities

- Apply basic scoring rules (if any): product type, estimated deal value, customer tier
- Route to appropriate team:
  - High-value commercial leads → Relationship Manager
  - Retail mortgage leads → Mortgage broker desk
  - Retail product leads → Call centre or digital self-serve
  - Existing customer cross-sell → Account manager
- Assign in CRM
- Set SLA for first contact (e.g., 4 hours for commercial, 24 hours for retail)
- Monitor queue depth and response times

#### Data Needs

- Lead details (name, product interest, estimated value)
- Customer tier / segment (existing customer? which segment?)
- RM availability / capacity
- Product eligibility rules
- SLA targets by segment

#### Deliverables

- Scored and assigned leads in CRM
- RM notification (email or CRM task)
- Queue depth dashboard
- SLA adherence report

#### Pain Points

- Scoring is rudimentary or non-existent — a £5M commercial lending enquiry gets the same priority as a student account signup
- Manual triage by junior marketing ops staff
- Routing rules are hardcoded and inflexible
- Response time to high-value leads: 24–72 hours (vs. industry best practice of <1 hour)
- No real-time alerting for high-value leads
- Branch leads often not captured in CRM at all (lost in paper notes)

#### Duration

- 24–72 hours from lead capture to first contact

---

## Phase 7: Nurture, Follow-Up & Conversion

### 7a. Automated Nurture Journeys

**Objective:** Re-engage non-converting leads through automated multi-touch campaigns.

#### Personas Involved

| Persona | Role in This Phase |
|---|---|
| Marketing Automation Specialist | Builds and manages nurture journeys in MAP |
| Content Writer (Nurture Emails) | Creates drip email content |
| Campaign Manager | Defines nurture strategy and success criteria |

#### Activities

- Enrol non-converting leads into drip email sequences (3–7 emails over 4–8 weeks)
- Set up retargeting audiences in ad platforms (sync CRM segments to Google/Meta)
- Schedule follow-up SMS for high-intent leads
- Trigger RM callback tasks for leads showing re-engagement signals
- Manage journey branching logic:
  - If opened email 2 → send variant A
  - If not opened → send variant B
  - If clicked but didn't apply → trigger RM callback
  - If applied but abandoned → send application reminder

#### Data Needs

- Lead engagement history (email opens, clicks, website visits)
- Website visit / page view data (from web analytics)
- Application status (started, abandoned, completed)
- Product eligibility (pre-approved? if so, for what?)
- Nurture sequence content library

#### Deliverables

- Active nurture journeys in marketing automation platform
- Retargeting audiences (synced to ad platforms)
- Nurture performance report (open rates, click rates, conversion by journey stage)
- Conversion / drop-off funnel analysis

---

### 7b. RM Follow-Up & Conversion Support

**Objective:** Enable relationship managers to convert warm leads through informed, personalised outreach.

#### Personas Involved

| Persona | Role in This Phase |
|---|---|
| Relationship Manager (RM) | Makes outbound calls to warm leads, conducts needs assessments |
| Product Specialist (Mortgage, Lending) | Provides specialist advice for complex products |
| Customer Service Agent | Handles general enquiries and application support |

#### Activities

- RM calls warm leads assigned via CRM
- Discuss product suitability, gather customer requirements
- Support application completion (walk customer through online or paper application)
- Handle objections (rate comparison, competitor offers)
- Escalate complex cases to product specialist
- Log all interactions in CRM
- Convert lead → opportunity → application in CRM pipeline

#### Data Needs

- Full customer 360 view (all products held, transaction history, contact history)
- Digital engagement history (which emails opened, which pages visited, which products browsed)
- Product eligibility / pre-approval status
- Competitor rate comparison data
- Next best action recommendation (if available)

#### Deliverables

- CRM interaction notes (call log, outcomes)
- Completed applications (submitted to origination system)
- Pipeline forecast update

#### Pain Points

- Nurture journeys are generic, pre-built, and the same for every customer in the segment
- No dynamic content adaptation based on individual behaviour
- RM has no visibility into which digital touchpoints the customer engaged with before the call
- No next-best-action engine to guide RM conversations
- RM follow-up is inconsistent — competing priorities, no accountability tracking
- Application drop-off rate: 40–60% with no automated save/resume capability

#### Duration

- 4–12 week nurture cycle

---

## Phase 8: Measurement, Attribution & Optimisation

### 8a. Campaign Performance Reporting

**Objective:** Consolidate performance data across all channels into unified campaign dashboards.

#### Personas Involved

| Persona | Role in This Phase |
|---|---|
| Marketing Analytics Lead | Designs dashboards, defines metrics, presents to leadership |
| BI / Data Analyst | Pulls data from source systems, builds reports |
| Campaign Manager (Consumer) | Reviews performance, identifies optimisation opportunities |
| CMO (Executive Summary) | Reviews top-line performance, makes investment decisions |

#### Activities

- Pull data from each channel platform:
  - Email: Salesforce Marketing Cloud / Adobe Campaign
  - Paid media: Google Ads, Meta Ads Manager, DV360
  - Web: Google Analytics 4 / Adobe Analytics
  - CRM: Salesforce (leads, opportunities)
  - Call centre: Interaction logs with campaign tags
  - Branch: Enquiry data (often manual)
- Manually consolidate into campaign dashboard (Tableau, Power BI, or Excel)
- Calculate KPIs: open rate, CTR, conversion rate, CPA, CPL, ROAS
- Compare performance against targets
- Produce weekly in-flight reports and end-of-campaign reports
- Present to CMO and product heads

#### Data Needs

- Email metrics (sends, opens, clicks, bounces, unsubscribes — from ESP)
- Paid media metrics (impressions, clicks, conversions, spend — from platform APIs)
- CRM lead / opportunity data (volume, status, conversion rates)
- Web analytics (sessions, bounce rate, goal completions — from GA4)
- Call centre campaign-tagged interaction data
- Branch enquiry data

#### Deliverables

- Weekly campaign dashboard (live in Tableau/Power BI or static Excel)
- End-of-campaign report (PowerPoint, 10–15 slides)
- Channel performance comparison
- CMO executive summary (1-page)

---

### 8b. Attribution & ROI Analysis

**Objective:** Link marketing spend to originated products and calculate true return on investment.

#### Personas Involved

| Persona | Role in This Phase |
|---|---|
| Marketing Analytics Lead | Designs attribution model, produces ROI analysis |
| Finance Business Partner | Validates marketing spend figures, provides product revenue data |
| Data Scientist (If Available) | Builds multi-touch attribution models, marketing mix models |
| CMO | Makes budget reallocation decisions based on findings |

#### Activities

- Attempt to link marketing spend to originated products (loans booked, accounts opened, cards issued)
- Attribution model: typically last-touch (whoever gets credit for the final click/interaction)
- Try to reconcile marketing leads (in CRM) with origination system data (in core banking)
- Calculate true ROI by product and by channel
- Feed insights back to strategy for next planning cycle
- Identify highest-performing and lowest-performing campaigns for budget reallocation

#### Data Needs

- Origination system data (loans booked, accounts opened, cards issued — from core banking)
- Product revenue / net interest income (NII) by account
- Marketing spend by channel and by campaign
- Customer journey touchpoint data (all interactions across all channels)
- Lifetime value (LTV) models

#### Deliverables

- Attribution report by channel
- ROI analysis by campaign
- Marketing contribution to revenue (marketing-attributed originations)
- Recommendations for next quarter (budget reallocation, channel shifts, audience refinements)

#### Pain Points

- No closed-loop attribution — origination data lives in a different system (core banking) with no automated link to marketing CRM
- Last-touch attribution ignores multi-touch customer journeys (a customer may see a display ad, receive an email, visit a branch, then apply online — only the last touchpoint gets credit)
- Reports are backward-looking, produced 2–4 weeks after campaign end
- Finance and marketing use different numbers (different definitions of "marketing-attributed")
- No predictive modelling for budget reallocation
- Branch and call centre attribution is essentially guesswork
- No ability to measure incrementality (would the customer have converted anyway without the campaign?)

#### Duration

- 2–4 weeks post-campaign for full analysis

---

## Summary: Key Structural Weaknesses

| Weakness | Impact | Phases Affected |
|---|---|---|
| Compliance bottleneck | 5–20 day delay per asset, single biggest time-to-market killer | Phase 4 |
| No dynamic content/personalisation | Same message for every customer, low relevance, poor conversion | Phases 2, 5, 7 |
| Siloed channel execution | No unified orchestration, inconsistent customer experience | Phase 5 |
| Primitive lead scoring | High-value leads treated same as low-value, slow response times | Phase 6 |
| Broken attribution chain | Cannot link marketing spend to revenue, budget decisions based on guesswork | Phase 8 |
| Manual asset production | 25–40 image variants manually produced per campaign, rate changes cascade | Phases 2c, 2d |
| Legacy document composition | No dynamic PDF generation, 10–15 year old tools, specialist dependency | Phase 2d |
| No proper DAM | Expired assets live, branch staff create non-compliant materials | Phase 2f |
| Static audience segments | Snapshot-based, not real-time, analyst dependency for every list | Phase 3 |
| No closed-loop feedback | Insights from one campaign don't feed into the next before it's in production | Phase 8 → Phase 1 |

---

## Appendix: Complete Persona Registry

| # | Persona | Primary Phases |
|---|---|---|
| 1 | CMO / Head of Marketing | 1a, 8b |
| 2 | Product Heads (Retail, Commercial, Cards) | 1a, 1b |
| 3 | CFO / Finance Business Partner | 1a, 8b |
| 4 | Head of Digital | 1a |
| 5 | Marketing Campaign Manager | 1b, 2a, 4a |
| 6 | Product Marketing Manager | 1b |
| 7 | Marketing Ops Lead | 1b, 2f |
| 8 | Analytics Lead | 1b |
| 9 | Copywriter | 2a, 2d, 7a |
| 10 | Brand Manager | 2a, 2c, 2f |
| 11 | Product SME | 2a |
| 12 | Graphic Designer | 2b, 2c, 2d |
| 13 | UX Designer | 2b, 2g |
| 14 | Email Developer | 2b, 5a |
| 15 | Art Director / Creative Lead | 2c |
| 16 | Production Designer / Artworker | 2c |
| 17 | Video Producer | 2e |
| 18 | Motion Graphics Designer | 2e |
| 19 | DAM Administrator | 2f |
| 20 | Web Content Manager | 2g |
| 21 | SEO Specialist | 2g |
| 22 | CRM / Database Marketing Analyst | 3a |
| 23 | Data Engineer | 3a |
| 24 | Data Protection Officer | 3a, 2d |
| 25 | Compliance Officer | 4a, 2d, 2e, 2g |
| 26 | Legal Counsel | 4a |
| 27 | Paid Media Manager | 5b |
| 28 | Social Media Manager | 5b, 2e |
| 29 | Direct Mail Coordinator | 5c |
| 30 | Branch Operations Manager | 5c |
| 31 | Relationship Manager (RM) | 5c, 7b |
| 32 | Marketing Ops Analyst | 6a, 6b |
| 33 | Call Centre Manager | 6a |
| 34 | Marketing Automation Specialist | 7a |
| 35 | Marketing Analytics Lead | 8a, 8b |
| 36 | BI / Data Analyst | 8a |

---

*Document generated: March 2026*
*Context: As-is process mapping for agentic AI marketing automation opportunity assessment*
