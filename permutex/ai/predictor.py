"""
Permutex — Lightweight AI-Style Heuristic Estimator

This module provides password analysis utilities, including:
- entropy estimation
- human-likelihood scoring
- generation time benchmarking
- candidate ranking

Does not require external AI libraries.
"""

import re
import math
import time
from collections import Counter
from typing import List, Dict, Iterable, Tuple, Optional

# Constants
MAX_ENTROPY_PER_CHAR = 6.57  # ~log2(95 printable ASCII)
YEAR_RE = re.compile(r'\b(19|20)\d{2}\b')


def entropy_bits(text: str) -> float:
    """Calculate Shannon entropy in bits for a string."""
    if not text:
        return 0.0
    freq = Counter(text)
    length = len(text)
    entropy = -sum((cnt / length) * math.log2(cnt / length) for cnt in freq.values())
    return entropy * length


def entropy_per_char(text: str) -> float:
    return entropy_bits(text) / len(text) if text else 0.0


def charset_diversity_score(s: str) -> float:
    """Score diversity based on use of lowercase, uppercase, digits, and symbols."""
    classes = sum(bool(re.search(pattern, s)) for pattern in [r'[a-z]', r'[A-Z]', r'\d', r'\W'])
    return classes / 4.0


def contains_any_token(text: str, tokens: Iterable[str]) -> float:
    """Return fraction of tokens found in text (case-insensitive)."""
    tokens = [t.lower() for t in tokens if t]
    matches = sum(1 for t in tokens if t in text.lower())
    return min(1.0, matches / max(1, len(tokens)))


def has_year(s: str) -> bool:
    return bool(YEAR_RE.search(s))


def length_score(s: str, ideal_min: int = 6, ideal_max: int = 12) -> float:
    n = len(s)
    if ideal_min <= n <= ideal_max:
        return 1.0
    if n < ideal_min:
        return n / ideal_min
    return max(0.0, (ideal_max * 2 - n) / ideal_max)


def features_for_password(pwd: str, tokens: Iterable[str] = ()) -> Dict[str, float]:
    """Extract normalized feature set from password candidate."""
    return {
        "token_match": contains_any_token(pwd, tokens),
        "year": float(has_year(pwd)),
        "entropy_bits": entropy_bits(pwd),
        "entropy_per_char": entropy_per_char(pwd),
        "entropy_norm": min(1.0, entropy_per_char(pwd) / MAX_ENTROPY_PER_CHAR),
        "diversity": charset_diversity_score(pwd),
        "length_score": length_score(pwd),
        "has_separator": float(bool(re.search(r'[_@\-\!\$]', pwd))),
    }


def human_likelihood(pwd: str, tokens: Iterable[str] = ()) -> float:
    """Score how likely a password resembles something a human might choose."""
    f = features_for_password(pwd, tokens)
    weights = {
        "token_match": 0.45,
        "year": 0.15,
        "length_score": 0.12,
        "entropy": 0.18,
        "has_separator": 0.10
    }
    entropy_component = 1.0 - f["entropy_norm"]
    likelihood = (
        weights["token_match"] * f["token_match"] +
        weights["year"] * f["year"] +
        weights["length_score"] * f["length_score"] +
        weights["entropy"] * entropy_component +
        weights["has_separator"] * f["has_separator"]
    )
    return max(0.0, min(1.0, likelihood))


def score_password(pwd: str, tokens: Iterable[str] = ()) -> Dict[str, float]:
    f = features_for_password(pwd, tokens)
    return {
        "password": pwd,
        "entropy_bits": round(f["entropy_bits"], 3),
        "entropy_per_char": round(f["entropy_per_char"], 3),
        "human_likelihood": round(human_likelihood(pwd, tokens), 4),
        "features": f
    }


def rank_candidates(candidates: Iterable[str], tokens: Iterable[str] = (), top_k: Optional[int] = None) -> List[Dict]:
    """Sort password candidates by human-likelihood descending."""
    scored = [score_password(p, tokens) for p in candidates]
    scored.sort(key=lambda x: x["human_likelihood"], reverse=True)
    return scored[:top_k] if top_k else scored


def microbenchmark_throughput(sample_tokens: List[str], iterations: int = 5000) -> float:
    """
    Perform a small synthetic benchmark using concat operations.
    Returns candidates/sec on single core.
    """
    tokens = sample_tokens or ["alpha", "beta", "2024", "!"]
    t0 = time.time()
    for i in range(iterations):
        a, b = tokens[i % len(tokens)], tokens[(i + 1) % len(tokens)]
        _ = a + b
        _ = a + "_" + b
        _ = a + "@" + b
    t1 = time.time()
    elapsed = max(1e-6, t1 - t0)
    return (iterations * 3) / elapsed


def estimate_generation_time(num_candidates: int, threads: int = 1, sample_tokens: List[str] = None) -> Dict[str, float]:
    per_core = microbenchmark_throughput(sample_tokens or [])
    total = num_candidates / max(1, per_core * threads)
    return {
        "per_core_cand_per_sec": int(per_core),
        "threads": threads,
        "estimated_seconds": total,
        "estimated_minutes": total / 60
    }


if __name__ == "__main__":
    sample_passwords = ["Alice@2022", "passw0rd", "RishuBruno1122", "Xk3!9zQ"]
    sample_tokens = ["Alice", "Rishu", "Bruno", "1998", "2022"]

    print("Scoring candidates:")
    for rec in rank_candidates(sample_passwords, sample_tokens):
        print(f"{rec['password']:25} Likelihood={rec['human_likelihood']:0.3f}  Entropy={rec['entropy_bits']:0.1f}")

    print("\nThroughput Benchmark (1 core):")
    print(microbenchmark_throughput(sample_tokens))

    print("Estimation for 1M candidates (4 threads):")
    print(estimate_generation_time(1_000_000, threads=4))
