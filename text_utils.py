def to_title_case(text: str) -> str:
    """Capitalize the first letter of every word; preserve line breaks."""
    if not text:
        return text
    lines = text.split("\n")
    return "\n".join(" ".join(word.capitalize() for word in line.split()) for line in lines)
