from dataclasses import dataclass

from schema import Schema, Optional, And, Or, SchemaError

from Options import Choice, DefaultOnToggle, OptionCounter, OptionDict, OptionSet, PerGameCommonOptions, Range, Toggle, Visibility

from ..config import craftsanity_filter, items_required_for_automation, victory_conditions
from ..data.raw import items, science_packs
from .items.pool import upgrades_default_count, upgrades_min_count, upgrades_max_count
from .locations import craftsanity_item_pool


# schema helpers
class FloatRange:
    def __init__(self, low, high):
        self._low = low
        self._high = high

    def validate(self, value) -> float:
        if not isinstance(value, (float, int)):
            raise SchemaError(f"should be instance of float or int, but was {value!r}")
        if not self._low <= value <= self._high:
            raise SchemaError(f"{value} is not between {self._low} and {self._high}")
        return float(value)


class SchemaRange:
    def __init__(self, low, high):
        self.low = low
        self.high = high

    def validate(self, value):
        if self.low is not None and value < self.low:
            raise SchemaError(f"{value} should be higher than {self.low}")
        if self.high is not None and value > self.high:
            raise SchemaError(f"{value} should be lower than {self.high}")
        return value


LuaBool = Or(bool, And(int, lambda n: n in (0, 1)))


class MaxSciencePack(Choice):
    """Maximum level of science pack required to complete the game."""
    display_name = "Maximum Required Science Pack"
    default = len(science_packs) - 1

    def get_allowed_packs(self):
        return {option.replace("_", "-") for option, value in self.options.items() if value <= self.value}

MaxSciencePack.options = {name: index for index, name in enumerate(science_packs)}
MaxSciencePack.name_lookup = {option_id: option_name for option_name, option_id in MaxSciencePack.options.items()}


class MinTechCost(Range):
    """The cheapest a Technology can be in Science Packs."""
    display_name = "Minimum Science Pack Cost"
    range_start = 1
    range_end = 10000
    default = 5


class MaxTechCost(Range):
    """The most expensive a Technology can be in Science Packs."""
    display_name = "Maximum Science Pack Cost"
    range_start = 1
    range_end = 10000
    default = 500


class TechCostDistribution(Choice):
    """Random distribution of costs of the Science Packs.
    Even: any number between min and max is equally likely.
    Low: low costs, near the minimum, are more likely.
    Middle: medium costs, near the average, are more likely.
    High: high costs, near the maximum, are more likely."""
    display_name = "Tech Cost Distribution"
    option_even = 0
    option_low = 1
    option_middle = 2
    option_high = 3


class TechCostMix(Range):
    """Percent chance that a preceding Science Pack is also required.
    Chance is rolled per preceding pack."""
    display_name = "Science Pack Cost Mix"
    range_end = 100
    default = 70


class RampingTechCosts(Toggle):
    """Forces the amount of Science Packs required to ramp up with the highest involved Pack. Average is preserved."""
    display_name = "Ramping Tech Costs"


class TechTreeInformation(Choice):
    """How much information should be displayed in the tech tree.
    None: No indication of what a research unlocks.
    Advancement: Indicates if a research unlocks an item that is considered logical advancement, but not who it is for.
    Full: Labels with exact names and recipients of unlocked items; all researches are prefilled into the !hint command.
    """
    display_name = "Technology Tree Information"
    option_none = 0
    option_advancement = 1
    option_full = 2
    default = 2


class Goal(Choice):
    """Goal required to complete the game."""
    display_name = "Goal"
    default = 0

    def get_victory_condition(self):
        return victory_conditions[self.value]

Goal.options = {victory_condition['name']: index for index, victory_condition in enumerate(victory_conditions)}
Goal.name_lookup = {option_id: option_name for option_name, option_id in Goal.options.items()}

if len(victory_conditions) == 1:
    Goal.visibility = Visibility.none


class CraftSanity(Range):
    """Choose a number of researches to require crafting a specific item rather than with science packs.
    May be increased to add technologies/recipes needed for the first science pack
    May be capped based on the total number of locations."""
    display_name = "CraftSanity"
    default = 0
    range_start = 0
    range_end = len(craftsanity_item_pool)


class SplitTechnologies(Toggle):
    """Split technologies into individual recipes instead of awarding them as a whole"""
    display_name = "Split technologies"


class Progressive(DefaultOnToggle):
    """Merges together some technologies into progressive items which awards them in order.
    Upgrades and are always progressive."""
    display_name = "Progressive Technologies"


class FactorioUpgradesCount(OptionDict):
    """Number of upgrade levels added to the item pool."""
    display_name = "Upgrades counts"
    default = {
        key: default
        for key, default in upgrades_default_count.items()
        if upgrades_min_count[key] != upgrades_max_count[key]
    }
    schema = Schema({
        Optional(key): And(int, SchemaRange(upgrades_min_count[key], upgrades_max_count[key]))
        for key in upgrades_default_count.keys()
        if upgrades_min_count[key] != upgrades_max_count[key]
    })

    def __getitem__(self, item: str) -> int:
        return self.value.get(item, upgrades_default_count[item])


class FactorioStartItems(OptionCounter):
    """Mapping of Factorio internal item-name to amount granted on start."""
    display_name = "Starting Items"
    valid_keys = items
    min = 0


class FreeSamples(Choice):
    """Get free items with your technologies."""
    display_name = "Free Samples"
    option_none = 0
    option_single_craft = 1
    option_half_stack = 2
    option_stack = 3
    default = 3


class FreeSamplesQuality(Choice):
    """If free samples are on, determine the quality of the granted items.
    Requires the quality mod, which is part of the Space Age DLC. Without it, normal quality is given."""
    display_name = "Free Samples Quality"
    option_normal = 0
    option_uncommon = 1
    option_rare = 2
    option_epic = 3
    option_legendary = 4
    default = 0


class FactorioFreeSampleBlacklist(OptionSet):
    """Set of items that should never be granted from Free Samples"""
    display_name = "Free Sample Blacklist"
    valid_keys = items


class FactorioFreeSampleWhitelist(OptionSet):
    """Overrides any free sample blacklist present. This may ruin the balance of the mod, be warned."""
    display_name = "Free Sample Whitelist"
    valid_keys = items


class WorldGen(OptionDict):
    """World Generation settings. Overview of options at https://wiki.factorio.com/Map_generator,
    with in-depth documentation at https://lua-api.factorio.com/latest/concepts/MapGenSettings.html"""
    display_name = 'World Generation'
    value: dict[str, dict]
    default = {}
    schema = Schema({
        'basic': {
            Optional('autoplace_controls'): {
                str: {
                    'frequency': FloatRange(0, 6),
                    'size': FloatRange(0, 6),
                    'richness': FloatRange(0.166, 6)
                }
            },
            Optional('seed'): Or(None, And(int, lambda n: n >= 0)),
            Optional('width'): And(int, lambda n: n >= 0),
            Optional('height'): And(int, lambda n: n >= 0),
            Optional('starting_area'): FloatRange(0.166, 6),
            Optional('peaceful_mode'): LuaBool,
            Optional('no_enemies_mode'): LuaBool,
            Optional('cliff_settings'): {
                'name': str, 'cliff_elevation_0': FloatRange(0, 99),
                'cliff_elevation_interval': FloatRange(0.066, 241),  # 40/frequency
                'richness': FloatRange(0, 6)
            },
            Optional('property_expression_names'): Schema({
                Optional('control-setting:moisture:bias'): FloatRange(-0.5, 0.5),
                Optional('control-setting:moisture:frequency:multiplier'): FloatRange(0.166, 6),
                Optional('control-setting:aux:bias'): FloatRange(-0.5, 0.5),
                Optional('control-setting:aux:frequency:multiplier'): FloatRange(0.166, 6),
                Optional(str): object  # allow overriding all properties
            }),
        },
        'advanced': {
            Optional('pollution'): {
                Optional('enabled'): LuaBool,
                Optional('diffusion_ratio'): FloatRange(0, 0.25),
                Optional('ageing'): FloatRange(0.1, 4),
                Optional('enemy_attack_pollution_consumption_modifier'): FloatRange(0.1, 4),
                Optional('min_pollution_to_damage_trees'): FloatRange(0, 9999),
                Optional('pollution_restored_per_tree_damage'): FloatRange(0, 9999)
            },
            Optional('enemy_evolution'): {
                Optional('enabled'): LuaBool,
                Optional('time_factor'): FloatRange(0, 1000e-7),
                Optional('destroy_factor'): FloatRange(0, 1000e-5),
                Optional('pollution_factor'): FloatRange(0, 1000e-7),
            },
            Optional('enemy_expansion'): {
                Optional('enabled'): LuaBool,
                Optional('max_expansion_distance'): FloatRange(2, 20),
                Optional('settler_group_min_size'): FloatRange(1, 20),
                Optional('settler_group_max_size'): FloatRange(1, 50),
                Optional('min_expansion_cooldown'): FloatRange(3600, 216000),
                Optional('max_expansion_cooldown'): FloatRange(18000, 648000)
            }
        }
    })

    def __init__(self, value: dict):
        advanced = {'pollution', 'enemy_evolution', 'enemy_expansion'}
        self.value = {
            'basic': {k: v for k, v in value.items() if k not in advanced},
            'advanced': {k: v for k, v in value.items() if k in advanced}
        }

        # verify min_values <= max_values
        def optional_min_lte_max(container, min_key, max_key):
            min_val = container.get(min_key, None)
            max_val = container.get(max_key, None)
            if min_val is not None and max_val is not None and min_val > max_val:
                raise ValueError(f'{min_key} can\'t be bigger than {max_key}')

        enemy_expansion = self.value['advanced'].get('enemy_expansion', {})
        optional_min_lte_max(enemy_expansion, 'settler_group_min_size', 'settler_group_max_size')
        optional_min_lte_max(enemy_expansion, 'min_expansion_cooldown', 'max_expansion_cooldown')

    @classmethod
    def from_any(cls, data: dict):
        if type(data) == dict:
            return cls(data)
        else:
            raise NotImplementedError(f'Cannot Convert from non-dictionary, got {type(data)}')


@dataclass
class FactorioOptions(PerGameCommonOptions):
    max_science_pack: MaxSciencePack
    min_tech_cost: MinTechCost
    max_tech_cost: MaxTechCost
    tech_cost_distribution: TechCostDistribution
    tech_cost_mix: TechCostMix
    ramping_tech_costs: RampingTechCosts
    tech_tree_information: TechTreeInformation
    goal: Goal
    craftsanity: CraftSanity
    split_technologies: SplitTechnologies
    progressive: Progressive
    upgrades_count: FactorioUpgradesCount
    starting_items: FactorioStartItems
    free_samples: FreeSamples
    free_samples_quality: FreeSamplesQuality
    free_sample_blacklist: FactorioFreeSampleBlacklist
    free_sample_whitelist: FactorioFreeSampleWhitelist
    world_gen: WorldGen

    def apply_required_adjustments(self):
        self.craftsanity.value = max(self.craftsanity.value, len(items_required_for_automation(self)))
