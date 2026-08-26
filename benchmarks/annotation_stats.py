#!/usr/bin/env python3
# regula-ignore
"""Multi-annotator agreement statistics for the labelled corpus.

Krippendorff's alpha for nominal labels is the primary statistic because it
supports two or more raters and incomplete rating matrices. Fleiss' kappa is
retained as a complete-case compatibility view. Neither statistic turns an
adjudicated label into objective ground truth.

Stdlib only. Rater files use the same packet format as
rater1_blind_subset.json / rater2_blind_subset.json: a dict with a
"labels" list of entries carrying "id"-forming fields and a "label" of
"tp" or "fp". Entries are matched across raters by (project, file, line)
when no explicit "id" is present, matching compute_kappa's convention.

Usage:
    python3 benchmarks/annotation_stats.py rater1.json rater2.json rater3.json
    python3 benchmarks/annotation_stats.py --test   # synthetic validation
"""

import json
import math
import random
import sys
from pathlib import Path

CATEGORIES = ("tp", "fp")


def entry_id(e: dict) -> str:
    if e.get("id"):
        return str(e["id"])
    return f"{e.get('project','?')}::{e.get('file','?')}::{e.get('line','?')}"


def load_rater(path: Path) -> dict:
    """Load {finding_id: label} for one rater, keeping only tp/fp labels."""
    data = json.load(Path(path).open())
    entries = data if isinstance(data, list) else data.get(
        "labels", data.get("candidates", []))
    out = {}
    for e in entries:
        label = (e.get("label") or "").strip().lower()
        if label in CATEGORIES:
            out[entry_id(e)] = label
    return out


def fleiss_kappa(raters: list) -> dict:
    """Fleiss' kappa over the findings every rater labelled.

    raters: list of {finding_id: label} dicts, one per rater.
    Standard formulation: for each of N items rated by n raters into k
    categories, P_i = (sum_j n_ij^2 - n) / (n(n-1)); kappa =
    (P_bar - P_e) / (1 - P_e) with P_e = sum_j p_j^2.
    """
    if len(raters) < 2:
        return {"error": "need at least 2 raters", "n_items": 0}
    common = set(raters[0])
    for r in raters[1:]:
        common &= set(r)
    items = sorted(common)
    n_items = len(items)
    n_raters = len(raters)
    if n_items == 0:
        return {"error": "no findings labelled by all raters", "n_items": 0}

    counts = []
    for fid in items:
        row = {c: 0 for c in CATEGORIES}
        for r in raters:
            row[r[fid]] += 1
        counts.append(row)

    total = n_items * n_raters
    p_j = {c: sum(row[c] for row in counts) / total for c in CATEGORIES}
    p_e = sum(v * v for v in p_j.values())

    p_i_sum = 0.0
    unanimous = 0
    for row in counts:
        s = sum(v * v for v in row.values())
        p_i_sum += (s - n_raters) / (n_raters * (n_raters - 1))
        if max(row.values()) == n_raters:
            unanimous += 1
    p_bar = p_i_sum / n_items

    if p_e >= 1.0:
        # All raters used one category for everything: agreement is total
        # but kappa is undefined (division by zero); report explicitly.
        return {
            "n_items": n_items, "n_raters": n_raters,
            "kappa": None, "p_bar": p_bar, "p_e": p_e,
            "note": "kappa undefined: zero label variance (all one category)",
            "unanimous": unanimous,
            "category_proportions": p_j,
        }

    kappa = (p_bar - p_e) / (1 - p_e)
    disagreements = [
        items[i] for i, row in enumerate(counts)
        if max(row.values()) < n_raters
    ]
    return {
        "n_items": n_items,
        "n_raters": n_raters,
        "kappa": round(kappa, 4),
        "p_bar": round(p_bar, 4),
        "p_e": round(p_e, 4),
        "unanimous": unanimous,
        "category_proportions": {c: round(v, 4) for c, v in p_j.items()},
        "disagreement_ids": disagreements,
    }


def _nominal_alpha(unit_ratings: list[list[str]]) -> float | None:
    """Return nominal Krippendorff alpha for pairable rating units.

    The coincidence-matrix formulation weights a unit with ``m`` available
    ratings by ``1 / (m - 1)``. Units with fewer than two ratings are excluded
    because they contain no observable agreement or disagreement.
    """
    pairable = [ratings for ratings in unit_ratings if len(ratings) >= 2]
    total = sum(len(ratings) for ratings in pairable)
    if total < 2:
        return None

    category_counts: dict[str, int] = {}
    observed_disagreement = 0.0
    for ratings in pairable:
        counts: dict[str, int] = {}
        for label in ratings:
            counts[label] = counts.get(label, 0) + 1
            category_counts[label] = category_counts.get(label, 0) + 1
        m = len(ratings)
        observed_disagreement += (
            m * m - sum(count * count for count in counts.values())
        ) / (m - 1)

    observed_disagreement /= total
    expected_disagreement = (
        total * total - sum(count * count for count in category_counts.values())
    ) / (total * (total - 1))
    if math.isclose(expected_disagreement, 0.0):
        return None
    return 1.0 - (observed_disagreement / expected_disagreement)


def krippendorff_alpha_nominal(
    raters: list[dict[str, str]],
    *,
    n_resamples: int = 2_000,
    seed: int = 20260825,
) -> dict:
    """Compute nominal alpha and a deterministic item-bootstrap 95% CI.

    Missing labels remain missing. The point estimate uses every item with at
    least two ratings; the interval resamples those items, not individual
    ratings, so within-item dependence is preserved.
    """
    if len(raters) < 2:
        return {"error": "need at least 2 raters", "n_items": 0}
    if n_resamples < 0:
        raise ValueError("n_resamples must be non-negative")

    item_ids = sorted(set().union(*(set(rater) for rater in raters)))
    units = [
        [rater[item_id] for rater in raters if item_id in rater]
        for item_id in item_ids
    ]
    pairable = [ratings for ratings in units if len(ratings) >= 2]
    alpha = _nominal_alpha(pairable)
    observed_ratings = sum(len(ratings) for ratings in units)
    possible_ratings = len(item_ids) * len(raters)
    categories = sorted({label for ratings in pairable for label in ratings})

    result = {
        "n_items": len(pairable),
        "n_items_total": len(item_ids),
        "n_raters": len(raters),
        "n_ratings": observed_ratings,
        "missing_ratings": possible_ratings - observed_ratings,
        "rating_coverage": (
            round(observed_ratings / possible_ratings, 4)
            if possible_ratings else 0.0
        ),
        "categories": categories,
        "alpha": None if alpha is None else round(alpha, 4),
        "alpha_ci_95": None,
        "bootstrap_resamples_requested": n_resamples,
        "bootstrap_resamples_valid": 0,
        "bootstrap_seed": seed,
    }
    if not pairable:
        result["error"] = "no findings have at least two ratings"
        return result
    if alpha is None:
        result["note"] = "alpha undefined: zero expected disagreement"
        return result
    if not n_resamples:
        return result

    rng = random.Random(seed)
    bootstrapped: list[float] = []
    for _ in range(n_resamples):
        sample = [rng.choice(pairable) for _ in range(len(pairable))]
        estimate = _nominal_alpha(sample)
        if estimate is not None:
            bootstrapped.append(estimate)
    bootstrapped.sort()
    result["bootstrap_resamples_valid"] = len(bootstrapped)
    if bootstrapped:
        last = len(bootstrapped) - 1
        lower = bootstrapped[math.floor(0.025 * last)]
        upper = bootstrapped[math.ceil(0.975 * last)]
        result["alpha_ci_95"] = [round(lower, 4), round(upper, 4)]
    return result


def interpret(kappa) -> str:
    """Describe an estimate without treating a universal band as a gate."""
    if kappa is None:
        return "undefined (zero label variance)"
    return (f"agreement estimate {kappa:.4f}; report its interval, missingness, "
            "label prevalence and disagreement cases without a universal "
            "publishability threshold")


def _self_test() -> int:
    # Worked example (Fleiss 1971 structure, 2 categories): 4 items,
    # 3 raters. Item rows (tp,fp): (3,0), (2,1), (1,2), (0,3).
    # p_tp = 6/12 = 0.5; p_e = 0.5. P_i: 1.0, 1/3, 1/3, 1.0; P_bar = 2/3.
    # kappa = (2/3 - 1/2) / (1 - 1/2) = 1/3.
    r1 = {"a": "tp", "b": "tp", "c": "tp", "d": "fp"}
    r2 = {"a": "tp", "b": "tp", "c": "fp", "d": "fp"}
    r3 = {"a": "tp", "b": "fp", "c": "fp", "d": "fp"}
    result = fleiss_kappa([r1, r2, r3])
    expected = round(1 / 3, 4)
    ok = result["kappa"] == expected
    print(f"self-test: kappa={result['kappa']} expected={expected} "
          f"{'OK' if ok else 'FAIL'}")
    return 0 if ok else 1


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    if args == ["--test"]:
        return _self_test()
    raters = [load_rater(Path(p)) for p in args]
    for path, r in zip(args, raters):
        print(f"  {path}: {len(r)} labelled")
    result = {
        "krippendorff_alpha_nominal": krippendorff_alpha_nominal(raters),
        "fleiss_kappa_complete_case": fleiss_kappa(raters),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
