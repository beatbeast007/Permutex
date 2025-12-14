"""
Mutation utilities for Permutex.
UPGRADE: Added 'generate_all_casings' for exhaustive toggle permutations.
"""

from typing import Set, List

def leet_transform(s: str) -> str:
    """Basic leetspeak transformation."""
    table = str.maketrans({
        'a': '@', 'A': '@',
        'o': '0', 'O': '0',
        'i': '1', 'I': '1',
        's': '$', 'S': '$',
        'e': '3', 'E': '3',
        't': '7', 'T': '7'
    })
    return s.translate(table)

def generate_all_casings(text: str, max_variants: int = 50) -> Set[str]:
    """
    Generates exhaustive casing: abhi, Abhi, aBhi, abHi, AbHi...
    Uses bit-shifting.
    Safety cap 'max_variants' prevents crashing on long strings.
    """
    n = len(text)
    # Safety: If string is too long (e.g., >8 chars), 2^8=256 is okay, 
    # but 2^12=4096 is dangerous for a single token.
    if n > 8: 
        # Fallback to simple variations for long tokens
        return {text, text.lower(), text.upper(), text.title(), text.swapcase()}
    
    results = set()
    # Iterate from 0 to 2^n
    for i in range(1 << n):
        chars = []
        for j in range(n):
            # If j-th bit is set, Uppercase; else Lowercase
            if (i >> j) & 1:
                chars.append(text[j].upper())
            else:
                chars.append(text[j].lower())
        
        results.add("".join(chars))
        if len(results) >= max_variants:
            break
            
    return results

def generate_mutations(
    token: str,
    enable_leet: bool = False,
    enable_reverse: bool = False,
    enable_case_variants: bool = False,
    append_years=None,
    deep_casing: bool = False  # <--- NEW FLAG
):
    """Yield controlled mutations of a single token."""
    
    if append_years is None:
        append_years = []

    seen = set()

    def yield_once(x):
        if x not in seen:
            seen.add(x)
            yield x

    # 1. Exhaustive Casing (The Game Changer)
    if deep_casing:
        # This generates 'Abhi', 'aBhi', 'abHi'...
        all_cases = generate_all_casings(token)
        for c in all_cases:
            for v in yield_once(c):
                yield v
    else:
        # Standard casing
        for v in yield_once(token): yield v
        if enable_case_variants:
            for v in [token.lower(), token.upper(), token.title()]:
                for x in yield_once(v): yield x

    # 2. Leet Speak
    if enable_leet:
        # We apply leet to the base token (and maybe lowercase)
        leet = leet_transform(token)
        for v in yield_once(leet):
            yield v

    # 3. Reversed
    if enable_reverse:
        rev = token[::-1]
        for v in yield_once(rev):
            yield v

    # 4. Years
    for y in append_years:
        base = token + y
        for v in yield_once(base):
            yield v
