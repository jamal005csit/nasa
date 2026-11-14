# Challenge Crosswalk — source list

Numbered paraphrase of every explicit requirement and strong recommendation we found in `docs/official/`. The Crosswalk screen (P0.5 per SPEC §2 item 10) will consume this file, map each row to the screen that answers it, and show the status (Done / Partial / Deferred). Each row ends with a **source** tag pointing to the file the requirement came from.

**No row here is invented.** If the official text is silent on something, it does not appear below.

---

## A. Challenge-specific (what the project must do)

1. **Identify Earth-science variables of interest that can be investigated for potential trends.** [source: `challenge description.md` Objectives §1]
2. **Acquire the data variables for a particular region** (most trends are not global). [source: `challenge description.md` Objectives §2]
3. **Generate and visualise a time series** of the variable over a long enough period to allow statistical analysis. [source: `challenge description.md` Objectives §3]
4. **Perform a basic statistical analysis of that time series:** report the rate of change over time, and **test the trend's significance** using a method such as a t-test, Mann-Kendall, or confidence intervals. [source: `challenge description.md` Objectives §4]
5. **Both visualisation AND analysis** are required to meet the full scope of the challenge. [source: `challenge description.md` Objectives last line]
6. (Recommended) Provide **simple definitions of the variables** — the likely audience is high-school / college students plus scientifically-literate public. [source: `challenge description.md` Audience]
7. (Recommended) Frame the user as a **"data detective"**. [source: `challenge description.md` Audience]
8. (Recommended) **Guide users via a short series of questions** (what / where to investigate) that leads to the right data variable. [source: `challenge description.md` Approach]
9. (Recommended) **Provide one or two demonstration examples** the user can watch to understand the tool. [source: `challenge description.md` Approach]
10. (Recommended) **Daily or monthly data** are the easiest temporal resolutions for this challenge. [source: `challenge description.md` Working with the data]
11. (Allowed) A **non-significant trend is still interesting** — document it; do not filter it out. [source: `challenge description.md` Working with the data]
12. (Allowed) **Linear trend detection is a great starting point**; deseasonalising and nonlinear analyses are welcome but beyond the required scope. [source: `challenge description.md` Working with the data]

## B. Submission mechanics (must be present on the Project Submission page)

13. **Respond to one official NASA Space Apps Challenge.** [source: `judging and awards guide.pdf` Eligibility]
14. **Team size:** 1 permitted for Local only; **≥ 2 and ≤ 6** required for Universal Event and for Global-judging eligibility. [source: `judging and awards guide.pdf` Eligibility + `team formation.pdf` p.2]
15. **Submit by 2026-11-15 11:59 p.m. local time** via the project's team page. [source: `judging and awards guide.pdf` Eligibility]
16. **Complete all required fields** on the Project Submission page. [source: `judging and awards guide.pdf` Eligibility]
17. **Provide a demo** — either a slide presentation (**7-slide max**, including title/intro) or a **30-second video**. [source: `judging and awards guide.pdf` Eligibility]
18. **Project page and all linked materials in English.** If the demo is spoken in another language, **include English subtitles**. [source: `judging and awards guide.pdf` Eligibility]
19. **Tick the originality statement:** confirms the submission is original work, all external resources (code/text/images, including open-source) are listed in the References field, and no copyrighted material is used without permission. [source: `judging and awards guide.pdf` Eligibility]
20. **Tick the Terms-and-Conditions / Privacy-Policy agreement.** [source: `judging and awards guide.pdf` Eligibility]
21. **Describe SI (Super Intelligence) use in the submission:** every team must include, in its project submission, a description of how SI tools (LLMs, chat assistants, image/video/code generators) were used — even if minimal or none. [source: `FAQs.pdf` p.12]
22. **References field** must list every dataset, library, texture, font, AI/SI tool, image, sound, and text source (with license). [source: `judging and awards guide.pdf` Eligibility, implied by the originality statement]
23. **Public, no-password URL** for the running project + public repository link + public demo video link (implicit — the submission page requests links; confirm field names at Stage 11). [source: `judging and awards guide.pdf` Eligibility, referenced to the Project Submission Guide]

## C. Judging criteria (the project is scored on these 1–5 scales)

24. **Impact** — reach, inspiration, quality & quantity of overall effect. [source: `judging and awards guide.pdf` Judging Criteria → Impact]
25. **Creativity** — originality, novel concept, inventive execution. [source: `judging and awards guide.pdf` Judging Criteria → Creativity]
26. **Validity** — grounded in scientific principles; technically sound; feasible; usable; user-friendly; refined. [source: `judging and awards guide.pdf` Judging Criteria → Validity]
27. **Relevance** — thorough, direct engagement with the chosen challenge; **meaningful NASA data integration as a core component, not superficial**. [source: `judging and awards guide.pdf` Judging Criteria → Relevance]
28. **Presentation** — clear, well-structured, compelling storytelling in both the demo and the full project. [source: `judging and awards guide.pdf` Judging Criteria → Presentation]

## D. Ten Global Awards (project may be considered for one)

29. Best Use of Science. [source: `judging and awards guide.pdf` Phase 3]
30. Best Use of Data. [source: `judging and awards guide.pdf` Phase 3]
31. Best Use of Technology. [source: `judging and awards guide.pdf` Phase 3]
32. Galactic Impact. [source: `judging and awards guide.pdf` Phase 3]
33. Best Mission Concept. [source: `judging and awards guide.pdf` Phase 3]
34. Most Inspirational. [source: `judging and awards guide.pdf` Phase 3]
35. Best Storytelling. [source: `judging and awards guide.pdf` Phase 3]
36. Global Connection. [source: `judging and awards guide.pdf` Phase 3]
37. Art & Technology. [source: `judging and awards guide.pdf` Phase 3]
38. Local Impact. [source: `judging and awards guide.pdf` Phase 3]

## E. Conduct & eligibility caveats

39. **Space Apps Values** — professional decorum; no bullying, discrimination, or harassment on any basis. [source: `space apps connect.pdf` Introduction]
40. **China-funding restriction review:** teams with Chinese-government, Chinese-owned-entity, Hong Kong, or Macau governmental affiliation are reviewed before advancing to Global Judging. [source: `judging and awards guide.pdf` Eligibility]
41. **Under-18 participants** need a parent/guardian for registration; must not upload a photo of themselves or use likenesses of others under 18 in the project demo or submission; some Local Events add further restrictions. [source: `FAQs.pdf` p.2]

---

**How the UI will use this file.** The Crosswalk screen (SPEC §2 item 10) reads this document and renders a one-page table:  row number → requirement → the screen/route that answers it → implementation status. Rows A1–A5 and A10–A12 map to the Trend Lab and Signal Atlas; A6 maps to the Methodology drawer; A8–A9 map to Story Mode; B13–B23 are submission-page checkpoints (status tracked, not rendered in-app); C24–C28 are internal self-review columns used in the Decision Brief; D29–D38 are reference-only; E39–E41 are policy footer links.
