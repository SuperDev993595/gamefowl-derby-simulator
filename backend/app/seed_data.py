"""Breed names and image filenames. Trait ratings from TRAIT RATINGS.xlsx (P.S.I.St.A per derby type)."""

# Canonical breed order (1-20). Image filenames: some breeds have spaces (BROWN RED, SID TAYLOR, THOMPSON WHITE).
BREEDS = [
    {"name": "HATCH", "image": "HATCH.jpg"},
    {"name": "KELSO", "image": "KELSO.jpg"},
    {"name": "CLARET", "image": "CLARET.jpg"},
    {"name": "ROUNDHEAD", "image": "ROUNDHEAD.jpg"},
    {"name": "WHITEHACKLE", "image": "WHITEHACKLE.jpg"},
    {"name": "BUTCHER", "image": "BUTCHER.jpg"},
    {"name": "SWEATER", "image": "SWEATER.jpg"},
    {"name": "MUFF", "image": "MUFF.jpg"},
    {"name": "TOPPY", "image": "TOPPY.jpg"},
    {"name": "REDQUILL", "image": "REDQUILL.jpg"},
    {"name": "MUG", "image": "MUG.jpg"},
    {"name": "BROWNRED", "image": "BROWN RED.jpg"},
    {"name": "BLUE", "image": "BLUE.jpg"},
    {"name": "SID TAYLOR", "image": "SID TAYLOR.jpg"},
    {"name": "GREY", "image": "GREY.jpg"},
    {"name": "PYLE", "image": "PYLE.jpg"},
    {"name": "THOMPSON WHITE", "image": "THOMPSON WHITE.jpg"},
    {"name": "HENNY", "image": "HENNY.jpg"},
    {"name": "PUMPKIN", "image": "PUMPKIN.jpg"},
    {"name": "DOM", "image": "DOM.jpg"},
]

# Derby type column key for API/DB
DERBY_TYPES = ["long_heel", "short_heel", "long_blade", "short_blade"]

# Rating strings from xlsx: Long Heel, Short Heel, Long Blade, Short Blade (20 breeds each; Short Blade had 19, we append 20th).
# Format "P.S.I.St.A". For "4.10.6.8" (REDQUILL Long Heel) use accuracy=5.
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
_LONG_BLADE = [
    "9.3.3.7.6", "7.7.7.5.7", "7.7.6.7.8", "6.9.9.5.7", "8.6.6.7.7",
    "5.7.5.7.8", "5.8.6.6.8", "7.4.5.7.6", "6.8.4.5.7", "4.10.7.5.8",
    "4.9.3.6.7", "5.7.3.5.7", "6.7.7.7.9", "2.7.7.6.8", "6.6.6.5.7",
    "5.5.6.7.7", "4.9.8.6.9", "2.8.8.5.8", "4.9.8.4.8", "5.7.7.5.7",
]
_SHORT_BLADE = [
    "8.4.4.8.7", "5.6.7.5.8", "5.7.7.6.8", "5.8.9.5.8", "5.4.6.8.8",
    "5.6.5.8.8", "4.7.7.5.7", "5.5.4.8.8", "5.7.6.6.8", "4.9.9.5.8",
    "3.8.8.5.8", "5.7.7.8.7", "6.8.6.6.8", "3.8.5.6.7", "6.6.5.8.8",
    "4.8.6.3.8", "3.9.6.7.8", "3.6.6.4.8", "5.6.5.7.8",
]
if len(_SHORT_BLADE) < 20:
    _SHORT_BLADE.append("5.6.5.7.8")
RATING_STRINGS = [_LONG_HEEL, _SHORT_HEEL, _LONG_BLADE, _SHORT_BLADE]


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
