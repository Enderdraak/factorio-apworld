from dataclasses import dataclass

from rule_builder.rules import And, False_, Has, HasAny, Or, Rule, True_

from ..config import game_name
from ..data.classes import get_name, Recipe, SpaceLocation, Surface, Technology
from ..data.lookup import technologies_by
from ..data.raw import recipes_unlocked_at_start, space_locations, technologies
from ..data.utils import upgrades_levels, upgrades_map
from .productions.event import get_production_item_name


@dataclass()
class All(Rule['FactorioWorld'], game=game_name):
    rules: list[Rule]

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if len(self.rules) == 0:
            return True_().resolve(world)

        return And(*self.rules).resolve(world)


@dataclass()
class Any(Rule['FactorioWorld'], game=game_name):
    rules: list[Rule]

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if len(self.rules) == 0:
            return False_().resolve(world)

        return Or(*self.rules).resolve(world)


@dataclass()
class HasTechnology(Rule['FactorioWorld'], game=game_name):
    technology_name: str

    def __init__(self, technology: Technology|str):
        super().__init__()
        self.technology_name = get_name(technology)

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if self.technology_name in upgrades_map:
            item_name = upgrades_map[self.technology_name]
            level = upgrades_levels[item_name].index(technologies[self.technology_name]) + 1

            return Has(item_name, level).resolve(world)
        else:
            return Has(self.technology_name).resolve(world)


@dataclass()
class UnlockedMiningWithFluid(Rule['FactorioWorld'], game=game_name):
    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        return Any([HasTechnology(technology) for technology in technologies_by(unlock_mining_with_fluid=True)]).resolve(world)


@dataclass()
class UnlockedRecipe(Rule['FactorioWorld'], game=game_name):
    recipe_name: str

    def __init__(self, recipe: Recipe|str):
        super().__init__()
        self.recipe_name = get_name(recipe)

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if self.recipe_name in recipes_unlocked_at_start:
            return True_().resolve(world)

        technologies = technologies_by(unlock_recipe=self.recipe_name)

        if len(technologies) == 0:
            raise Exception(f'No technology unlocks recipe "{self.recipe_name}"')

        if world.options.split_technologies:
            technologies = [technology for technology in technologies if technology.name in upgrades_map]

        return (Has(f'recipe: {self.recipe_name}') | Any([HasTechnology(technology) for technology in technologies])).resolve(world)


@dataclass()
class UnlockedSpaceLocation(Rule['FactorioWorld'], game=game_name):
    space_location_name: str

    def __init__(self, space_location: SpaceLocation|str):
        super().__init__()
        self.space_location_name = get_name(space_location)

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if space_locations[self.space_location_name].unlocked_at_start:
            return True_().resolve(world)

        technologies = technologies_by(unlock_space_location=self.space_location_name)

        if len(technologies) == 0:
            raise Exception(f'No technology unlocks space location "{self.space_location_name}"')

        if world.options.split_technologies:
            technologies = [technology for technology in technologies if technology.name in upgrades_map]

        return (Has(f'space location: {self.space_location_name}') | Any([HasTechnology(technology) for technology in technologies])).resolve(world)


@dataclass()
class CanAutomate(Rule['FactorioWorld'], game=game_name):
    item_name: str
    surface_name: str

    def __init__(self, item: str, surface: Surface|str):
        super().__init__()
        self.item_name = item
        self.surface_name = get_name(surface)

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        return Has(get_production_item_name(self.surface_name, self.item_name, True)).resolve(world)


@dataclass()
class CanCraft(Rule['FactorioWorld'], game=game_name):
    item_name: str
    surface_name: str

    def __init__(self, item: str, surface: Surface|str):
        super().__init__()
        self.item_name = item
        self.surface_name = get_name(surface)

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        return HasAny(
            get_production_item_name(self.surface_name, self.item_name, True),
            get_production_item_name(self.surface_name, self.item_name, False),
        ).resolve(world)
