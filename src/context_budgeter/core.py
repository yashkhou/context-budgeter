from __future__ import annotations

from collections import defaultdict
import re


def estimate(text):
    return max(1, (len(text) + 3) // 4)


def similarity(a, b):
    left = set(re.findall(r"[a-z0-9]+", a.lower())); right = set(re.findall(r"[a-z0-9]+", b.lower()))
    return len(left & right) / max(1, len(left | right))


def duplicates(chunks, threshold=0.8):
    out = []
    for i, first in enumerate(chunks):
        for j in range(i + 1, len(chunks)):
            score = similarity(first["text"], chunks[j]["text"])
            if score >= threshold:
                out.append({"a": first["id"], "b": chunks[j]["id"], "similarity": round(score, 3)})
    return out


def collisions(chunks):
    facts = defaultdict(set)
    for chunk in chunks:
        match = re.match(r"\s*(allow|deny)\s+(.+?)\s*$", chunk["text"], re.I)
        if match:
            facts[match.group(2).lower()].add(match.group(1).lower())
    return [{"subject": key, "decisions": sorted(value)} for key, value in facts.items() if len(value) > 1]


def _by_source(rows):
    totals = defaultdict(int)
    for row in rows:
        totals[row.get("source", "unknown")] += row["estimated_tokens"]
    return dict(sorted(totals.items()))


def allocate(chunks, budget):
    rows = [{**chunk, "estimated_tokens": estimate(chunk["text"])} for chunk in chunks]
    used = 0; selected = []
    for chunk in sorted(rows, key=lambda item: (-int(item.get("priority", 0)), item["id"])):
        size = chunk["estimated_tokens"]
        if used + size <= budget:
            selected.append({**chunk, "allocated_tokens": size}); used += size
    return {"budget": budget, "used": used, "remaining": budget - used, "selected": selected, "duplicates": duplicates(rows), "policy_collisions": collisions(rows), "by_source": _by_source(rows)}


def optimize(chunks, budget, duplicate_threshold=0.8):
    """Choose whole context chunks, suppress near-duplicates, and honor dependency closure."""
    rows = [{**chunk, "estimated_tokens": estimate(chunk["text"])} for chunk in chunks]
    by_id = {row["id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError("chunk ids must be unique")
    dropped = []
    duplicate_of = {}
    ordered = sorted(rows, key=lambda item: (-int(item.get("priority", 0)), item["estimated_tokens"], item["id"]))
    keepers = []
    for row in ordered:
        match = next((kept for kept in keepers if similarity(row["text"], kept["text"]) >= duplicate_threshold), None)
        if match:
            duplicate_of[row["id"]] = match["id"]
            dropped.append({"id": row["id"], "reason": "near-duplicate", "of": match["id"]})
        else:
            keepers.append(row)
    used = 0; selected = []; selected_ids = set()
    def closure(row, stack=()):
        if row["id"] in stack:
            raise ValueError("dependency cycle: " + " -> ".join((*stack, row["id"])))
        result = []
        for dep_id in row.get("requires", []):
            if dep_id not in by_id:
                raise ValueError(f"{row['id']} requires missing chunk {dep_id}")
            if dep_id in duplicate_of:
                dep_id = duplicate_of[dep_id]
            dep = by_id[dep_id]
            result.extend(closure(dep, (*stack, row["id"])))
        result.append(row)
        unique = []
        seen = set()
        for item in result:
            if item["id"] not in seen:
                unique.append(item); seen.add(item["id"])
        return unique
    for row in keepers:
        needed = [item for item in closure(row) if item["id"] not in selected_ids and item["id"] not in duplicate_of]
        cost = sum(item["estimated_tokens"] for item in needed)
        if used + cost > budget:
            dropped.append({"id": row["id"], "reason": "budget", "required_tokens": cost})
            continue
        for item in needed:
            selected.append({**item, "allocated_tokens": item["estimated_tokens"]}); selected_ids.add(item["id"]); used += item["estimated_tokens"]
    return {"budget": budget, "used": used, "remaining": budget - used, "selected": selected, "dropped": dropped, "duplicates": duplicates(rows, duplicate_threshold), "policy_collisions": collisions(rows), "by_source": _by_source(rows)}
