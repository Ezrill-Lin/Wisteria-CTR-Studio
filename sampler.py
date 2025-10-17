"""Sampling utilities for synthetic identity generation.

This module reads a JSON-defined identity bank and produces sampled
identities according to the configured distributions.
"""

import json
import math
import os
import random
from typing import Any, Dict, List


def load_identity_bank(path: str) -> Dict[str, Any]:
    """Load an identity bank JSON file from disk.

    Args:
        path: Filesystem path to the identity bank JSON.

    Returns:
        Parsed JSON as a dictionary.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _weighted_choice(weights: List[float], rng: random.Random) -> int:
    """Return an index sampled proportional to ``weights``.

    Args:
        weights: Non-negative weights.
        rng: Random number generator.

    Returns:
        Selected index in ``weights``.
    """
    total = sum(weights)
    if total <= 0:
        raise ValueError("Sum of weights must be positive")
    r = rng.random() * total
    upto = 0.0
    for i, w in enumerate(weights):
        upto += w
        if r <= upto:
            return i
    return len(weights) - 1


def _sample_categorical(cfg: Dict[str, Any], rng: random.Random):
    """Sample a value from a categorical configuration.

    Args:
        cfg: Dict with keys ``values`` and optional ``probs``.
        rng: Random number generator.

    Returns:
        One element from ``values``.
    """
    values = cfg.get("values", [])
    probs = cfg.get("probs")
    if not values:
        raise ValueError("categorical values empty")
    if probs is None:
        return rng.choice(values)
    if len(values) != len(probs):
        raise ValueError("values and probs length mismatch")
    idx = _weighted_choice(probs, rng)
    return values[idx]


def _sample_int_normal(cfg: Dict[str, Any], rng: random.Random) -> int:
    """Sample an integer from a truncated normal distribution.

    Args:
        cfg: Dict with ``mean``, ``std``, ``min``, ``max``.
        rng: Random number generator.

    Returns:
        Integer sample within [min, max].
    """
    mean = cfg.get("mean", 40)
    std = cfg.get("std", 12)
    vmin = cfg.get("min", 0)
    vmax = cfg.get("max", 120)
    # Truncated normal via rejection with fallback to clipping
    for _ in range(8):
        x = rng.gauss(mean, std)
        if vmin <= x <= vmax:
            return int(round(x))
    x = max(vmin, min(vmax, rng.gauss(mean, std)))
    return int(round(x))


def _sample_float_bucketed(cfg: Dict[str, Any], rng: random.Random) -> float:
    """Sample a float uniformly within a randomly chosen weighted bucket.

    Args:
        cfg: Dict containing ``buckets`` with ``min``, ``max``, and ``weight``.
        rng: Random number generator.

    Returns:
        Float sampled from the selected bucket range.
    """
    buckets = cfg.get("buckets", [])
    if not buckets:
        raise ValueError("float_bucketed requires 'buckets'")
    weights = [b.get("weight", 1.0) for b in buckets]
    idx = _weighted_choice(weights, rng)
    b = buckets[idx]
    vmin = float(b.get("min", 0.0))
    vmax = float(b.get("max", vmin))
    if vmax < vmin:
        vmin, vmax = vmax, vmin
    return rng.random() * (vmax - vmin) + vmin


def _sample_region(cfg: Dict[str, Any], rng: random.Random) -> str:
    """Sample a region as a "City, ST" string from composite values.

    Args:
        cfg: Dict with list of objects containing ``city`` and ``state``.
        rng: Random number generator.

    Returns:
        Region string.
    """
    values = cfg.get("values", [])
    if not values:
        raise ValueError("region.values empty")
    item = rng.choice(values)
    city = item.get("city", "Unknown")
    state = item.get("state", "")
    if state:
        return f"{city}, {state}"
    return city


def _sample_bool(cfg: Dict[str, Any], rng: random.Random) -> bool:
    """Sample a boolean with probability ``p_true`` of being True.

    Args:
        cfg: Dict containing ``p_true`` (default 0.5).
        rng: Random number generator.

    Returns:
        Boolean sample.
    """
    p_true = float(cfg.get("p_true", 0.5))
    return rng.random() < p_true


def _sample_health(cfg: Dict[str, Any], rng: random.Random):
    """Sample health status and an optional illness name.

    If the boolean health flag is True, return a random illness from ``values``
    excluding the literal "None" entry; otherwise illness is ``None``.

    Args:
        cfg: Dict with ``p_true`` and ``values``.
        rng: Random number generator.

    Returns:
        Tuple ``(health_status: bool, illness: Optional[str])``.
    """
    has_condition = _sample_bool(cfg, rng)
    illness = None
    if has_condition:
        values = [v for v in cfg.get("values", []) if v.lower() != "none"]
        if values:
            illness = rng.choice(values)
    return has_condition, illness


def sample_identity(bank: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
    """Sample a single identity record from the bank.

    Args:
        bank: Parsed identity bank configuration.
        rng: Random number generator.

    Returns:
        Dictionary with sampled fields and optional ``illness``.
    """
    gender = _sample_categorical(bank["gender"], rng)
    age = _sample_int_normal(bank["age"], rng)
    region = _sample_region(bank["region"], rng)
    occupation = _sample_categorical(bank["occupation"], rng)
    annual_salary = _sample_float_bucketed(bank["annual_salary"], rng)
    liability_status = _sample_float_bucketed(bank["liability_status"], rng)
    is_married = _sample_bool(bank["is_married"], rng)
    health_status, illness = _sample_health(bank["health_status"], rng)

    ident = {
        "gender": gender,
        "age": age,
        "region": region,
        "occupation": occupation,
        "annual_salary": round(float(annual_salary), 2),
        "liability_status": round(float(liability_status), 2),
        "is_married": bool(is_married),
        "health_status": bool(health_status)
    }
    if health_status and illness:
        ident["illness"] = illness
    return ident


def sample_identities(n: int, bank: Dict[str, Any], seed: int | None = None) -> List[Dict[str, Any]]:
    """Sample ``n`` identities using the provided bank.

    Args:
        n: Number of records to generate.
        bank: Parsed identity bank configuration.
        seed: Optional seed for reproducibility.

    Returns:
        List of identity dictionaries.
    """
    rng = random.Random(seed)
    return [sample_identity(bank, rng) for _ in range(n)]


__all__ = [
    "load_identity_bank",
    "sample_identities",
    "sample_identity",
]
