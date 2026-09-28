# context-budgeter

Inspect an agent context bundle as a budget: source allocation, redundancy and conflicting policy text before tokens are spent.

## What it does

- estimates tokens with a transparent byte/character heuristic
- allocates a hard context budget by source priority and reserved minimums
- finds near-duplicate chunks with normalized word-set similarity
- flags simple policy collisions such as allow/deny statements about the same subject

## Quick start

```bash
PYTHONPATH=src python -m context_budgeter examples/context.json --budget 1200
```

No model API, network service, or third-party package is required.

## Architecture

Chunks remain source-addressable. The allocator honors source priority and reserved budgets, then spends remaining capacity greedily; redundancy and policy collision checks run independently so compression decisions stay inspectable.

See [`docs/architecture.md`](docs/architecture.md) for the data model and trade-offs.

## V1 boundary

Token estimates are deliberately provider-neutral approximations; use a tokenizer adapter when exact provider billing counts matter.

## Development

```bash
python -m unittest discover -s tests -v
```

MIT licensed.


## v0.1.1

**Dependency-aware context optimization.** A new optimizer selects whole chunks, suppresses lower-priority near-duplicates, resolves required context dependencies, and fails fast on missing or cyclic dependencies.

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```
