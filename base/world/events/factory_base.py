from rule_builder.rules import HasAny, Rule, True_

from ...data.classes import Surface
from ...data.raw import space_locations
from ..rules import Any, UnlockedSpaceLocation


def get_events(surface: Surface) -> dict[str, Rule]:
    events = {}

    if surface.is_space_platform:
        for space_location in space_locations:
            if not space_location.accessible_at_start:
                if any((space_locations[connection].accessible_at_start for connection in space_location.connections)):
                    has_reached_connecting_location = True_()
                else:
                    has_reached_connecting_location = HasAny(*(f'Reach {connection} on {surface.name}' for connection in space_location.connections))

                events[f'Reach {space_location.name}'] = UnlockedSpaceLocation(space_location.name) & has_reached_connecting_location

    return events
