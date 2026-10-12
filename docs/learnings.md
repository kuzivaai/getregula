# Learnings

Rules for this file (do not edit this header from a task; propose changes through the scaffolding repo):

1. Append-only. New entries go at the end; existing entries are never rewritten or deleted. A superseded entry gets a new dated entry that says it is superseded and why.
2. Dated. Every entry starts with the ISO date it was recorded.
3. Demonstrated only. An entry records something observed in a session: a command that failed and why, a check that caught a defect, a behaviour of this repo's tooling. Each entry carries an evidence reference: a commit hash, a file path with line, a test name, a CI run URL or a pasted command with its output.
4. Written on explicit retro request only (the `/retro` command in Claude Code, or the same wording in Codex). Never written automatically by a hook, a scheduled job or auto memory.
5. Anything not verified in the session is labelled Asserted, in the entry text, and stays Asserted until a later entry demonstrates it.
6. This file never contains secrets, personal identifiers, expanded home paths or hostnames.
7. Promotion: a learning that keeps recurring can be promoted to one line under "Known failure modes" in this repo's AGENTS.md, by a human, with a reference back to the entry here.

Entry format:

    ## YYYY-MM-DD: <one-line title>
    Status: Demonstrated | Asserted
    Evidence: <commit, path:line, test name, run URL, or pasted output>
    What happened: <two to five lines>
    What to do differently: <one to three lines>

---

<!-- seeded 2026-08-26 by the scaffolding overhaul run; no entries yet -->
