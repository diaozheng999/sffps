import game_manager

class Action(object):
    def __init__(self):
        self.game_manager = game_manager.GameManager.instance

    def set_card(self, card):
        pass

    def invoke(self):
        pass

    def __repr__(self):
        return "<None>"


class ResourceUpdate(Action):
    def __init__(self, updates):
        super(ResourceUpdate, self).__init__()
        self.updates = updates

    def invoke(self):
        self.game_manager.resources.update(self.updates)

    def __repr__(self):
        return "ResourceUpdate(%s)"%(
            self.game_manager.resources.repr_values(self.updates)
        )


class SetResource(Action):
    def __init__(self, values):
        super(SetResource, self).__init__()
        self.values = values

    def invoke(self):
        self.game_manager.resources.set_value(self.values)

    def __repr__(self):
        return "SetResource(%s)"%(
            self.game_manager.resources.repr_values(self.values, False)
        )


class If(Action):
    def __init__(self, check, true, false=None):
        super(If, self).__init__()
        self.check = check
        self.true = true
        self.false = false

    def invoke(self):
        if self.check.check():
            self.true.invoke()
        elif self.false:
            self.false.invoke()
    def __repr__(self):
        if self.false:
            return "If %r Then %r Else %r"%(self.check, self.true, self.false)
        else:
            return "If %r Then %r"%(self.check, self.true)

class Trigger(Action):
    def __init__(self, action):
        super(Trigger, self).__init__()
        self.trigger = None
        self.action = action

    def invoke(self):
        self.trigger.append(self.action)

class TriggerRemove(Action):
    def __init__(self, trigger, action):
        super(TriggerRemove, self).__init__()
        self.trigger = trigger
        self.action = action

    def invoke(self):
        self.trigger.remove(self.action)

class WhenRepealed(Trigger):
    def __init__(self, card, action):
        super(WhenRepealed, self).__init__(action)
        self.trigger = self.game_manager.get_legislation_repealed_trigger(card)

class OnTurnStart(Trigger):
    def __init__(self, action):
        super(OnTurnStart, self).__init__(action)
        self.trigger = self.game_manager.turn_start_trigger

class EachTurn(Action):
    def __init__(self, action):
        super(EachTurn, self).__init__()
        self.on_turn_start = OnTurnStart(action)
        self.remove_trigger = TriggerRemove(
            self.game_manager.turn_start_trigger, 
            action)
        self.action = action
        self.when_repealed = None

    def set_card(self, card):
        self.when_repealed = WhenRepealed(card, self.remove_trigger)

    def invoke(self):
        if not self.when_repealed:
            raise "Card not set"
        else:
            self.on_turn_start.invoke()
            self.when_repealed.invoke()

    def __repr__(self):
        return "EachTurn(%r)"%(self.action)

class WhenPresent(Action):
    def __init__(self, resource_updates):
        self.up_delta = resource_updates
        self.down_delta = [(a, -b) for a,b in resource_updates]
        self.up_action = ResourceUpdate(self.up_delta)
        self.down_action = ResourceUpdate(self.down_delta)
        self.triggered = None

    def set_card(self, card):
        self.triggered = WhenRepealed(card, self.down_action)

    def invoke(self):
        if not self.triggered:
            raise "Card not set"
        else:
            self.up_action.invoke()
            self.triggered.invoke()
    
    def __repr__(self):
        return "WhenPresent(%s)"%(
            self.up_action.game_manager.resources.repr_values(self.up_delta)
        )

class SequentialAction(Action):
    def __init__(self, actions):
        super(SequentialAction, self).__init__()
        self.actions = actions

    def invoke(self):
        for action in self.actions:
            action.invoke()

    def __repr__(self):
        return "<%s>"%(', '.join(repr(r) for r in self.actions))

class WhenEnacted(Action):
    def __init__(self, cards, action):
        super(WhenEnacted, self).__init__()

        if isinstance(cards, basestring):
            cards = [cards]

        self.cards = cards
        self.enact_triggers = []
        for card in cards:
            self.enact_triggers.append(
                self.game_manager.get_legislation_enacted_trigger(card)
            )

        self.up_action = []
        self.down_action = []
        self.action = action

        for trigger in self.enact_triggers:
            up_action = Trigger(action)
            up_action.trigger = trigger
            self.up_action.append(up_action)
            self.down_action.append(
                TriggerRemove(trigger, action)
            )
    
    def set_card(self, card):
        self.when_repealed = WhenRepealed(card, SequentialAction(self.down_action))

    def invoke(self):
        if not self.when_repealed:
            raise "Card not set"
        else:
            for action in self.up_action:
                action.invoke()
            self.when_repealed.invoke()
    
    def __repr__(self):
        return "WhenEnacted(%r) Do %r"%(self.cards, self.action)
    
class ForEach(Action):
    def __init__(self, action, tag=None, tags=None, card=None, cards=None, no_self=False):
        super(ForEach, self).__init__()
        self.check_tags = None
        self.check_names = None
        if not (tag or tags or card or cards):
            raise "Empty check set."
        if tags:
            self.check_tags = tags
        elif tag:
            self.check_tags = [tag]
        elif cards:
            self.check_names = cards
        elif card:
            self.check_names = [card]
        self.action = action
        self.no_self = no_self

    def set_card(self, card):
        self.self = card


    def invoke_on(self, card):
        if self.no_self and card.name == self.self.name:
            return
        if self.check_tags:
            if not card.tags:
                return
            for t in self.check_tags:
                if t not in card.tags:
                    return
            self.action.set_card(card)
            self.action.invoke()
        elif card.name in self.check_names:
            self.action.set_card(card)
            self.action.invoke()

    def invoke(self):
        for card in self.game_manager.legislations:
            self.invoke_on(card)

    def __repr__(self):
        if self.check_tags:
            chk_str = "Tag=%r"%self.check_tags
        else:
            chk_str = "Card=%r"%self.check_names
        if self.no_self:
            chk_str += ' NoSelf'
        return "ForEach %s Do %r"%(chk_str, self.action)

class Repeal(Action):
    def __init__(self):
        super(Repeal, self).__init__()

    def set_card(self, card):
        self.card = card
    
    def invoke(self):
        if not self.card:
            raise "Card not set"
        self.game_manager.repeal(self.card)

    def __repr__(self):
        return "Repeal"

class ResetHand(Action):
    def __init__(self):
        super(ResetHand, self).__init__()

    def invoke(self):
        self.game_manager.reset_hand()

    def __repr__(self):
        return "ResetHand"

class SelectLegislation(Action):
    def __init__(self, action):
        super(SelectLegislation, self).__init__()
        self.action = action

    def invoke(self):
        card = self.game_manager.select_legislation()
        self.action.set_card(card)
        self.action.invoke()

    def __repr__(self):
        return "With Selected Legislation Do %r"%self.action