import dataclasses
import typing

@dataclasses.dataclass
class Base:
    name: str

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'

    def __hash__(self):
        return hash(self.name)


def get_name(value: Base|str) -> str:
    if isinstance(value, Base):
        return value.name
    else:
        return value


class Table:
    data: dict[str, Base]

    def __init__(self):
        self.data = {}

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key: str):
        return self.data[key]

    def __delitem__(self, key: str):
        del self.data[key]

    def __contains__(self, key: str):
        return key in self.data

    def __iter__(self):
        return map(lambda name: self.data[name], sorted(self.data.keys()))

    def add(self, item: Base):
        self.data[item.name] = item


@dataclasses.dataclass
class Resource:
    name: str


@dataclasses.dataclass
class PumpableResource(Resource):
    '''Resources that can be pumped by an offshore pump (ex: water)'''
    fluid: str


@dataclasses.dataclass
class GatherableResource(Resource):
    '''Resources that can be gathered by the character (ex: rocks)'''
    results: dict[str, int|float]


@dataclasses.dataclass
class MinableResource(Resource):
    '''Ressurces that can be mined by a mining drill (ex: iron)'''
    category: str
    results: dict[str, int|float]
    mining_fluid: str|None = None


@dataclasses.dataclass
class Surface(Base):
    properties: dict[str, float]
    resources: list[Resource] = dataclasses.field(default_factory=list)

    @property
    def is_space_platform(self) -> bool:
        return self.name == 'space-platform'


@dataclasses.dataclass
class SpaceLocation(Base):
    asteroid_chunks: set[str] = dataclasses.field(default_factory=set)
    connections: set[str] = dataclasses.field(default_factory=set)
    unlocked_at_start: bool = False
    accessible_at_start: bool = False


@dataclasses.dataclass
class SurfaceCondition:
    property: str
    min: float | None
    max: float | None

    def accept(self, surface: Surface) -> bool:
        self.accept_value(surface.properties[self.property])

    def accept_value(self, value: float) -> bool:
        if self.min is not None and value < self.min:
            return False

        if self.max is not None and value > self.max:
            return False

        return True


@dataclasses.dataclass
class Machine(Base):
    surface_conditions: list[SurfaceCondition] = dataclasses.field(default_factory=list)
    crafting_categories: set[str] = dataclasses.field(default_factory=set)
    mining_categories: set[str] = dataclasses.field(default_factory=set)
    is_offshore_pump: bool = False
    is_asteroid_collector: bool = False

    def can_be_placed_on(self, surface: Surface) -> bool:
        return all(map(lambda surface_condition: surface_condition.accept(surface), self.surface_conditions))


@dataclasses.dataclass
class Recipe(Base):
    category: str
    ingredients: dict[str, int]
    products: dict[str, int | float] # int means an exact value, float an average
    time: float

    def __init__(self, name: str, category: str, ingredients: dict[str, int], products: dict[str, int | float], time: float):
        super().__init__(name)
        self.category = category
        self.ingredients = ingredients
        self.products = products
        self.time = time


@dataclasses.dataclass
class Technology(Base):
    upgrade: bool = False
    max_level: int | None | typing.Literal['infinite'] = None
    unlocked_qualities: set[str] = dataclasses.field(default_factory=set)
    unlocked_recipes: set[str] = dataclasses.field(default_factory=set)
    unlocked_space_locations: set[str] = dataclasses.field(default_factory=set)
    modifiers: list[str] = dataclasses.field(default_factory=list)
    unit_count: int | None = None

    @property
    def has_modifier(self):
        return any((
            len(self.unlocked_qualities) > 0,
            len(self.unlocked_recipes) > 0,
            len(self.unlocked_space_locations) > 0,
            len(self.modifiers) > 0,
        ))
