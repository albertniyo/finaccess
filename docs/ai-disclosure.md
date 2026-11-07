# AI disclosure

The NISR 2026 Big Data Hackathon rules require participants to disclose AI assistance. This is how
we used it.

## Brainstorming and understanding the challenge

We used AI assistants to:

- unpack the Track 2 brief and the judging criteria, and turn them into a concrete policy question;
- brainstorm candidate features and narrow them to three (explore, prioritise, brief);
- understand the EICV7 and FinScope survey designs, their definitions and why they cannot be linked
  at household level;
- stress-test the method like weighting, uncertainty, baselines and the wording of limitations.

## Building

We also used an AI coding assistant (Cursor) while writing the code for completion, tests and documentation. The
team reviewed, ran and tested all of it, and is responsible for every design choice and claim in the
submission.

## What AI did not do

- **Produce any statistic.** EICV7 values are read from NISR's Excel tables by
  `scripts/build_indicators.py`. Figures available only in PDFs were transcribed into `data/manual/`
  and are re-checked against the PDF text layer by `scripts/verify_transcriptions.py`.
- **Decide what the numbers mean.** Each displayed figure is traced to its table or figure, and the
  build fails unless 50 checks against the published reports pass.

## Log

| Date | Tool | Use |
| --- | --- | --- |
| 2026-10-27 and 28 | ChatGPT | Reading the challenge and rules, brainstorming the product, data inventory and plan |
| 2026-10-29 | Cursor | Project scaffold and Setup (FastAPI backend, Vite plus React frontend) |
| 2026-11-07 | Cursor | Data pipeline and checks, scoring and API, interface, deployment configuration, documentation |
