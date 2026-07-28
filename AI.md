# AI direction

The future platform will use specialized Travel Coordinator, Policy, Visa, Risk,
Insurance, and Approval agents rather than one general-purpose agent. Each agent will
have bounded tools, controlled memory, versioned prompts, and its own evaluation.

RAG sources will include travel and expense policies, insurance documents, visa
documents, travel advisories, and company rules. Retrieval will use semantic chunking,
Titan embeddings, metadata filtering, hybrid retrieval, and citations. Every answer
must cite its sources.

Prompts are source code: versioned, reviewable, evaluable, rollback-capable, and able
to support controlled A/B experiments. The evaluation framework will measure
groundedness, faithfulness, latency, hallucination, answer relevance, and citation
accuracy through golden datasets and regression tests.
