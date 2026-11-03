# Workflow

"Next step" in `docs/Plan.md` names the current issue. Start new work there. Read that issue's newest handoff comment first: it overrides "Next step". Follow these stages in order. Each stage names the `mattpocock-skills` skill to load.

1. **Grill**, when design decisions are open: `grill-with-docs`. Commit any docs it changes to the issue's branch. Done when no decision is left assumed, and `GLOSSARY.md`, ADRs and issues record the outcome.
2. **Hand off to implementation**, after a grill: post the handoff, naming the branch, and update "Next step" on that branch. Implementation continues on the same branch, so one PR carries both.
3. **Implement** the issue test-first: `tdd`. Add `codebase-design` for module boundaries and `diagnosing-bugs` for hard bugs. Done when the issue's "Done when" list is met.
4. **Open the PR:** `pr`.
5. **Review:** `code-review`. Fix or report every finding.
6. **Hand off to the next issue**, as the reviewer's last step, before approving: choose the next issue from `docs/Plan.md`, post its handoff, and update "Next step" on the PR's branch. If the next issue has open design decisions, make "Next step" a grilling session on that issue.

**Handoffs:** post each one as a comment on the issue it hands off to. Cover what's decided, what to read first, gotchas, how to verify, and suggested skills. Link to issues, ADRs and docs rather than copying them, and leave out secrets.

When the issue already says everything needed, skip the handoff and write "Handoff: none needed" in "Next step". After a grill, also post that line on the issue with the branch name, or "no branch" if nothing was committed, so the next agent knows the grill finished.

**Work with no issue:** every committed change belongs to an issue, whatever its size. Before the first edit, check the open issues. If none covers the change, create one, add it to the project board and give the maintainer the link. Use the usual format: what and why, optional `## Changes`, `## Done when`, plus any context from the conversation that prompted it. Then enter at stage 1 if design decisions are open, otherwise at Implement.

- **Requested by the maintainer:** that request is the go-ahead to start. "Next step" stays as it is unless the change makes it wrong.
- **Found during other work:** file the issue and keep it out of the current PR, unless it blocks that work. Add the issue to `docs/Plan.md` at its place in the build order, on the current branch.

**The maintainer decides** when to start an issue, push, open a PR and merge. Creating an issue doesn't start it.

# Git conventions

**Commits:** include the number of the issue the commit belongs to, for example `#7 add Dead Letter state`.

**Branches:** name them `<developer-first-name-or-slug>/<branch-name>`, for example `julian/fakeredis-adapter`.
