from sffps.card import Building, Legislation, Event, Holiday, Disaster, Specialization
from sffps.check import *
from sffps.actions import *
from sffps.resources import *

class Holiday_(Holiday):
    def __init__(self, name, desc, check, tags=None):
        super(Holiday_, self).__init__(name, desc, 
            [If(Enacted('Celebrate Public Holiday.') & check, 
                ResourceUpdate([(HAPPINESS, 1), (ECONOMY, -1)])),
             If(~Enacted('Celebrate Public Holiday.'),
                ResourceUpdate([(HAPPINESS, -1)]))
            ], tags)


def get_legislation_cards():
    return [
        Building (
            "Build a Wall.",
            "",
            ResourceUpdate([(ECONOMY, -1), (INFRASTRUCTURE, +1)])
        ),
        Building(
            "Build a Mosque.",
            "",
            [
                ResourceUpdate([(ECONOMY, -1)]),
                If(~(Enacted("Build a Church.") | Enacted("Religious Harmony.")),
                    ResourceUpdate([(HAPPINESS, 1)]))
            ]
        ),
        Building(
            "Build a Church.",
            "",
            [
                ResourceUpdate([(ECONOMY, -1)]),
                If(~(Enacted("Build a Mosque.") | Enacted("Religious Harmony.")),
                    ResourceUpdate([(HAPPINESS, 1)]))
            ]
        ),
        Building(
            "Build a Fire Station.",
            "",
            [
                ResourceUpdate([(ECONOMY, -1), (INFRASTRUCTURE, +1)])
            ]
        ),
        Legislation(
            "Religious Harmony.",
            "",
            [
                WhenEnacted(
                    ["Build a Church.", "Build a Mosque."],
                    ResourceUpdate([(HAPPINESS, 1)])
                )
            ],
            ~Enacted("Build a Church.") | Enacted("Build a Mosque.")
        ),
        Legislation(
            "Emission Regulation.",
            "",
            ResourceUpdate([(ENVIRONMENT, 1), (ECONOMY, -1)])
        ),
        Legislation(
            "Building Codes.",
            "",
            Action()
        ),
        Legislation(
            "Increase Taxes.",
            "",
            WhenPresent([(ECONOMY, 1), (HAPPINESS, -1)])
        ),
        Legislation(
            "Decrease Taxes.",
            "",
            WhenPresent([(ECONOMY, -1), (HAPPINESS, 1)])
        ),
        Legislation(
            "Promote Zero-Emission Vehicles.",
            "",
            WhenPresent([(ENVIRONMENT, 1), (ECONOMY, -1)])
        ),
        Legislation(
            "Cut Transportation Budget.",
            "",
            WhenPresent([(ENVIRONMENT, 1), (ECONOMY, 1), (INFRASTRUCTURE, -1)])
        ),
        Legislation(
            "Promote Local Businesses.",
            "",
            WhenPresent([(ECONOMY, -1)])
        ),
        Legislation(
            "Promote Large Corporations.",
            "",
            WhenPresent([(ECONOMY, -1)])
        ),
        Legislation(
            "Global Veganism.",
            "",
            WhenPresent([(HAPPINESS, -1), (ENVIRONMENT, 1)])
        ),
        Specialization(
            "Sharia Laws.",
            "",
            [
                ForEach(Repeal(), cards=['Religious Harmony.', 'Build a Church.']),
                ForEach(Repeal(), tag='Specialization', no_self=True),
                WhenEnacted('Build a Church.', ResourceUpdate([(HAPPINESS, -3)])),
                EachTurn(If(NumEnacted('Build a Mosque.', 2), ResourceUpdate([(INFRASTRUCTURE, 1)])))
            ],
            precond = Resource([(HAPPINESS, '>=', 8)]) & Enacted('Build a Mosque.')
        ),
        Specialization(
            "Papal Primacy.",
            "",
            [
                ForEach(Repeal(), cards=['Religious Harmony.', 'Build a Mosque.']),
                ForEach(Repeal(), tag='Specialization', no_self=True),
                WhenEnacted('Build a Mosque.', ResourceUpdate([(HAPPINESS, -3)])),
                EachTurn(If(NumEnacted('Build a Church.', 2), ResourceUpdate([(INFRASTRUCTURE, 1)])))
            ],
            precond = Resource([(HAPPINESS, '>=', 8)]) & Enacted('Build a Mosque.')
        ),
        Specialization(
            "Sustainable Energy Hub.",
            "",
            [
                ForEach(Repeal(), tag='Specialization', no_self=True),
                EachTurn(ResourceUpdate([(ECONOMY, 1)]))
            ],
            precond = Resource([(ENVIRONMENT, '>=', 8), (INFRASTRUCTURE, '>=', 6)])
        ),
        Specialization(
            "Knoxville Stock Exchange.",
            "",
            [
                ForEach(Repeal(), tag='Specialization', no_self=True),
                EachTurn(If(Resource([(ECONOMY, '>=', 5), (INFRASTRUCTURE, '>=', 5)]),
                    ResourceUpdate([(HAPPINESS, 1)])))
            ],
            precond = Resource([(ECONOMY, '>=', 8)])
        ),
        Specialization(
            "Certified Green Spaces.",
            "",
            [
                ForEach(Repeal(), tag='Specialization', no_self=True),
                EachTurn(ResourceUpdate([(ENVIRONMENT, 1)]))
            ],
            precond = Resource([(INFRASTRUCTURE, '>=', 8)]) & NumTagEnacted('Building', 2)
        ),
        Legislation(
            "Celebrate Public Holiday.",
            "",
            Action()
        ),
        Legislation(
            "Photosynthetic Clothes.",
            "",
            WhenPresent([(ENVIRONMENT, 1)])
        ),
        Building(
            "Federal Highway.",
            "",
            WhenPresent([(INFRASTRUCTURE, 1)])
        ),
        Building(
            "Start a Local Business.",
            "",
            If(Enacted("Promote Local Businesses."), ResourceUpdate([(ECONOMY, 1)])),
            tags=['Business']
        ),
        Building(
            "Found a Large Corporation.",
            "",
            If(Enacted("Promote Large Corporations."), ResourceUpdate([(ECONOMY, 2), (HAPPINESS, -1)])),
            tags=['Business']
        ),
        Legislation(
            "Repeal",
            "",
            SelectLegislation(Repeal())
        ),
        Legislation(
            "Promote Steel Production.",
            "",
            WhenPresent([(ECONOMY, 1), (ENVIRONMENT, -1)])
        ),
        Legislation(
            "Strip Mining.",
            "",
            [
                ResourceUpdate([(ENVIRONMENT, -2)]),
                WhenPresent([(ECONOMY, 3)])
            ]
        )
    ]


def get_event_cards():
    return [
        Disaster(
            "Flood.", 
            "",
            If(Resource([(ENVIRONMENT, '<=', 5)]) & ~Enacted('Build a Wall.'),
            ResourceUpdate([(INFRASTRUCTURE, -1), (HAPPINESS, -1), (ECONOMY, -1)]))
        ),
        Event(
            "Gas shortage.",
            "",
            [
                ResourceUpdate([(ECONOMY, -1), (HAPPINESS, -1)]),
                If(~Enacted("Promote Zero-emission Vehicles."),
                    ResourceUpdate([(INFRASTRUCTURE, -1)]))
            ]
        ),
        Event(
            "High unemployment rate.",
            "",
            If(Resource([(ECONOMY, '<=', 5)]), ResourceUpdate([(HAPPINESS, -1)]))
        ),
        Event(
            "Recession.",
            "",
            If(Resource([(ECONOMY, '<=', 6)]), 
                ResourceUpdate([(ECONOMY, -2), (HAPPINESS, -2)]),
                ResourceUpdate([(ECONOMY, -2)]))
        ),
        Event(
            "A factory decided to set up in town.",
            "",
            If(Enacted("Emission Regulation."), 
                ResourceUpdate([(ECONOMY, 1)]),
                ResourceUpdate([(ECONOMY, 2), (ENVIRONMENT, -1)]))
        ),
        Event(
            "Graffiti on Church/Mosque.",
            "",
            If(~Enacted("Religious Harmony."),
                ForEach(ResourceUpdate([(HAPPINESS, -1)]), tags=["Religious", "Building"]))
        ),
        Disaster(
            "Earthquake.",
            "",
            [
                ResourceUpdate([(INFRASTRUCTURE, -1), (HAPPINESS, -1), (ECONOMY, -1)]),
                If(~Enacted("Building Codes."), ForEach(Repeal(), tag='Building'))
            ]
        ),
        Event(
            "Gentrification.",
            "",
            ForEach(ResourceUpdate([(HAPPINESS, -1), (ECONOMY, +1)]), tag='Building')
        ),
        Disaster(
            "Highway collapsed.",
            "",
            If(Resource([(INFRASTRUCTURE, '<=', 4)]) & Enacted("Cut Transportation Budget."),
                ResourceUpdate([(INFRASTRUCTURE, -1), (ECONOMY, -1), (HAPPINESS, -1)]),
                ResourceUpdate([(INFRASTRUCTURE, -1)]))
        ),
        Event(
            "Freedom-con.",
            "",
            If(Enacted("Cut Transportation Budget."),
                ResourceUpdate([(INFRASTRUCTURE, -2), (HAPPINESS, -2), (ECONOMY, -2)]),
                ResourceUpdate([(ECONOMY, 1), (HAPPINESS, 1)]))
        ),
        Disaster(
            "Riot.",
            "",
            If(Resource([(HAPPINESS, '<=', 5)]), 
                ResourceUpdate([(ECONOMY, -1), (INFRASTRUCTURE, -1)]))
        ),
        Event(
            "Charity drive.",
            "",
            If(Enacted("Build a Church.") | Enacted("Build a Mosque."),
                ResourceUpdate([(HAPPINESS, 1)]),
                ResourceUpdate([(HAPPINESS, -1)]))
        ),
        Holiday_(
            "Earth day.", "", Resource([(ENVIRONMENT, '>=', 7)])
        ),
        Holiday_(
            "Easter.", "", Enacted('Build a Church.')
        ),
        Holiday_(
            "Eid-al-Fitr.", "", Enacted('Build a Mosque.')
        ),
        Holiday_(
            "Free burgers for everyone.", "", ~Enacted('Global Veganism.')
        ),
        Disaster(
            'Wrath of God.',
            '',
            If (~(Enacted('Sharia Laws.') & Enacted('Papal Primacy.')), 
                SetResource([(INFRASTRUCTURE, 2), (ECONOMY, 2), (HAPPINESS, 2)]))
        ),
        Event(
            'Reset',
            '',
            [
                SetResource([(ENVIRONMENT, 5), (ECONOMY, 5), (INFRASTRUCTURE, 5), (HAPPINESS, 5)]),
                ResetHand()
            ]
        ),
        Disaster(
            'Forest Fire',
            '',
            If(Enacted('Build a Fire Station.'),
                ResourceUpdate([(ENVIRONMENT, -1)]),
                ResourceUpdate([(ENVIRONMENT, -1), (ECONOMY, -1), (INFRASTRUCTURE, -1), (HAPPINESS, -1)]))
        )
    ]
'''
    ),

    Event(
        'Free Trees.',
        '',
        ResourceUpdate([(ENVIRONMENT, 1)])
    ),
    Event(
        'Free Roads.',
        '',
        ResourceUpdate([(INFRASTRUCTURE, 1)])
    ),
    Event(
        'Free Money.',
        '',
        ResourceUpdate([(ECONOMY, 1)])
    ),
    Event(
        'Free Hugs.',
        '',
        ResourceUpdate([(HAPPINESS, 1)])
'''