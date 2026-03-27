from dataclasses import dataclass
from typing import Optional, Literal, List


@dataclass
class ParsedSection:
    section_title: Optional[str]
    text: str
    content_type: Literal["text", "table"]
    page_number: Optional[int] = None
    heading_level: Optional[int] = None


class DocumentParser:
    def parse_plain_text(self, title: str, text: str) -> List[ParsedSection]:
        sections: List[ParsedSection] = []
        blocks = [b.strip() for b in text.split("\n\n") if b.strip()]

        current_title = None
        current_body = []

        for block in blocks:
            lines = [line.strip() for line in block.splitlines() if line.strip()]

            if len(lines) == 1 and len(lines[0]) < 80 and not lines[0].endswith("."):
                if current_body:
                    sections.append(
                        ParsedSection(
                            section_title=current_title or title,
                            text="\n".join(current_body).strip(),
                            content_type="text",
                        )
                    )
                    current_body = []
                current_title = lines[0]
            else:
                current_body.append(block)

        if current_body:
            sections.append(
                ParsedSection(
                    section_title=current_title or title,
                    text="\n\n".join(current_body).strip(),
                    content_type="text",
                )
            )

        if not sections:
            sections.append(
                ParsedSection(
                    section_title=title,
                    text=text.strip(),
                    content_type="text",
                )
            )

        return sections