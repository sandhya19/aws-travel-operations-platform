# Prompt source directory

`releases.json` is the source-controlled prompt release registry. A release names its template,
owner, model assumption, evaluation dataset and minimum gates, and explicit rollback version.
Exactly one release for a prompt may be `ACTIVE`; prompt templates are reviewed source artifacts.
