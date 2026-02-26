---
description: Dependency audit — vulnerabilities, outdated packages, license issues. Delegates to the dependency-analyzer agent.
---

Run a full dependency health check on the current project:

1. Delegate to the `dependency-analyzer` agent with these instructions:

   a. **Security audit** — Run `npm audit --audit-level=high` and collect all findings. For each vulnerability provide the CVE, severity, affected package, and exact fix command.

   b. **Freshness report** — Run `npm outdated` and categorize results by major/minor/patch lag. Flag any packages more than one major version behind.

   c. **Unused dependencies** — Check `package.json` dependencies against actual imports in the codebase. Flag packages listed as dependencies that are never imported.

   d. **License check** — Identify any packages with GPL, AGPL, or unknown licenses that may conflict with the project's license.

   e. **Dependency count** — Report total number of direct dependencies and total (including transitive). Flag projects with > 500 total packages as at risk of supply chain issues.

2. Output a ranked action list:

   ```
   DEPENDENCY REPORT
   =================
   Direct dependencies:  XX
   Total (transitive):   XXX

   CRITICAL — Fix immediately
   --------------------------
   npm install package@X.X.X   # CVE-XXXX-XXXX

   HIGH — Fix before release
   -------------------------
   npm install package@latest  # 2 major versions behind

   MEDIUM — Schedule update
   ------------------------
   ...

   CLEANUP
   -------
   npm uninstall unused-package  # never imported
   ```

3. After generating the report, ask whether to apply the CRITICAL and HIGH fixes automatically.
