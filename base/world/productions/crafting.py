from rule_builder.rules import Rule

from ...data.classes import Surface
from ...data.lookup import machines_by
from ...data.raw import machines_for_manual_craft
from ...data.utils import craftable_recipes
from ..rules import All, Any, CanAutomate, CanCraft, UnlockedRecipe

def get_crafting_productions(surface: Surface) -> dict[str, tuple[Rule, dict[str, bool]]]:
    events = {}

    for recipe in craftable_recipes:
        machines = machines_by(can_be_placed_on=surface, crafting_category=recipe.category)

        if len(machines) == 0:
            continue

        if len(machines_for_manual_craft.intersection((machine.name for machine in machines))) > 0:
            events[f'Craft {recipe.name}'] = (
                UnlockedRecipe(recipe)
                    & All([CanCraft(item_name, surface) for item_name in recipe.ingredients]),
                {product_name: False for product_name in recipe.products},
            )

        events[f'Automate {recipe.name} crafting'] = (
            UnlockedRecipe(recipe)
                & Any([CanCraft(machine.name, surface) for machine in machines])
                & All([CanAutomate(item_name, surface) for item_name in recipe.ingredients]),
            {product_name: True for product_name in recipe.products},
        )

    return events
