from .raw_base import *

# Keep only space platform surface
for surface in surfaces:
    if not surface.name == 'space-platform':
        del surfaces[surface.name]

surfaces_accessible_at_start.clear()
surfaces_accessible_at_start.add('space-platform')

# Removed machines
del machines['character']
del machines['steel-furnace']

# Starting machines
machines_for_manual_craft.clear()
machines_for_manual_craft.add('assembling-machine-1')
machines_for_manual_craft.add('asteroid-collector')
machines_for_manual_craft.add('crusher')
machines_for_manual_craft.add('electric-furnace')

# Can't be crafted because one of their ingredient doesn't exist
del recipes['tesla-turret']

# Space platform is automaticaly unlocked on game start
recipes_unlocked_at_start.update(technologies['space-platform'].unlocked_recipes)
del technologies['space-platform']

# Removed technologies
_removed_technologies = [
    # Technologies explicitely removed by platformer
    'heavy-armor',
    'battery-equipment',
    'belt-immunity-equipment',
    'night-vision-equipment',
    'modular-armor',
    'solar-panel-equipment',
    'toolbelt',
    'mining-productivity-1',
    'mining-productivity-2',
    'mining-productivity-3',
    'flamethrower',
    'defender',
    'follower-robot-count-1',
    'follower-robot-count-2',
    'follower-robot-count-3',
    'follower-robot-count-4',
    'follower-robot-count-5',
    'refined-flammables-1',
    'refined-flammables-2',
    'refined-flammables-3',
    'refined-flammables-4',
    'refined-flammables-5',
    'refined-flammables-6',
    'refined-flammables-7',
    'energy-shield-equipment',
    'exoskeleton-equipment',
    'personal-roboport-equipment',
    'worker-robots-speed-1',
    'worker-robots-speed-2',
    'worker-robots-speed-3',
    'worker-robots-speed-4',
    'worker-robots-speed-5',
    'worker-robots-speed-6',
    'worker-robots-speed-7',
    'braking-force-1',
    'braking-force-2',
    'braking-force-3',
    'braking-force-4',
    'braking-force-5',
    'braking-force-6',
    'braking-force-7',
    'construction-robotics',
    'power-armor',
    'worker-robots-storage-1',
    'worker-robots-storage-2',
    'worker-robots-storage-3',
    'discharge-defense-equipment',
    'personal-laser-defense-equipment',
    'distractor',
    'battery-mk2-equipment',
    'battery-mk3-equipment',
    'fission-reactor-equipment',
    'electric-weapons-damage-1',
    'electric-weapons-damage-2',
    'electric-weapons-damage-3',
    'electric-weapons-damage-4',
    'destroyer',
    'power-armor-mk2',
    'logistic-system',
    'personal-roboport-mk2-equipment',
    'energy-shield-mk2-equipment',
    'cliff-explosives',
    'mech-armor',
    'tree-seeding',
    'toolbelt-equipment',
    'fish-breeding',
    'spidertron',
    'fusion-reactor-equipment',
    'foundation',
    'health',
    'artillery-shell-speed-1',
    'artillery-shell-damage-1',
    'artillery-shell-range-1',
    'artillery',
    'logistic-robotics',
    'rocket-silo',
    # Technologies pruned by platformer because they have no remaining modifiers
    'advanced-material-processing',
    'advanced-material-processing-2',
    'artificial-soil',
    'asteroid-reprocessing',
    'automobilism',
    'big-mining-drill',
    'biter-egg-handling',
    'electric-mining-drill',
    'flammables',
    'laser',
    'lightning-collector',
    'military',
    'military-3',
    'military-4',
    'modules',
    'overgrowth-soil',
]

for technology_name in _removed_technologies:
    del technologies[technology_name]

# Technologies that are not removed by platformer but gives useless bonuses
_useless_technologies = [
    'steel-axe',
    'rail-support-foundations',
    'rocket-part-productivity',
]

for technology_name in _useless_technologies:
    technologies[technology_name].modifiers = []

# Make modules non-upgrades
technologies['efficiency-module'].upgrade = False
technologies['efficiency-module-2'].upgrade = False
technologies['efficiency-module-3'].upgrade = False
technologies['productivity-module'].upgrade = False
technologies['productivity-module-2'].upgrade = False
technologies['productivity-module-3'].upgrade = False
technologies['quality-module'].upgrade = False
technologies['quality-module-2'].upgrade = False
technologies['quality-module-3'].upgrade = False
technologies['speed-module'].upgrade = False
technologies['speed-module-2'].upgrade = False
technologies['speed-module-3'].upgrade = False

# Cap productivity infine techs
technologies['asteroid-productivity'].max_level = 30
technologies['low-density-structure-productivity'].max_level = 30
technologies['plastic-bar-productivity'].max_level = 30
technologies['processing-unit-productivity'].max_level = 30
technologies['rocket-fuel-productivity'].max_level = 30
technologies['scrap-recycling-productivity'].max_level = 30
technologies['steel-plate-productivity'].max_level = 30
