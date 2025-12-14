"""
Permutex Core Combinator Engine

Generates password candidates by combining tokens across selected
categories using different logic modes.
"""

from typing import Dict, List, Tuple

DEFAULT_SEPARATORS = ["", "_", ".", "@", "-", "!"]

def combine_tokens(
    list_a: List[str],
    list_b: List[str],
    separators: List[str] = DEFAULT_SEPARATORS,
    allow_reverse: bool = False
) -> List[str]:
    """
    Combine elements from two lists using separators.

    Args:
        list_a: First list of strings
        list_b: Second list of strings
        separators: Separators to use between tokens
        allow_reverse: Include reversed pair combinations as well

    Returns:
        List of combined strings
    """
    results = set()

    for a in list_a:
        for b in list_b:
            for sep in separators:
                if a and b:
                    results.add(f"{a}{sep}{b}")
                    if allow_reverse:
                        results.add(f"{b}{sep}{a}")

    return list(results)


def generate_pairs_from_categories(
    selected: Dict[str, List[str]],
    manual_pairs: List[Tuple[str, str]] = None,
    allow_self_pairs: bool = False,
    allow_reverse: bool = False
) -> List[str]:
    """
    Create pairwise password combinations from selected input categories.

    Args:
        selected: Dictionary of category_name -> list of words
        manual_pairs: If given, restrict to (catA, catB) pairs only
        allow_self_pairs: Whether to allow categoryA x categoryA
        allow_reverse: Whether to include reverse combinations

    Returns:
        List of pairwise combined password candidates
    """
    pairs = []
    categories = list(selected.keys())

    # Use only manual pairs if provided
    pair_set = manual_pairs if manual_pairs else [
        (cat_a, cat_b)
        for cat_a in categories
        for cat_b in categories
        if allow_self_pairs or cat_a != cat_b
    ]

    for cat_a, cat_b in pair_set:
        list_a = selected.get(cat_a, [])
        list_b = selected.get(cat_b, [])
        combined = combine_tokens(list_a, list_b, allow_reverse=allow_reverse)
        pairs.extend(combined)

    return pairs
