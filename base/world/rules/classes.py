from dataclasses import dataclass

from rule_builder.rules import And, False_, Has, HasAny, Or, Rule, True_

from ...config import game_name
from ...data.classes import SpaceLocation, Surface
from ...data.raw import machines_available_at_start, recipes_unlocked_at_start, space_locations, surfaces, technologies
from ...data.utils import recipes_by_product, technologies_by_recipe_unlocked, technologies_by_space_location_unlocked, upgrades_map, upgrades_levels


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
class HasMachine(Rule['FactorioWorld'], game=game_name):
    machine_name: str
    surface_name: str

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if self.machine_name in machines_available_at_start:
            return True_().resolve(world)
        else:
            return CanCraft(self.machine_name, self.surface_name).resolve(world)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(machine={self.machine_name}, surface={self.surface_name})"


@dataclass()
class CanCraft(Rule['FactorioWorld'], game=game_name):
    item_name: str
    surface_name: str | None = None

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        events = []

        for recipe in recipes_by_product(self.item_name):
            for surface in [surfaces[self.surface_name]] if self.surface_name is not None else surfaces:
                events.append(f'Craft {recipe.name} on {surface.name}')

        return HasAny(*events).resolve(world)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(item={self.item_name}, surface={self.surface_name})"


@dataclass()
class CanAutomate(Rule['FactorioWorld'], game=game_name):
    item_name: str
    surface_name: str | None = None

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        events = []

        for recipe in recipes_by_product(self.item_name):
            for surface in [surfaces[self.surface_name]] if self.surface_name is not None else surfaces:
                events.append(f'Automate {recipe.name} on {surface.name}')

        return HasAny(*events).resolve(world)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(item={self.item_name}, surface={self.surface_name})"


@dataclass()
class HasTechnology(Rule['FactorioWorld'], game=game_name):
    name: str

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        technology = technologies[self.name]

        if technology.name in upgrades_map:
            item_name = upgrades_map[technology.name]
            level = upgrades_levels[item_name].index(technology) + 1

            return Has(item_name, level).resolve(world)
        else:
            return Has(technology.name).resolve(world)


@dataclass()
class UnlockedRecipe(Rule['FactorioWorld'], game=game_name):
    name: str

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if self.name in recipes_unlocked_at_start:
            return True_().resolve(world)

        technologies = technologies_by_recipe_unlocked(self.name)

        if len(technologies) == 0:
            raise Exception(f'No technology unlocks recipe "{self.name}"')

        if world.options.split_technologies:
            technologies = [technology for technology in technologies if technology.name in upgrades_map]

        return (Has(f'{self.name} recipe') | Any([HasTechnology(technology.name) for technology in technologies])).resolve(world)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"


@dataclass()
class UnlockedSpaceLocation(Rule['FactorioWorld'], game=game_name):
    name: str

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if space_locations[self.name].unlocked_at_start:
            return True_().resolve(world)

        technologies = technologies_by_space_location_unlocked(self.name)

        if len(technologies) == 0:
            raise Exception(f'No technology unlocks space location "{self.name}"')

        return Any([HasTechnology(technology.name) for technology in technologies]).resolve(world)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"


class ReachedSpaceLocation(Rule['FactorioWorld'], game=game_name):
    space_location_name: str
    surface_name: str

    def __init__(self, space_location: SpaceLocation | str, surface: Surface | str):
        super().__init__()
        self.space_location_name = space_location.name if isinstance(space_location, SpaceLocation) else space_location
        self.surface_name = surface.name if isinstance(surface, Surface) else surface

    def _instantiate(self, world: 'FactorioWorld') -> Rule.Resolved:
        if space_locations[self.space_location_name].accessible_at_start:
            return True_().resolve(world)

        return Has(f'Reach {self.space_location_name} with {self.surface_name}').resolve(world)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(space_location={self.space_location_name}, surface={self.surface_name})"
