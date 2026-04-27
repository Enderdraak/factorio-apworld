'''Implementation of production logic with events and custom collection logic'''


from BaseClasses import Item, ItemClassification, Location, Region
from rule_builder.rules import Rule

from ...config import game_name
from ...data.classes import Surface


class FactorioProductionEventItem(Item):
    game = game_name
    production: dict[str, bool]
    surface: Surface

    def __init__(self, player: int, name: str, production: list[str, bool], surface: Surface):
        super().__init__(name, ItemClassification.progression, None, player)
        self.production = production
        self.surface = surface


class FactorioProductionEventLocation(Location):
    game = game_name

    def __init__(self, player: int, name: str, parent: Region | None = None):
        super().__init__(player, name, None, parent)
        self.show_in_spoiler = False


def create_production_events(world, surface, events: dict[str, tuple[Rule, dict[str, bool]]]) -> None:
    region = world.get_region(surface.name)

    for name, (rule, production) in events.items():
        event_item = FactorioProductionEventItem(region.player, f'{name} on {surface.name}', production, surface)
        event_location = FactorioProductionEventLocation(region.player, f'{name} on {surface.name}', region)

        world.set_rule(event_location, rule)

        event_location.place_locked_item(event_item)

        region.locations.append(event_location)


def get_production_item_name(surface_name: str, item_name: str, automated: bool):
    return f'Production of {item_name}{' automated' if automated else ''} on {surface_name}'


def collect_production_event(world, state, item: FactorioProductionEventItem) -> bool:
    for item_name, automated in item.production.items():
        state.add_item(get_production_item_name(item.surface.name, item_name, automated), world.player)
    return True


def remove_production_event(world, state, item: FactorioProductionEventItem) -> bool:
    for item_name, automated in item.production.items():
        state.remove_item(get_production_item_name(item.surface.name, item_name, automated), world.player)
    return True
