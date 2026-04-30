from rule_builder.rules import Has, Rule, True_

from ...data.classes import Surface
from ...data.lookup import machines_by
from ...data.raw import machines_for_manual_craft, space_locations
from ..rules import Any, CanCraft

def get_asteroid_productions(surface: Surface) -> dict[str, tuple[Rule, dict[str, bool]]]:
    events = {}

    if surface.is_space_platform:
        available_asteroid_chunks = set()
        for space_location in space_locations:
            available_asteroid_chunks.update(space_location.asteroid_chunks)

        for asteroid_chunk in available_asteroid_chunks:
            machines = machines_by(can_be_placed_on=surface, is_asteroid_collector=True)

            if len(machines) == 0:
                continue

            reached_location_rule = Any([
                True_() if space_location.accessible_at_start else Has(f'Reach {space_location.name} on {surface.name}')
                for space_location in space_locations
                if asteroid_chunk in space_location.asteroid_chunks
            ])

            if len(machines_for_manual_craft.intersection((machine.name for machine in machines))) > 0:
                events[f'Collect {asteroid_chunk}'] = (
                    reached_location_rule,
                    {asteroid_chunk: False},
                )

            events[f'Automate {asteroid_chunk} collection'] = (
                reached_location_rule & Any([CanCraft(machine.name, surface) for machine in machines]),
                {asteroid_chunk: True},
            )

    return events
