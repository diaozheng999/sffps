import random


class Player(object):

    def propose(self, hand):
        return random.randint(0, len(hand)-1)
    
    def vote(self, legislations):
        p = random.randint(0, len(legislations))
        if p == len(legislations):
            if random.random() > 0.5:
                p += random.randint(0, 4)
            else:
                p = -1
        return p

    def select_legislation(self, legislations):
        return random.choice(legislations)