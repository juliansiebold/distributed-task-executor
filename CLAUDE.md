# Workflow

"Next step" in `docs/Plan.md` names the current issue. Start new work there. If that issue has a post-grill comment, it overrides "Next step": switch to the branch it names and continue from there. Follow these stages in order, loading the `mattpocock-skills` skills each one names.

1. **Grill**, when design decisions are open: `grilling` and `domain-modeling`. Commit any docs it changes to the issue's branch. Done when no decision is left assumed, and `GLOSSARY.md`, ADRs and issues record the outcome.
2. **Hand off to implementation**, after a grill: if the grill committed anything, update "Next step" on the issue's branch to say Implement, and push the branch. Then post the post-grill comment, naming the branch or "no branch". If nothing was committed, leave "Next step" alone. Implementation continues on any branch named, so one PR carries both. Done when the comment is on the issue and any branch it names is pushed.
3. **Implement** the issue test-first: `tdd`. Check **PR size** first. Add `codebase-design` for module boundaries and `diagnosing-bugs` for hard bugs. Done when the issue's "Done when" list is met.
4. **Open the PR:** `pr`.
5. **Review:** `code-review`. Fix or report every finding.
6. **Hand off to the next issue**, as the reviewer's last step before approving, when the PR's issue is the one "Next step" names: choose the next issue from `docs/Plan.md`, post its handoff, and update "Next step" on the PR's branch. If the next issue has open design decisions, make "Next step" a grilling session on that issue.

**Handoffs:** post each one as a comment on the issue it hands off to. Cover what's decided, what to read first, gotchas, how to verify, and suggested skills. Link to issues, ADRs and docs rather than copying them, and leave out secrets.

When the issue already says everything needed, skip the handoff. After a review, write "Handoff: none needed" in "Next step". After a grill, post that line as the post-grill comment, so the next agent knows the grill finished.

**PR size:** count the added and deleted lines from `git diff --numstat -M main...HEAD -- . ':!uv.lock'`. This leaves out generated files and files moved without changes. Tests and docs count.

- **Up to 300:** the target.
- **300 to 500:** fine.
- **500 to 800:** big. The PR body says why it couldn't be split.
- **Over 800:** never open it. Split it first, unless the maintainer approves an exception for that PR.

Before implementing, estimate the size from the issue. If it's likely to go over 500, propose a split to the maintainer before writing code. Split into separate issues, each with its own "Done when" and PR, and add them to `docs/Plan.md` in build order. The PR body states the count, and the reviewer flags any PR over 500 that doesn't say why.

**Work with no issue:** every committed change belongs to an issue, whatever its size. Before the first edit, check the open issues. If none covers the change, create one without asking, add it to the project board and give the maintainer the link. Use this format: what and why, optional `## Changes`, `## Done when`, plus any context from the conversation that prompted it.

- **Requested by the maintainer:** that request is the go-ahead to start. Enter at Grill if design decisions are open, otherwise at Implement. "Next step" stays as it is unless the change makes it wrong.
- **Found during other work:** ask the maintainer whether it blocks the current work and where it goes in the build order. Add it to `docs/Plan.md` there, in its own commit on the current branch with the new issue's number. Unless it blocks, the change itself stays out of the current PR.

**The maintainer decides** when to start an issue, open a PR and merge. Creating an issue leaves the start to them.

# Git conventions

**Commits:** include the number of the issue the commit belongs to, for example `#7 add Dead Letter state`. Commit and push finished work to the issue's branch without asking. Force-pushes and pushes to `main` need the maintainer's go-ahead.

**Branches:** name them `<developer-first-name-or-slug>/<branch-name>`, for example `julian/fakeredis-adapter`.
