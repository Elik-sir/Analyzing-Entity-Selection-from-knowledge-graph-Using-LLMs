---
name: latex-paper-builder
description: Assemble and validate an authorized research manuscript with the verified official WWW 2027 ACM LaTeX template, bibliography, figures, anonymity, and page limits.
---

# LaTeX paper builder

Read root `AGENTS.md` and [the artifact contract](../../../paper/research_notes/ARTIFACT_CONTRACT.md). Formatting does not authorize new scientific text or repair unsupported claims.

## Inputs

Approved-scope section files, `workflow_state.json`, claim map, verified bibliography and figures; `paper/research_notes/conference_requirements.md`; official template source and provenance under `paper/template/` when downloaded.

## Procedure

1. Recheck the official Research Track call and ACM template before final submission preparation. Record date/URLs and separate long/short and review/camera-ready rules. Never inherit another year's limits or sample conference metadata.
2. Follow the verified WWW directive `\documentclass[sigconf,anonymous,review]{acmart}` for review unless the official call changes. Use ACM's official class and `ACM-Reference-Format`. Generic single-column template advice does not override the WWW call. Do not modify class typography, margins or spacing to fit pages.
3. If source retrieval fails, record the failed attempt and preserve verified official links; do not call a home-made class an official template. Inspect the actual downloaded version/hash rather than assuming the website's version matches the bundle. Keep template examples separate from scientific content.
4. Check the writing gate before creating a full manuscript. A template readiness check may precede it, but must contain no generated paper claims. For a new local project use the available LaTeX-project creation tool if present, otherwise create a dedicated `paper/manuscript/` directory. Respect an existing project's main file.
5. Assemble only supported sections. Remove sample authors, affiliations, DOI/ISBN, rights statement and sample results; do not invent replacement bibliographic metadata. Use the appropriate ACM review defaults. Keep figures, references and section paths local and deterministic.
6. Compile using the available app compiler or an installed TeX toolchain. Avoid shell escape and automatic execution of unknown external commands. Save command/tool, engine/version if available, source hash, exit status and diagnostics. No compiler means “not compiled,” not success.
7. Check missing citations/references, overfull content, fonts, figure readability, page count, main-text boundary, PDF metadata and anonymity. Inspect rendered pages. For long papers verify the first 8 pages are self-contained and total <=12; short papers <=4 total, subject to a fresh rules check.

## Outputs

`paper/manuscript/` sources and bibliography; compiled PDF only after successful compilation; `paper/research_notes/build_report.md` with evidence of build and visual inspection, page/anonymity checks and unresolved warnings. Update template provenance when the official source changes.

## Completion check

Report compilation, visual QA, scientific verification, and venue compliance separately. A successful build is not permission to submit or evidence that the paper is scientifically ready.
