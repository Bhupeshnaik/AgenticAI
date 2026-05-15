# Booth assets

Static media for the `/booth` HeyGen interactive avatar kiosk.

## Layout

```
booth-assets/
├── slides/      ← static SVG/PNG slides shown by [[ACTION:show_slide]]
├── demos/       ← MP4 demo videos shown by [[ACTION:show_demo]]
├── posters/     ← poster frames for the demo videos
└── idle/        ← attract-loop background (e.g. attract-loop.mp4)
```

## What ships in this repo

- `slides/architecture.svg`
- `slides/roi-summary.svg`
- `slides/phase-map.svg`

The slides are committed so the booth is usable end-to-end without any
external dependencies. Video files (`demos/*.mp4`, `idle/*.mp4`) are
intentionally **not** committed — they're large and tend to be event-specific.

## Adding your own

1. Render or export an MP4 — keep under 60 MB per file, H.264, AAC audio.
2. Drop it in `demos/` using the `id` you reference from the booth agent
   prompt (`backend/agents/booth_agent.py`). For example, `lead_routing` →
   `demos/lead-routing.mp4`.
3. Add a poster frame to `posters/` with the matching name (e.g.
   `posters/lead-routing.jpg`).
4. Restart `npm run dev`. No backend changes needed — the catalog in
   `backend/api/avatar.py` already references these filenames.

## Adding a new demo or slide

Edit the `DEMOS` / `SLIDES` lists in `backend/api/avatar.py`, then teach
the booth agent about the new `id` in `BOOTH_SYSTEM_PROMPT`.
