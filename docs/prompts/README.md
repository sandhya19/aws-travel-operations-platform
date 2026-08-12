# Prompt management

Prompts are source code and are stored as versioned files in `prompts/`. The
`prompts/releases.json` registry identifies each release's owner, model assumption, evaluation
dataset and required groundedness/citation gates, status, and rollback version. Release selection
fails unless exactly one version of a prompt is active; rollback resolves only a reviewed version of
the same prompt.

The active `rag_grounded_answer` release is `v2`, which strengthens the instruction boundary by
treating retrieved context as evidence rather than instructions. Its rollback target is `v1`.
Prompt changes require review and a linked evaluation result that meets both configured gates.
