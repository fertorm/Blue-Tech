---
description: Full security audit — OWASP Top 10 + secrets scan. Delegates to the security-reviewer agent.
---

Run a comprehensive security audit of the current codebase:

1. Delegate to the `security-reviewer` agent with these instructions:

   a. **Secrets scan** — Search for hardcoded API keys, tokens, and passwords in all non-test files. Look for patterns: `AIzaSy`, `sk-`, `AKIA`, `ghp_`, `xoxb-`, `password =`, `secret =`.

   b. **OWASP Top 10 audit** — Review code for the 10 most critical web application security risks: injection, broken auth, sensitive data exposure, XXE, broken access control, security misconfiguration, XSS, insecure deserialization, vulnerable components, insufficient logging.

   c. **Dependency audit** — Run `npm audit --audit-level=high` and report all HIGH and CRITICAL vulnerabilities with remediation commands.

   d. **Environment check** — Verify `.gitignore` covers all `.env*`, `*.backup`, `*.key`, `secrets.*` patterns. Flag any secrets files tracked by git.

2. Generate a severity-ranked report:
   - CRITICAL: Block all work until fixed
   - HIGH: Fix before next release
   - MEDIUM: Fix within 2 weeks
   - LOW: Backlog item

3. For each finding provide:
   - File path and line number
   - Description of the vulnerability
   - Concrete remediation step with example code

4. End with a pass/fail summary and list of immediate action items.
