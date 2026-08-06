"""Build bounded, cited context for grounded model requests."""

from travel_operations.rag.models import RetrievedChunk


class ContextBuilder:
    def build(self, chunks: list[RetrievedChunk], maximum_characters: int = 12000) -> str:
        sections: list[str] = []
        used = 0
        for chunk in chunks:
            section = f"Source {chunk.citation}\n{chunk.content}"
            if used + len(section) > maximum_characters:
                break
            sections.append(section)
            used += len(section)
        return "\n\n".join(sections)
