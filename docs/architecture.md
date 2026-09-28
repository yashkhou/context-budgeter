# Architecture

Chunks remain source-addressable. The allocator honors source priority and reserved budgets, then spends remaining capacity greedily; redundancy and policy collision checks run independently so compression decisions stay inspectable.

## Design constraints

- deterministic offline behavior
- explicit machine-readable inputs and outputs
- small standard-library surface area
- failures are surfaced rather than hidden

## V1 limitation

Token estimates are deliberately provider-neutral approximations; use a tokenizer adapter when exact provider billing counts matter.
