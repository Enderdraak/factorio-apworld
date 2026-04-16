game_name = 'Factorio: Platformer'


# Mod dependencies
dependencies = [
    'platformer',
]


# Possible victory conditions
victory_conditions = [
    {
        'type': 'reach-space-location',
        'name': 'reach-solar-system-edge',
        'space_location': 'solar-system-edge',
    },
    {
        'type': 'reach-space-location',
        'name': 'reach-aquilo',
        'space_location': 'aquilo',
    },
]

# Early technologies
def items_required_for_research(options) -> set[str]:
    if options.split_technologies:
        return {'automation-science-pack recipe', 'copper-cable recipe', 'electronic-circuit recipe', 'lab recipe'}
    else:
        return {'automation-science-pack', 'electronics'}

def items_required_for_automation(options) -> set[str]:
    if options.split_technologies:
        return {
            'assembling-machine-1 recipe', 'engine-unit recipe', 'inserter recipe', 'solar-panel recipe',
            'splitter recipe', 'steel-plate recipe', 'underground-belt recipe',
        }
    else:
        return {'automation', 'engine', 'logistics', 'solar-energy', 'steel-processing'}

progressive_items_with_split_technologies = {
    'progressive assembling machine': ['assembling-machine-1 recipe', 'assembling-machine-2 recipe', 'assembling-machine-3 recipe'],
    'progressive circuit': ['electronic-circuit recipe', 'advanced-circuit recipe', 'processing-unit recipe', 'quantum-processor recipe'],
    'progressive combinator': ['constant-combinator recipe', 'arithmetic-combinator recipe', 'decider-combinator recipe', 'selector-combinator recipe'],
    'progressive inserter': ['inserter recipe', 'long-handed-inserter recipe', 'fast-inserter recipe', 'bulk-inserter recipe', 'stack-inserter recipe'],
    'progressive oil processing': ['basic-oil-processing recipe', 'advanced-oil-processing recipe'],
    'progressive quality': ['quality-module', 'epic-quality', 'legendary-quality'],
    'progressive rail': ['rail recipe', 'rail-ramp recipe', 'rail-support recipe'],
    'progressive rail automation': ['train-stop recipe', 'rail-signal recipe', 'rail-chain-signal recipe'],
    'progressive splitter': ['splitter recipe', 'fast-splitter recipe', 'express-splitter recipe', 'turbo-splitter recipe'],
    'progressive train': ['locomotive recipe', 'cargo-wagon recipe', 'fluid-wagon recipe'],
    'progressive transport belt': ['fast-transport-belt recipe', 'express-transport-belt recipe', 'turbo-transport-belt recipe'],
    'progressive underground belt': ['underground-belt recipe', 'fast-underground-belt recipe', 'express-underground-belt recipe', 'turbo-underground-belt recipe'],
    'progressive wall': ['stone-wall recipe', 'gate recipe'],
    # Modules
    'progressive efficiency module': ['efficiency-module recipe', 'efficiency-module-2 recipe', 'efficiency-module-3 recipe'],
    'progressive productivity module': ['productivity-module recipe', 'productivity-module-2 recipe', 'productivity-module-3 recipe'],
    'progressive quality module': ['quality-module recipe', 'quality-module-2 recipe', 'quality-module-3 recipe'],
    'progressive speed module': ['speed-module recipe', 'speed-module-2 recipe', 'speed-module-3 recipe'],
}

progressive_items_without_split_technologies = {
    'progressive automation': ['automation', 'automation-2', 'automation-3'],
    'progressive circuit': ['electronics', 'advanced-circuit', 'processing-unit', 'quantum-processor'],
    'progressive circuit network': ['circuit-network', 'advanced-combinators'],
    'progressive inserter': ['fast-inserter', 'bulk-inserter', 'stack-inserter'],
    'progressive logistics': ['logistics', 'logistics-2', 'logistics-3', 'turbo-transport-belt'],
    'progressive oil processing': ['oil-processing', 'advanced-oil-processing'],
    'progressive railway': ['railway', 'elevated-rail', 'rail-support-foundations'],
    'progressive quality': ['epic-quality', 'legendary-quality'],
    'progressive wall': ['stone-wall', 'gate'],
    # Modules
    'progressive efficiency module': ['efficiency-module', 'efficiency-module-2', 'efficiency-module-3'],
    'progressive productivity module': ['productivity-module', 'productivity-module-2', 'productivity-module-3'],
    'progressive quality module': ['quality-module', 'quality-module-2', 'quality-module-3'],
    'progressive speed module': ['speed-module', 'speed-module-2', 'speed-module-3'],
}

# Item that should be included in craftsanity
def craftsanity_filter(item_name: str):
    return not item_name.endswith('-barrel') and not item_name.endswith('-asteroid-chunk')
