# native

Reserved for C extensions on profiled hot paths; none are needed.

A full `compass.scoring.rank_priorities()` call — 30 districts, a 21-step weight sweep, six
sensitivity schemes and 2,000 Monte Carlo draws — takes about 20 ms in Python with NumPy, and
results are cached. Revisit only if household-level estimation with replicate weights is added.
