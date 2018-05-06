
class Card(object):
    def __init__(self, name, desc, actions, tags=None):
        self.name = name
        self.desc = desc
        self.tags = set(tags) if tags else set()
        self.type = None
        try:
            for a in actions:
                a.set_card(self)
            self.actions = actions
        except:
            actions.set_card(self)
            self.actions = [actions]
    
    def __repr__(self):
        return "<%s card \"%s\" %sEffects: %r>"%(
            self.type,
            self.name,
            "Tags: [%s] "%(','.join(self.tags)) if self.tags else '',
            self.actions
        )


class Legislation(Card):
    def __init__(self, name, desc, actions, precond=None, tags=None):
        super(Legislation, self).__init__(name, desc, actions, tags)
        self.type = 'Legislation'
        self.precond = precond

    def __repr__(self):
        if self.precond:
            return "<%s card \"%s\" %sEffects: %r Precondition: %r>"%(
            self.type,
            self.name,
            "Tags: [%s] "%(','.join(self.tags)) if self.tags else '',
            self.actions,
            self.precond
        )
        return super(Legislation, self).__repr__()
        

class Building(Legislation):
    def __init__(self, name, desc, actions, precond=None, tags=None):
        super(Building, self).__init__(name, desc, actions, precond, tags)
        self.tags.add("Building")

class Specialization(Legislation):
    def __init__(self, name, desc, actions, precond=None, tags=None):
        super(Specialization, self).__init__(name, desc, actions, precond, tags)
        self.tags.add("Specialization")

class Event(Card):
    def __init__(self, name, desc, actions, tags=None):
        super(Event, self).__init__(name, desc, actions, tags)
        self.type = 'Event'

class Disaster(Event):
    def __init__(self, name, desc, actions, tags=None):
        super(Disaster, self).__init__(name, desc, actions, tags)
        self.tags.add("Disaster")

class Holiday(Event):
    def __init__(self, name, desc, actions, tags=None):
        super(Holiday, self).__init__(name, desc, actions, tags)
        self.tags.add("Holiday")    