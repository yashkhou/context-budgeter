# Implementation note

Working V1 scope: Inspect an agent context bundle as a budget: source allocation, redundancy and conflicting policy text before tokens are spent.

Verified with `python -m unittest discover -s tests -v`.

Known boundary: Token estimates are deliberately provider-neutral approximations; use a tokenizer adapter when exact provider billing counts matter.
