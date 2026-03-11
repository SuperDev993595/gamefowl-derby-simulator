"""
Derby attribute modifiers per client doc "Derby Attribute".
Each derby type modifies the five core attributes (Power, Speed, Intelligence, Accuracy, Stamina)
before match simulation. Percentages are applied to base breed traits.
"""
# (power, speed, intelligence, accuracy, stamina) as multiplier - 1.0 = no change
DERBY_MODIFIERS = {
    "long_heel": (1.0, 1.0, 1.0, 1.0, 1.0),   # The favorite of the South; neutral
    "short_heel": (1.15, 0.85, 0.95, 1.05, 1.10),   # Power +15%, Speed -15%, etc.
    "pilipino": (0.95, 1.20, 1.10, 1.15, 0.85),     # Fast and furious
    "mexican": (1.10, 1.0, 1.05, 1.25, 1.25),       # Powerful but smart
}

# Keep type: (power, speed, intelligence, accuracy, stamina)
# Bench: improves Endurance, Durability, Recovery; slightly reduces explosive speed
# Flypen: improves Agility, Speed, Reflex; slightly reduces stamina
KEEP_MODIFIERS = {
    "bench": (1.05, 0.95, 1.0, 1.0, 1.10),   # +stamina/durability, -speed
    "flypen": (1.0, 1.10, 1.05, 1.05, 0.90),  # +speed/agility/reflex, -stamina
}


def apply_derby_modifiers(
    base: tuple[int, int, int, int, int],
    derby_type: str,
) -> tuple[float, float, float, float, float]:
    """Apply derby type percentage modifiers to base (P, S, I, A, St). Returns floats."""
    mod = DERBY_MODIFIERS.get(derby_type, (1.0, 1.0, 1.0, 1.0, 1.0))
    return tuple(b * m for b, m in zip(base, mod))


def apply_keep_modifiers(
    traits: tuple[float, ...],
    keep_type: str,
) -> tuple[float, float, float, float, float]:
    """Apply keep type modifiers. Input and output are (P, S, I, A, St) as floats."""
    mod = KEEP_MODIFIERS.get(keep_type, (1.0, 1.0, 1.0, 1.0, 1.0))
    return tuple(t * m for t, m in zip(traits, mod))
