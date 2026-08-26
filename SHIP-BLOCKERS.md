# Ship blockers

**Do not publish this repository, or announce it, while anything below is open.**
Each entry blocks release on its own.

## Open

*(none)*

Add an entry here the moment something is deferred. A blocker that lives only in
a conversation is a blocker that ships.

---

## Resolved

### 1. `board-request` had no transport — RESOLVED 2026-08-26

**Decision:** the GitHub CLI when it is available and authenticated, a
pre-filled issue URL otherwise, local-only if the user declines. Implemented in
`skills/board-request/SKILL.md` §4.

Why this one: no credentials handled, no service to run, nothing leaves the
machine without the user seeing the exact text and saying yes, and the issue is
filed under their own identity. It keeps the README's privacy claim true — the
only thing that can ever leave the machine is a board report they explicitly
submit, and it carries no part of their profile.

Checks that were required, and are met:

- [x] A transport is chosen and implemented
- [x] The privacy section of `README.md` still tells the truth afterwards
- [x] Nothing leaves the machine without a per-request confirmation
- [x] The skill never says "submitted" for something that was only saved
- [x] The warning block at the top of the skill is deleted

One thing the decision added: the report carries **one example ad URL**, which
reveals which job the user was looking at. The skill now discloses that before
asking, and offers to strip it.
