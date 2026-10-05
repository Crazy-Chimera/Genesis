from __future__ import annotations

from typing import Iterable
import numpy as np


def global_phase_harmonics(
    phase: np.ndarray,
    orders: Iterable[int] = (2, 3, 4),
) -> tuple[float, ...]:
    """Measure global phase harmonics while excluding the first harmonic.

    The first harmonic is intentionally excluded because its magnitude is the
    global coherence observable used as the prediction target.
    """
    values: list[float] = []
    flat = np.asarray(phase, dtype=np.float64).ravel()
    if flat.size == 0:
        return ()

    for order in orders:
        if order < 2:
            raise ValueError("harmonic orders must be >= 2")
        z = np.mean(np.exp(1j * order * flat))
        values.extend((float(z.real), float(z.imag), float(abs(z))))
    return tuple(values)
