---
description: Architecture review — folder structure, module dependencies, coupling analysis. Delegates to the architect agent.
---

Run a structural architecture review of the current project:

1. Delegate to the `architect` agent with these instructions:

   a. **Folder structure analysis** — Review top-level directories and assess whether the organization matches the project's domain boundaries. Flag folders with unclear responsibilities or overlapping concerns.

   b. **Module dependency graph** — Trace imports/requires across the codebase. Identify:
      - Circular dependencies (A imports B imports A)
      - God modules (one file imported by > 10 others)
      - Tight coupling between layers that should be independent (e.g., UI code importing DB logic directly)

   c. **Cohesion check** — For each module, verify that everything inside it belongs together. Flag modules that do too many unrelated things.

   d. **Naming and convention consistency** — Check that file naming, export patterns, and directory conventions are consistent throughout the project.

   e. **Scalability assessment** — Identify parts of the architecture that will become bottlenecks or maintenance burdens as the project grows.

2. Generate a prioritized recommendation report:

   ```
   ARCHITECTURE REVIEW
   ===================
   Project: <name>

   STRUCTURE ISSUES
   ----------------
   [HIGH]   scripts/ contains both hooks and CI utilities — split into scripts/hooks/ and scripts/ci/
   [MEDIUM] commands/ has 30+ files without subcategories — consider grouping by domain

   DEPENDENCY ISSUES
   -----------------
   [HIGH]   Circular: moduleA → moduleB → moduleA
   [MEDIUM] God module: utils.js imported by 15 files — split into focused utilities

   RECOMMENDATIONS (priority order)
   ---------------------------------
   1. ...
   2. ...
   ```

3. For each HIGH or MEDIUM issue, provide a concrete refactoring plan with:
   - Current state (what exists now)
   - Target state (what it should look like)
   - Migration steps (how to get there without breaking things)
