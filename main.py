import copy
from sffps.game_manager import GameManager
import cards
from sffps.player import Player

n_trials = 10000


with open('output1.csv', 'w') as f:
    f.write('trial,turn,ENV,ECO,INF,HAP\n')
    for i in xrange(n_trials):
        game = GameManager(4, 10)
        
        q_dist = cards.get_legislation_distribution()

        q = []
        for card in cards.get_legislation_cards():
            if card.name in q_dist:
                n = q_dist[card.name]
            else:
                n = q_dist['*']
            q += [card] * n


        p = cards.get_event_cards()

        game.set_deck(p, q)
        game.set_players([Player() for _ in xrange(4)])

        #1/0
        while not game.is_game_over:        
            game.next_turn()
            f.write('%d,%d'%(i, game.turn_count))
            for v in game.get_resource():
                f.write(',%d'%v)
            f.write('\n')