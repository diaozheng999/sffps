import game_manager


class Check(object):
    def __init__(self):
        self.game_manager = game_manager.GameManager.instance

    def check(self):
        return True

    def __or__(self, other):
        return Disjunction([self, other])

    def __and__(self, other):
        return Conjunction([self, other])

    def __invert__(self):
        return Negation(self)

class Disjunction(Check):
    def __init__(self, checks):
        super(Disjunction, self).__init__()
        self.checks = checks

    def check(self):
        for check in self.checks:
            if check.check():
                return True
        return False

    def __repr__(self):
        if len(self.checks) == 1:
            return repr(self.checks[0])
        elif len(self.checks) == 2:
            return "(%r | %r)"%(self.checks[0], self.checks[1])
        else:
            return "Or %r"%(self.checks)

class Conjunction(Check):
    def __init__(self, checks):
        super(Conjunction, self).__init__()
        self.checks = checks
    
    def check(self):
        for check in self.checks:
            if not check.check():
                return False
        return True

    def __repr__(self):
        if len(self.checks) == 1:
            return repr(self.checks[0])
        elif len(self.checks) == 2:
            return "(%r & %r)"%(self.checks[0], self.checks[1])
        else:
            return "And %r"%(self.checks)

class Negation(Check):
    def __init__(self, checks):
        super(Negation, self).__init__()
        self.checks = checks

    def check(self):
        return not self.checks.check()

    def __repr__(self):
        return "~%r"%(self.checks)

class Resource(Check):
    def __init__(self, resource_check_list):
        super(Resource, self).__init__()
        self.resource_check_list = resource_check_list

    def check(self):
        return self.game_manager.resources.check(self.resource_check_list)

    def __repr__(self):
        return self.game_manager.resources.repr_checks(self.resource_check_list)

class Card(Check):
    def __init__(self, card_name):
        super(Card, self).__init__()
        self.card_name = card_name
        self.cards = []

    def check(self):
        for card in self.cards:
            if card.name == self.card_name:
                return True
        return False

    def __repr__(self):
        return "CardPresent(\"%s\")"%(self.card_name)

class Tag(Check):
    def __init__(self, tag):
        super(Tag, self).__init__()
        self.tag = tag
        self.cards = []

    def check(self):
        for card in self.cards:
            if self.tag in card.tags:
                return True
        return False

    def __repr__(self):
        return "TagPresent(%s)"%(self.tag)

class CountCard(Check):
    def __init__(self, card_name, min_val, upper=True):
        super(CountCard, self).__init__()
        self.card_name = card_name
        self.min_val = min_val
        self.upper = upper
        self.cards = []

    def check(self):
        count = 0
        for card in self.cards:
            if card.name == self.card_name:
                count += 1
        if self.upper:
            return count >= self.min_val
        return count <= self.min_val

    def __repr__(self):
        return "CardCount(\"%s\") %s %d"%(
            self.card_name, 
            '>=' if self.upper else '<=',
            self.min_val)

class CountTag(Check):
    def __init__(self, tag, min_val, upper=True):
        super(CountTag, self).__init__()
        self.tag = tag
        self.min_val = min_val
        self.upper = upper
        self.cards = []

    def check(self):
        count = 0
        for card in self.cards:
            if self.tag in card.tags:
                count += 1
        if self.upper:
            return count >= self.min_val
        return count <= self.min_val

    def __repr__(self):
        return "TagCount(%s) %s %d"%(
            self.tag, 
            '>=' if self.upper else '<=',
            self.min_val)

class NumEnacted(CountCard):
    def __init__(self, card_name, min_val, upper=True):
        super(NumEnacted, self).__init__(card_name, min_val, upper)
        self.cards = self.game_manager.legislations

class Enacted(Card):
    def __init__(self, card_name):
        super(Enacted, self).__init__(card_name)
        self.cards = self.game_manager.legislations

class TagEnacted(Tag):
    def __init__(self, tag):
        super(TagEnacted, self).__init__(tag)
        self.cards = self.game_manager.legislations

class NumTagEnacted(CountTag):
    def __init__(self, tag, min_val, upper=True):
        super(NumTagEnacted, self).__init__(tag, min_val, upper)
        self.cards = self.game_manager.legislations

class EventCheck(Card):
    def __init__(self, card_name):
        super(EventCheck, self).__init__(card_name)
        self.cards = self.game_manager.events
