"""
Expander utilities for Permutex.
UPGRADE: Supports Deep Substring Recursion and Atomic Date Mixing.
"""

from typing import Dict, List, Iterable, Set, Tuple
import re
import itertools

# regex patterns
RE_DIGITS = re.compile(r"\d+")

def get_all_substrings(text: str, min_len: int = 2, max_len: int = None) -> Set[str]:
    """
    Generates ALL contiguous substrings.
    Input: "Abhi", min=2
    Output: {'Ab', 'bh', 'hi', 'Abh', 'bhi', 'Abhi'}
    """
    length = len(text)
    if max_len is None:
        max_len = length
    
    substrings = set()
    # Sliding window for all possible lengths
    for l in range(min_len, min(length, max_len) + 1):
        for i in range(length - l + 1):
            sub = text[i:i+l]
            substrings.add(sub)
    return substrings

def parse_dob_atomic(dob: str) -> dict:
    """
    Breaks a DOB into atomic Lego bricks.
    Input: "08122006" or "08-12-2006"
    Output: {'D': '08', 'M': '12', 'Y': '2006', 'y': '06'}
    """
    # Normalize separators
    clean = re.sub(r'[-/._\s]', '', dob)
    parts = {}
    
    if len(clean) == 8: # DDMMYYYY or MMDDYYYY (assuming DDMMYYYY primary)
        parts['D'] = clean[:2]
        parts['M'] = clean[2:4]
        parts['Y'] = clean[4:]
        parts['y'] = clean[6:]
    elif len(clean) == 6: # DDMMYY
        parts['D'] = clean[:2]
        parts['M'] = clean[2:4]
        parts['y'] = clean[4:]
        parts['Y'] = "20" + clean[4:] # Assumption
        
    return parts

def generate_atomic_date_mixes(dob_str: str) -> Set[str]:
    """
    Generates creative mixes of date parts.
    Input: "08122006"
    Output: {'0806', '1206', '2006', '0812', '08', '06', ...}
    """
    parts = parse_dob_atomic(dob_str)
    if not parts:
        return {dob_str}

    D, M, Y, y = parts.get('D'), parts.get('M'), parts.get('Y'), parts.get('y')
    mixes = set()
    
    # 1. atomic parts
    if D: mixes.add(D)
    if M: mixes.add(M)
    if Y: mixes.add(Y)
    if y: mixes.add(y)
    
    # 2. Creative Combos (The "Game Changer" part)
    if D and M:
        mixes.add(D + M) # 0812
        mixes.add(M + D) # 1208
    if D and y:
        mixes.add(D + y) # 0806 (Day + ShortYear)
        mixes.add(y + D) # 0608
    if M and y:
        mixes.add(M + y) # 1206
    if D and M and y:
        mixes.add(D + M + y) # 081206
    
    return mixes

def expand_token_deep(token: str, is_date: bool = False, min_sub_len: int = 2) -> Set[str]:
    """
    Master expansion function for a single token.
    """
    results = {token}
    
    # 1. Deep Substring Expansion (if not a pure date string)
    if not is_date and len(token) >= min_sub_len:
        subs = get_all_substrings(token, min_len=min_sub_len)
        results.update(subs)
        # Add lowercase/title versions of substrings automatically
        results.update({s.lower() for s in subs})
        results.update({s.title() for s in subs})

    # 2. Atomic Date Expansion
    # Trigger if explicitly flagged as date OR looks like date
    if is_date or (token[0].isdigit() and len(token) >= 6):
        date_mixes = generate_atomic_date_mixes(token)
        results.update(date_mixes)
        
    return results

def expand_categories(categories, **kwargs):
    # This remains largely the same, serving as the initial lightweight pass
    # The REAL expansion now happens in the worker (parallel.py) for the deep mode.
    # We return categories as-is or lightly processed here.
    return categories
