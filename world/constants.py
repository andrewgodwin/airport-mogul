"""
Various useful constants.
"""

# Item vertical space usage.
USES_FLOOR = 1
USES_LOWER = 2
USES_UPPER = 4
USES_NONFLOOR = USES_LOWER & USES_UPPER
USES_ALL = USES_FLOOR & USES_NONFLOOR