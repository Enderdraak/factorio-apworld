import dataclasses
import pprint

import data.classes
import data.raw

printer = pprint.PrettyPrinter(width=1000000)

def format_value(value):
    if dataclasses.is_dataclass(value):
        return f'{value.__class__.__name__}({', '.join(map(format_value, dataclasses.asdict(value).values()))})'

    return printer.pformat(value)

def print_data(name):
    value = getattr(data.raw, name)

    print('')
    if isinstance(value, data.classes.Table):
        print(f'{name} = Table()')
        for item in value:
            print(f'{name}.add({format_value(item)})')
    else:
        print(f'{name} = {format_value(value)}')


print('from .classes import Machine, Recipe, SpaceLocation, Surface, SurfaceCondition, Table, Technology')
print_data('surfaces')
print_data('surfaces_accessible_at_start')
print_data('space_locations')
print_data('machines')
print_data('machines_available_at_start')
print_data('recipes')
print_data('recipes_unlocked_at_start')
print_data('science_packs')
print_data('technologies')
print_data('items')
