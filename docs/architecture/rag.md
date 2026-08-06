# Retrieval-Augmented Generation

The RAG foundation retrieves approved knowledge chunks from CockroachDB using vector
similarity ranking, then builds a bounded context with source citations. The grounded
prompt template requires citation notation, and a deterministic check rejects answers
that cite no retrieved chunk or cite unknown sources.

Embeddings are supplied by the caller; model invocation and agents are intentionally
out of scope for this milestone.
