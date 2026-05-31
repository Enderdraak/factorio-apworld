from ...config import craftsanity_filter
from ...data.raw import items, science_packs
from ...data.utils import craftable_items


science_location_pools: dict[str, list[str]] = {}

for i, pack in enumerate(science_packs, start=1):
    max_needed: int = 999
    prefix: str = f"AP-{i}-"
    science_location_pools[pack] = [prefix + str(x).upper().zfill(3) for x in range(1, max_needed + 1)]

craftsanity_item_pool = sorted([item_name for item_name in craftable_items if item_name not in science_packs and craftsanity_filter(item_name)])
