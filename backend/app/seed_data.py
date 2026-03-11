"""Breed names and image filenames. Trait ratings from TRAIT RATINGS.xlsx (P.S.I.St.A per derby type)."""

# Canonical breed order (1-20). Image filenames: some breeds have spaces. Short descriptions per frontend guide.
BREEDS = [
    {"name": "HATCH", "image": "HATCH.jpg", "description": "A classic American strain known for power and gameness. Strong in the heel."},
    {"name": "KELSO", "image": "KELSO.jpg", "description": "Famous for speed and intelligence. Quick to strike and adapt."},
    {"name": "CLARET", "image": "CLARET.jpg", "description": "Irish heritage. Balanced fighter with good stamina and accuracy."},
    {"name": "ROUNDHEAD", "image": "ROUNDHEAD.jpg", "description": "Intelligent and agile. Excels in derbies that reward timing."},
    {"name": "WHITEHACKLE", "image": "WHITEHACKLE.jpg", "description": "Powerful and durable. A favorite in long, demanding derbies."},
    {"name": "BUTCHER", "image": "BUTCHER.jpg", "description": "Aggressive and accurate. Known for decisive, clean strikes."},
    {"name": "SWEATER", "image": "SWEATER.jpg", "description": "Speed and intelligence. Thrives in fast-paced derbies."},
    {"name": "MUFF", "image": "MUFF.jpg", "description": "Strong power and recovery. Traditional choice for heel derbies."},
    {"name": "TOPPY", "image": "TOPPY.jpg", "description": "Balanced across all qualities. A reliable all-rounder."},
    {"name": "REDQUILL", "image": "REDQUILL.jpg", "description": "Exceptional speed and accuracy. Dominant in Pilipino-style derbies."},
    {"name": "MUG", "image": "MUG.jpg", "description": "High accuracy and cunning. Low endurance but deadly precision."},
    {"name": "BROWNRED", "image": "BROWN RED.jpg", "description": "Solid power and speed. Consistent performer in any derby."},
    {"name": "BLUE", "image": "BLUE.jpg", "description": "Intelligent and well-rounded. Strong in stamina and accuracy."},
    {"name": "SID TAYLOR", "image": "SID TAYLOR.jpg", "description": "Speed and agility. Best in derbies that favor quick exchanges."},
    {"name": "GREY", "image": "GREY.jpg", "description": "Durable and accurate. Excels in long, strategic derbies."},
    {"name": "PYLE", "image": "PYLE.jpg", "description": "Power and stamina. A force in endurance-heavy derbies."},
    {"name": "THOMPSON WHITE", "image": "THOMPSON WHITE.jpg", "description": "Extreme speed and reflex. High risk, high reward."},
    {"name": "HENNY", "image": "HENNY.jpg", "description": "Agile and fast. Strong in speed-focused derbies."},
    {"name": "PUMPKIN", "image": "PUMPKIN.jpg", "description": "Balanced power and stamina. Reliable in Mexican-style derbies."},
    {"name": "DOM", "image": "DOM.jpg", "description": "Well-rounded and intelligent. Adapts to any derby style."},
]

# Derby type column key for API/DB (per client: Long Heel, Short Heel, Pilipino, Mexican)
DERBY_TYPES = ["long_heel", "short_heel", "pilipino", "mexican"]

# Rating strings: Power.Speed.Intelligence.Stamina.Accuracy (P.S.I.St.A) per derby type, 20 breeds each.
_LONG_HEEL = [
    "10.5.5.8.6", "7.7.6.5.8", "5.8.6.6.7", "5.8.9.6.8", "10.6.6.8.7",
    "7.6.6.8.8", "5.8.8.5.7", "9.5.4.8.7", "6.8.6.6.7", "4.10.6.8",
    "5.9.2.3.9", "5.8.5.5.7", "6.8.8.7.7", "3.9.3.5.8", "7.5.5.7.8",
    "8.6.5.8.9", "5.9.7.5.8", "2.10.7.3.7", "5.9.6.6.8", "6.7.6.7.8",
]
_SHORT_HEEL = [
    "10.2.2.9.5", "5.7.7.5.6", "6.7.8.5.7", "6.8.9.6.8", "10.6.5.9.6",
    "7.6.5.8.7", "3.7.6.4.7", "9.5.3.9.7", "5.8.4.6.7", "3.10.6.4.7",
    "4.8.3.5.8", "4.6.6.4.7", "6.6.7.6.7", "3.7.2.5.7", "6.7.5.8.8",
    "7.7.7.8.8", "4.8.7.5.7", "3.7.6.7.7", "2.8.7.4.7", "4.7.6.7.7",
]
# Pilipino: fast and furious; speed/accuracy focused. Using varied base ratings.
_PILIPINO = [
    "9.3.3.7.6", "7.7.7.5.7", "7.7.6.7.8", "6.9.9.5.7", "8.6.6.7.7",
    "5.7.5.7.8", "5.8.6.6.8", "7.4.5.7.6", "6.8.4.5.7", "4.10.7.5.8",
    "4.9.3.6.7", "5.7.3.5.7", "6.7.7.7.9", "2.7.7.6.8", "6.6.6.5.7",
    "5.5.6.7.7", "4.9.8.6.9", "2.8.8.5.8", "4.9.8.4.8", "5.7.7.5.7",
]
# Mexican: powerful but smart; stamina and accuracy.
_MEXICAN = [
    "8.4.4.8.7", "5.6.7.5.8", "5.7.7.6.8", "5.8.9.5.8", "5.4.6.8.8",
    "5.6.5.8.8", "4.7.7.5.7", "5.5.4.8.8", "5.7.6.6.8", "4.9.9.5.8",
    "3.8.8.5.8", "5.7.7.8.7", "6.8.6.6.8", "3.8.5.6.7", "6.6.5.8.8",
    "4.8.6.3.8", "3.9.6.7.8", "3.6.6.4.8", "5.6.5.7.8",
]
if len(_MEXICAN) < 20:
    _MEXICAN.append("5.6.5.7.8")
RATING_STRINGS = [_LONG_HEEL, _SHORT_HEEL, _PILIPINO, _MEXICAN]


def get_rating_list(derby_index: int, breed_index: int) -> list[int]:
    """Parse P.S.I.St.A string; default accuracy 5 if only 4 numbers."""
    lst = RATING_STRINGS[derby_index]
    s = lst[breed_index] if breed_index < len(lst) else "5.5.5.5.5"
    parts = s.split(".")
    nums = [int(x) for x in parts if x.isdigit()]
    if len(nums) == 4:
        nums.append(5)
    while len(nums) < 5:
        nums.append(5)
    return nums[:5]
