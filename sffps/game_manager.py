import resources
import random


class GameManager(object):
    instance = None

    def __init__(self, n_players, n_rounds, block_all_legislations=False, block_all_events=False):
        GameManager.instance = self
        self.resources = resources.Resources(self, [5,5,5,5], 0, 10)

        self.legislations = []
        self.events = []
        self.discarded_legislations = []
        self.repealed_legislations = []

        self.legislation_deck = []
        self.event_deck = []

        self.n_players = n_players
        self.n_rounds = n_rounds
        self.n_hand_size = 5

        ## triggers
        self.turn_start_trigger = []
        self.legislation_enacted_trigger = {}
        self.legislation_repealed_trigger = {}

        self.turn_count = 0
        self.curr_proposer = random.randint(0, n_players-1)

        self.is_game_over = False

        self.block_all_legislations = block_all_legislations
        self.block_all_events = block_all_events

        self.player_hands = [
            [] for _ in xrange(n_players)
        ]

    def get_keyed_trigger(self, trigger, key):
        _key = key if isinstance(key, basestring) else key.name
        if _key not in trigger:
            trigger[_key] = []
        return trigger[_key]

    def get_legislation_repealed_trigger(self, name):
        return self.get_keyed_trigger(self.legislation_repealed_trigger, name)
        
    def get_legislation_enacted_trigger(self, name):
        return self.get_keyed_trigger(self.legislation_enacted_trigger, name)

    def repeal(self, card):
        self.legislations.remove(card)
        self.discarded_legislations.append(card)

        for trigger in self.get_legislation_repealed_trigger(card):
            trigger.invoke()

    def enact(self, card):
        if self.block_all_legislations:
            return

        self.legislations.append(card)

        for action in card.actions:
            action.invoke()

        for trigger in self.get_legislation_enacted_trigger(card):
            trigger.invoke()

    def hand(self, i):
        return self.player_hands[i]

    def reset_hand(self):
        for i in xrange(self.n_players):
            self.discarded_legislations += self.player_hands[i]
            self.player_hands[i] = []

        for i in xrange(self.n_hand_size):
            for j in xrange(self.n_players):
                card = self.legislation_deck[-1]
                self.player_hands[j].append(card)
                del self.legislation_deck[-1]

    def set_deck(self, events, legislations):
        n_event_dups = 0
        while(len(self.event_deck) < self.n_rounds):
            self.event_deck += events
            n_event_dups += 1

        n_legislation_dups = 0
        while(len(self.legislation_deck) < self.n_players * self.n_rounds * self.n_hand_size):    
            self.legislation_deck += legislations
            n_legislation_dups += 1


        print "GameManager: Set %d event card(s) (duplicated %d time(s)), %d legislation card(s) (duplicated %d time(s))."%(
            len(events),
            n_event_dups,
            len(legislations),
            n_legislation_dups)

        print "GameManager: Shuffling and distributing cards..."    
        random.shuffle(self.event_deck)
        random.shuffle(self.legislation_deck)

        self.reset_hand()

    def select_legislation(self):
        return self.players[self.curr_proposer].select_legislation(self.legislations)

    def set_players(self, players):
        self.players = players
        for i in xrange(self.n_players):
            print "Player %d: %s"%(i, self.players[i])

    def next_turn(self):
        self.turn_count += 1
        print "GameManager: Begin turn %d"%self.turn_count
        if len(self.turn_start_trigger) > 0:
            print "GameManager: Process %d trigger(s)"%(len(self.turn_start_trigger))
            for trigger in self.turn_start_trigger:
                trigger.invoke()

        print "GameManager: Current resources: %s"%', '.join("%s:%d"%(resources.RESOURCE_ABBRS[i], self.resources.resources[i]) for i in xrange(4))

        if not self.block_all_events:
            event = self.event_deck[-1]
            self.events.append(event)
            del self.event_deck[-1]
            print "GameManager: Current legislations enacted:"
            for legislation in self.legislations:
                print "\t%s"%legislation.name
                for action in legislation.actions:
                    print '\t\t%r'%action
            if not len(self.legislations):
                print "\t(None)"

            print "GameManager: Drawn %r"%event
            for action in event.actions:
                action.invoke()
            
            print "GameManager: Current resources: %s"%', '.join("%s:%d"%(resources.RESOURCE_ABBRS[i], self.resources.resources[i]) for i in xrange(4))

        proposing_players = (self.curr_proposer, (self.curr_proposer+1)%self.n_players)

        print "GameManager: Player %d and %d propose legislations."%proposing_players
        
        voting_pot = []

        for i in proposing_players:
            self.curr_proposer = i
            lid = self.players[i].propose(self.player_hands[i])
            leg = self.player_hands[i][lid]
            voting_pot.append(leg)
            del self.player_hands[i][lid]
            self.player_hands[i].append(self.legislation_deck[-1])
            del self.legislation_deck[-1]
            print "GameManager: Player %d proposed '%s'"%(i, leg.name)

        print "GameManager: Voting begins."

        votes = []
        majority = self.n_players >> 1
        for i in xrange(self.n_players):
            votes.append(self.players[i].vote(voting_pot))

        tally = [0 for i in xrange(len(voting_pot))]
        for i in xrange(self.n_players):
            v = votes[i]
            if v < 0:
                print "GameManager: Player %d abstained."%i
            elif v >= len(voting_pot):
                rid = v - len(voting_pot)
                discard = self.player_hands[i][rid]
                del self.player_hands[i][rid]
                self.discarded_legislations.append(discard)
                self.player_hands[i].append(self.legislation_deck[-1])
                del self.legislation_deck[-1]
                print "GameManager: Player %d abstained to swap a legislation."%i
            else:
                print "GameManager: Player %d voted for '%s'"%(i, voting_pot[v].name)
                tally[v] += 1

        has_majority = False
        voted_legislation = None
        for i in xrange(len(voting_pot)):
            if tally[i] >= majority:
                if has_majority:
                    has_majority = False
                    break
                else:
                    has_majority = True
                    voted_legislation = voting_pot[i]

        if has_majority:
            if voted_legislation.precond and not voted_legislation.precond.check():
                print "GameManager: Voted legislation '%s' cannot be enacted."%(voted_legislation)
                self.discarded_legislations.append(voted_legislation)
            else:
                print "GameManager: Enacted %r"%voted_legislation
                
                self.enact(voted_legislation)

                print "GameManager: Current resources: %s"%', '.join("%s:%d"%(resources.RESOURCE_ABBRS[i], self.resources.resources[i]) for i in xrange(4))
        else:
            print "GameManager: No majority was reached."

        for legislation in voting_pot:
            if legislation != voted_legislation:
                self.discarded_legislations.append(legislation)

        if self.turn_count > self.n_rounds:
            self.is_game_over = True

    def game_over(self):
        self.is_game_over = True

    def get_resource(self):
        for i in self.resources.resources:
            yield i