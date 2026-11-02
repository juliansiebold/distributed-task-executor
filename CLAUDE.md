# Workflow

"Next step" in `docs/Plan.md` names the current issue and its handoff. Start new work there, and follow these stages in order. Each stage names the `mattpocock-skills` skill to load.

1. **Grill**, when design decisions are open: `grill-with-docs`. Done when no decision is left assumed, and `GLOSSARY.md`, ADRs and issues record the outcome.
2. **Implement** the issue test-first: `tdd`. Add `codebase-design` for module boundaries and `diagnosing-bugs` for hard bugs. Done when the issue's "Done when" list is met.
3. **Open the PR:** `pr`.
4. **Review:** `code-review`. Fix or report every finding.
5. **Hand off** as the reviewer's last step, before approving: choose the next issue from `docs/Plan.md`, post its handoff, and update "Next step" on the PR's branch. If the next issue has open design decisions, make "Next step" a grilling session on that issue.

**Handoffs:** write them with `handoff`, but post each one as a comment on the issue it hands off to. This replaces that skill's temp-directory location. When the issue already says everything needed, skip the handoff and write "Handoff: none needed" in "Next step".

**The maintainer decides** when to start an issue, push, open a PR and merge.

# Git conventions

**Commits:** include the number of the issue the commit belongs to, for example `#7 add Dead Letter state`.

**Branches:** name them `<developer-first-name-or-slug>/<branch-name>`, for example `julian/fakeredis-adapter`.
