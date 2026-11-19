# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Python 3 (existing CLI bot). Web UI: FastAPI + Jinja2 templates + vanilla JS, served locally by uvicorn. No build step, no external CDN needed at runtime.

## Users

One person: Jean-Luc Houédanou, a senior web developer / digital project lead based in Abidjan, looking for a new position. Uses the tool on a laptop and on a phone over the home Wi‑Fi. Not shared with anyone else; no accounts.

## Product Purpose

JobBot collects job offers (Novojob, Educarrière, Remotive, or pasted by hand), scores each against the user's CV with Claude, and prepares an application folder for the best ones: tailored CV, cover letter only when the offer asks for one, a short ready-to-send message. It never sends anything: the user reviews, then sends himself. Success = fewer minutes per good application and no missed or forgotten offer.

## Positioning

The CV (`cv.yaml`) is the single source of truth: the bot rewrites and reorders, it never invents. Guard-rails remove skills not in the CV, restore forgotten experiences, flag numbers absent from the CV, and flag offers asking for money (scams).

## Operating Context

- Daily routine: run collection in the morning, scan the ranking, open the best offers, prepare folders, review, copy the message into email/LinkedIn/WhatsApp, attach the PDFs.
- Tracking: offers move through à relire → envoyé → entretien → refus / ignoré; follow-ups after a few days.
- Offers are in French (Côte d'Ivoire) and English (remote).

## Capabilities and Constraints

- Data: local SQLite `jobbot.db`; folders in `candidatures/`.
- Claude API costs money: every scoring/writing action must be explicit and visible.
- Served on the local network for phone access: must be protected by a secret token.
- No LinkedIn/Indeed scraping (their terms forbid it); those offers are pasted by hand.

## Evidence on Hand

Real CV data in `cv.yaml` / `cv_en.yaml`, photo `photo.jpg`. No testimonials or metrics to show.

## Product Principles

1. Nothing leaves without review: the UI helps reading and checking, never auto-sends.
2. Truth over polish: warnings ("à vérifier", scam alert) are prominent, never buried.
3. Spend is deliberate: actions that call Claude are labelled as such.
4. Fast daily scan: the ranking answers "what deserves my attention today?" in seconds.

## Accessibility & Inclusion

French UI. Usable one-handed on a phone; readable in daylight.
