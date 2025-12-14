"""
Estimation Helpers for Permutex

Provides:
- estimate_combinations(): Estimate total number of password combinations
- estimate_size_bytes(): Predict output file size based on average password length
"""

from typing import Dict, List, Tuple

# Assumes UTF-8 encoding; 1 byte per character + 1 for newline
ESTIMATED_BYTES_PER_CHAR = 1

def estimate_combinations(
    selected_categories: Dict[str, List[str]],
    allow_self_combine: bool,
    max_depth: int = 2,
    manual_pairs: List[Tuple[str, str]] = None
) -> int:
    """
    Estimate how many password combinations will be generated.

    Args:
        selected_categories: Dict of category name to list of values
        allow_self_combine: If True, allows pairing same category with itself
        max_depth: Max pair depth to consider (1 = single token use, 2 = pairs)
        manual_pairs: If provided, only these (cat_a, cat_b) pairs are used

    Returns:
        Estimated combination count (int)
    """
    if manual_pairs:
        count = 0
        for cat_a, cat_b in manual_pairs:
            a_count = len(selected_categories.get(cat_a, []))
            b_count = len(selected_categories.get(cat_b, []))
            count += a_count * b_count
        return count

    categories = list(selected_categories.keys())

    if max_depth == 1:
        return sum(len(selected_categories[c]) for c in categories)

    # Full pairwise combination (default mode)
    total = 0
    for cat_a in categories:
        for cat_b in categories:
            if not allow_self_combine and cat_a == cat_b:
                continue
            a_len = len(selected_categories[cat_a])
            b_len = len(selected_categories[cat_b])
            total += a_len * b_len
    return total

def estimate_size_bytes(num_combinations: int, avg_length: float) -> int:
    """
    Estimate how big the wordlist file will be in bytes.

    Args:
        num_combinations: Number of passwords
        avg_length: Average characters per password

    Returns:
        Estimated file size in bytes
    """
    return int(num_combinations * (avg_length * ESTIMATED_BYTES_PER_CHAR + 1))  # +1 for newline
