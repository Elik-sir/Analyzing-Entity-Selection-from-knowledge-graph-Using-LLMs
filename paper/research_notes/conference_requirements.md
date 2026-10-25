# WWW 2027 Research Track requirements

Verified 2026-10-25. Recheck official sources immediately before submission; a cached note is not a permanent policy guarantee.

## Conference-specific rules

Source: [Research Track call](https://www2027.thewebconf.org/research-track-papers/).

Use English, double columns and double-blind anonymization. The recommended review declaration is `\documentclass[sigconf,anonymous,review]{acmart}`. Long papers allow 8 self-contained main-text pages and at most 12 pages including references and optional appendix. Short papers allow 4 pages total. Explain Web relevance and track fit on the first page; using Web data/APIs alone is insufficient. Semantics and Knowledge is a candidate subject track, not a finalized choice. Author order is fixed at the abstract deadline; do not infer submission status from the existing draft.

Source: [Important dates](https://www2027.thewebconf.org/important-dates/).

Long abstract deadline: 2026-10-18; full paper: 2026-10-25, end of day AoE, corresponding to 2026-10-26 at 14:59 Europe/Moscow at minute precision. Short abstract: 2026-11-09; short paper: 2026-11-16. This task neither verifies an OpenReview registration nor submits anything.

## Official template and availability

[ACM's Official Overleaf template](https://www.overleaf.com/latex/templates/acm-conference-proceedings-primary-article-template/wbvnghjbzwpc) is marked Official and authored by ACM. The page advertises acmart 2.19. Its generic manuscript-mode advice does not override the WWW double-column directive. Do not copy sample authors, DOI/ISBN, conference or rights metadata into this study.

[CTAN acmart](https://ctan.org/pkg/acmart?lang=en) lists ACM copyright, maintainer Boris Veytsman and production version 2.20 dated 2026-08-16. The [maintainer README](https://github.com/borisveytsman/acmart/blob/primary/README) distinguishes production releases on CTAN/ACM from development sources on GitHub. These versions describe the websites, not a locally verified class.

Official download targets inspected:

- [ACM primary template ZIP](https://portalparts.acm.org/hippo/latex_templates/acmart-primary.zip), linked by [ACM ISSAC submission guidance](https://test.issac.hosting.acm.org/2026/submission_guidelines.php). Download reached an ACM Cloudflare access block.
- [CTAN production ZIP](https://mirrors.ctan.org/macros/latex/contrib/acmart.zip), linked by the package page. The request returned an HTML bot-check page rather than a ZIP; signature validation rejected it.

No official archive/class has been successfully cached. `paper/template/review-settings.tex` records only the verified WWW class options and bibliography style; it is not a replacement class or a full paper. `paper/template/provenance.json` records retrieval status. Obtain the actual official bundle through an accessible supported route before compiling; inspect its class version and record SHA-256. No PDF compilation or compliance certification is claimed in this installation.
