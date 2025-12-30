# AI Agent Automation Spec

## Purpose

This repository is designed to be managed with heavy AI assistance (GitHub Copilot, ChatGPT, Claude, etc.). The primary "superpower" is:

> **Issue triage + code review + minimal-touch PR preparation.**

## Agent Responsibilities

1. **Issue triage**
   - Read new issues.
   - Tag them with `bug`, `enhancement`, or `question` based on content.
   - Suggest missing details as a comment using the issue template structure.

2. **Code review helper**
   - For each pull request:
     - Summarize changes in 3–5 bullet points.
     - Highlight risky areas (auth, database, file IO, external API calls).
     - Suggest at least one test case if tests are missing.

3. **PR preparation**
   - When changes are small and obvious (typo fixes, small refactors), the agent may:
     - Propose a branch name: `chore/<short-description>`
     - Generate a commit message in the format: `type(scope): summary`
       - Example: `fix(auth): prevent null token crash`

## Files AI Should Read First

1. `README.md`
2. `AGENT_AUTOMATION.md` (this file)
3. `CHANGELOG.md`
4. `.github/workflows/ci.yml`
5. Any `docs/` files if present.

## Rules of Engagement

- Never commit secrets, tokens, or API keys.
- Prefer small, focused pull requests.
- Always ensure CI is green before marking a PR as "ready to merge".
- When in doubt, add a comment instead of changing behavior silently.

## Future Ideas

- Add labeler workflow to automatically label issues based on keywords.
- Add release workflow to bump version and update `CHANGELOG.md`.
- Integrate with external tools (e.g., deployment, monitoring).
