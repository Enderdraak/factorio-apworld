import collections

from BaseClasses import CollectionState, Item, Region
from rule_builder.rules import Has
from worlds.AutoWorld import World

from ..config import game_name, progressive_technologies
from ..data.raw import science_packs, space_locations, surfaces, surfaces_accessible_at_start, technologies, technologies_required_for_automation, technologies_required_for_research
from ..data.utils import craftable_recipes

from .items import create_item, create_items, item_ids, FactorioItem
from .locations import FactorioCraftLocation, FactorioScienceLocation, get_locations, location_ids
from .options import FactorioOptions

class FactorioWorld(World):
    game = game_name

    item_name_to_id = item_ids
    location_name_to_id = location_ids

    options_dataclass = FactorioOptions
    options: FactorioOptions

    progressive_levels: dict[str, list[str]]

    def __init__(self, multiworld, player: int):
        super().__init__(multiworld, player)

    def generate_early(self) -> None:
        self.progressive_levels = {}

        if self.options.progressive:
            self.progressive_levels['progressive science-pack'] = science_packs
            self.progressive_levels.update(progressive_technologies)

    def create_regions(self) -> None:
        # Menu region holds all locations that are not tied to a specific surface
        menu_region = Region('Menu', self.player, self.multiworld)

        self.multiworld.regions.append(menu_region)

        for surface in surfaces:
            region = Region(surface.name, self.player, self.multiworld)
            region.connect(menu_region)

            if surface.name in surfaces_accessible_at_start:
                menu_region.connect(region)

            for recipe_name in craftable_recipes:
                region.add_event(f'Automate {recipe_name} on {surface.name}', show_in_spoiler=False)
                region.add_event(f'Craft {recipe_name} on {surface.name}', show_in_spoiler=False)

            if surface.is_space_platform:
                for space_location in space_locations:
                    if not space_location.accessible_at_start:
                        region.add_event(f'Reach {space_location.name} with {surface.name}', show_in_spoiler=False)

            self.multiworld.regions.append(region)

        for location in get_locations(self.options, self.random):
            location.player = self.player
            location.parent_region = menu_region

            menu_region.locations.append(location)

    def create_items(self) -> None:
        progressive_counts = collections.Counter()

        for item in create_items(self.options, self.progressive_levels, self.player):
            if item.name in self.progressive_levels:
                technology_name = self.progressive_levels[item.name][progressive_counts[item.name]]

                progressive_counts[item.name] += 1
            else:
                technology_name = item.name

            if technology_name in technologies_required_for_automation:
                # Early science locations are always placed at the start
                for location in self.get_locations():
                    if isinstance(location, FactorioScienceLocation) and location.item is None:
                        location.count = min(location.count, technologies[technology_name].unit_count)
                        location.place_locked_item(item)

                        break
            elif technology_name in technologies_required_for_research:
                # Early craft locations are always placed at the start
                for location in self.get_locations():
                    if isinstance(location, FactorioCraftLocation) and location.item is None:
                        location.place_locked_item(item)

                        break
            else:
                self.multiworld.itempool.append(item)

    def set_rules(self) -> None:
        from .rules.events import get_events_rules
        from .rules.locations import get_locations_rules

        for location_name, rule in get_events_rules().items():
            self.set_rule(self.get_location(location_name), rule)

        for location_name, rule in get_locations_rules(self.get_locations()).items():
            self.set_rule(self.get_location(location_name), rule)

        match (self.options.goal.get_victory_condition()):
            case {'type': 'reach-space-location', 'space_location': space_location}:
                self.set_completion_rule(Has(f'Reach {space_location} with space-platform'))
            case _:
                raise Error('Invalid victory condition')

    def create_item(self, name: str) -> FactorioItem:
        return create_item(self.progressive_levels, self.player, name)

    def get_filler_item_name(self) -> str:
        from .items.pool import upgrades_max_count

        filler_item_pool = [name for name, max_count in upgrades_max_count.items() if max_count is None]

        if len(filler_item_pool) == 0:
            filler_item_pool = upgrades_max_count.keys()

        return self.random.choice(filler_item_pool)

    def collect_item(self, state: CollectionState, item: Item, remove: bool = False) -> str | None:
        if item.advancement or item.name in self.progressive_levels:
            return item.name

        return None

    def collect(self, state: CollectionState, item: Item) -> bool:
        if super().collect(state, item):
            if item.name in self.progressive_levels:
                level = state.prog_items[self.player][item.name]
                if level <= len(self.progressive_levels[item.name]):
                    state.prog_items[self.player][self.progressive_levels[item.name][level - 1]] += 1

            return True

        return False

    def remove(self, state: CollectionState, item: Item) -> bool:
        if super().collect(state, item):
            if item.name in self.progressive_levels:
                level = state.prog_items[self.player][item.name] + 1
                if level <= len(self.progressive_levels[item.name]):
                    state.prog_items[self.player][self.progressive_levels[item.name][level - 1]] -= 1

            return True

        return False

    def generate_basic(self) -> None:
        world_gen = self.options.world_gen.value
        if world_gen['basic'].get('seed', None) is None:
            world_gen['basic']['seed'] = self.random.randint(0, 2 ** 32 - 1) # 32 bit uint

        if self.options.tech_tree_information.value == self.options.tech_tree_information.option_full:
            for location in self.get_locations():
                 if not location.is_event:
                    self.options.start_location_hints.value.add(location.name)

    def generate_output(self, output_directory: str) -> None:
        from ..mod.data import get_mod_data, get_mod_name, get_mod_version
        from ..mod.generate import generate_mod

        generate_mod(get_mod_name(self), get_mod_version(self), get_mod_data(self), self, output_directory)
