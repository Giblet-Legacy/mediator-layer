"""
conftest.py — pytest path setup for P17 Mediator

Function:
    Puts this directory and the sibling P16 Time directory
    (../forge-time) on sys.path, located from this file rather than the
    working directory, and, for the capsule test only, P1, P2, P3 and P7
    (../envelope-layer, ../sign-layer, ../freeze-layer, ../record-layer),
    which ../forge-time/seal_capsule.py uses. Contains no functions.

Layer:    P17 — Mediator
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)

for _p in [os.path.join(_PARENT, d) for d in ("envelope-layer", "sign-layer", "freeze-layer", "record-layer",
                                              "forge-time")] + [_HERE]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
