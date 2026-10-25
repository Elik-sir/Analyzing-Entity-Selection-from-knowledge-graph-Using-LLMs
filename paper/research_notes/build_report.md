# Manuscript build report

2026-10-25. English source: `paper/manuscript/main.tex`; compiled PDF: `paper/manuscript/main.pdf`.

Engine: official Tectonic 0.17.0, installed temporarily; untrusted mode disables unsafe features. Command, run from `paper/manuscript/`: `tectonic --untrusted --keep-logs --keep-intermediates main.tex`. Final diagnostics: `paper/manuscript/build-final.txt`. The app-compiler preflight did not return diagnostics before interruption; the reported successful build is the separate local Tectonic build.

Result: success, 9 pages total. Main text/Conclusion ends on page 6; references page 7; appendix pages 8–9. No overfull boxes or undefined citation keys remain in the final log. Remaining class warnings arise from listings' internal spacing; bibliography warnings concern deliberately absent/unverified optional fields and undated anonymous/documentation sources. No margins, font sizes or class typography were changed to evade page limits; the line-breaking emergency stretch repairs overflow.

Both scientific figures and all nine rendered manuscript pages were inspected during the writing pass. QA images are under `analyses/manuscript_assets/run-01/qa_final/`; the source-to-claim map remains a scope map whose final paragraph-level completion is pending. Numerical source rows are preserved in the asset manifest; this build is not independent scientific review or submission-readiness certification.

The Cypher appendix now uses the author's supplied query. Whitespace/comments are normalized for display; executable-token equivalence was checked. Global LIMIT 100, fixed sizes and the absence of full sampling-grid provenance are stated. No Neo4j execution, model call, public upload or submission occurred.

PDF SHA-256: `2e73903a987ca927884a339d7a520d277c3763cc4524aab0f3ba2da2686338f8`.
