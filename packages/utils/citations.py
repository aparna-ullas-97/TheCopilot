import re


def normalize_inline_citations(text: str) -> str:
    """
    Cleans common citation formatting issues like:
    - extra spaces before citations
    - duplicate spaces
    - malformed [ 1 ]
    """
    if not text:
        return text

    text = re.sub(r"\[\s*(A?\d+)\s*\]", r"[\1]", text)
    text = re.sub(r"\s+\[", " [", text)
    text = re.sub(r"([.,;:])\s+\[", r"\1 [", text)
    text = re.sub(r"\s{2,}", " ", text)

    return text.strip()