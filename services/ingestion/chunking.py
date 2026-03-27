from typing import List
from services.ingestion.document_parser import ParsedSection


class TextChunker:
    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_sections(self, sections: List[ParsedSection]) -> List[dict]:
        all_chunks: List[dict] = []

        for section in sections:
            text = (section.text or "").strip()
            if not text:
                continue

            prefix = ""
            if section.section_title:
                prefix += f"Section: {section.section_title}\n"
            if section.content_type:
                prefix += f"Content Type: {section.content_type}\n\n"

            body = prefix + text

            if len(body) <= self.chunk_size:
                all_chunks.append(
                    {
                        "section_title": section.section_title,
                        "content_type": section.content_type,
                        "page_number": section.page_number,
                        "heading_level": section.heading_level,
                        "chunk_text": body,
                    }
                )
                continue

            start = 0
            step = max(1, self.chunk_size - self.chunk_overlap)

            while start < len(body):
                part = body[start:start + self.chunk_size]
                all_chunks.append(
                    {
                        "section_title": section.section_title,
                        "content_type": section.content_type,
                        "page_number": section.page_number,
                        "heading_level": section.heading_level,
                        "chunk_text": part,
                    }
                )
                start += step

        return all_chunks