"""Embedding text generation for pattern JSON."""


def pattern_to_embedding_text(pattern: dict) -> str:
    lines = []

    # Layout type
    lines.append(f"{pattern['layout_type']} residential layout.")

    # Adjacency
    for room, neighbors in pattern["adjacency"].items():
        for nb in neighbors:
            lines.append(f"{room} is adjacent to {nb}.")

    # Area importance (top 2 only)
    area = pattern.get("area_weight", {})
    if area:
        ordered = sorted(area.items(), key=lambda x: x[1], reverse=True)
        if len(ordered) >= 1:
            lines.append(f"{ordered[0][0]} is the largest space.")
        if len(ordered) >= 2:
            lines.append(f"{ordered[1][0]} is the second largest space.")

    return " ".join(lines)

