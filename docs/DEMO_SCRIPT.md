# Demo Script — Hackathon Gemini Paris 2026

---

## Presentation (3 min)

**[0:00 — Pain]**
> "France has digitized tens of millions of 19th-century civil records. They're online. But they're raw scans of handwritten manuscripts — unusable for any standard search engine. So today, tracing your family tree means going page by page, archive by archive, by hand. For years."

**[0:25 — The gap]**
> "MyHeritage, FamilySearch, Geneanet — they search their own pre-indexed databases. None of them navigate raw archives autonomously. Nobody does the full loop: find the right register, read the manuscript, extract the parents, climb to the next generation — without human input."

**[0:50 — What we built]**
> "Lignée is an autonomous genealogy agent. You give it a name and a birth year. It does the rest."

**[1:00 — Live demo]**
*(1-minute demo script below)*

**[2:00 — Why it's possible now]**
> "Two things make this possible in 2026. Gemini 2.5 Pro with a 1-million token context window — we can send an entire parish register in one shot. And gemini-embedding-2-preview, released March 10th, which puts text and images in the same vector space — so you can semantically search across extracted ancestor profiles. That combination didn't exist before."

**[2:30 — Scale]**
> "Arkotheque covers 80 French departments. Everything we built this weekend runs on any of them. The demo is Cher — it works just as well on Ardennes, Indre, Moselle. Millions of families, accessible for the first time."

**[2:55]**
> "That's Lignée."

---

## Live demo (1 min)

**[fill the form]**
> "We're looking for the ancestors of Prudence Aimée Pinçon, born in 1843 in the Cher."

**[hit SEARCH]**
> "The agent is now navigating the departmental archives on its own."

**[agents panel + OCR stream]**
> "It found the right register. It's reading the manuscript with Gemini Vision, extracting father and mother — and automatically launching the next generation."

**[tree builds live]**
> "The family tree builds in real time."

**[click Jean Pinçon → VIEW ALL DOCS]**
> "That's the original document. A raw 19th-century scan — not indexed data, actual reading."

**[click Henri Pinçon, blue node]**
> "If an ancestor was born after 1900, records are restricted. The app detects it and generates the official request letter for the relevant town hall."

**[done]**
> "80 departments. No human in the loop."

---

## Q&A

**"Why Arkotheque and not other archives?"**
> "Arkotheque covers 80 departments with a consistent API — it's the largest French archive platform. Extending to others is straightforward."

**"How do you handle ambiguous matches?"**
> "The agent surfaces a question to the user when there's ambiguity — you saw it in the demo, the popup anchored directly on the concerned node in the graph."

**"Cost per search?"**
> "Around 50 cents for 2–3 generations with Gemini 2.5 Pro. Fine for a premium service."

**"Is it scalable?"**
> "Backend on Cloud Run, each generation runs in parallel. Scales to zero, autoscales up."

---

## Pre-demo checklist

- [ ] B7 merged + backend running (`uv run uvicorn main:app --reload`)
- [ ] `GEMINI_API_KEY` with sufficient quota
- [ ] Full test run the day before — know the exact timing
- [ ] `VITE_MOCK=false` for live, `VITE_MOCK=true` as fallback if network fails
