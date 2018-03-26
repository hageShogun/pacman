import random
import sys

from my_logger import make_logger

logger = make_logger(__name__)

class Enemy:
    def __init__(self, enemy_id, x, y):
        self.eid = enemy_id  # 5,6,7,8
        self.x = x
        self.y = y
        self.chase_wh = 5  # chasing width and height

    def get_action(self, player_pos):
        if self.eid == 5:  # random type
            action = random.randint(0,3)
        elif self.eid == 6:  # chaes type
            action = self._chase(player_pos)
        elif self.eid == 7 or self.eid == 8:  # wait and chase
            if abs(self.x - player_pos[0]) <= self.chase_wh and abs(self.y - player_pos[1]) <= self.chase_wh:
                logger.debug('Chaising at {},{}.'.format(self.x, self.y))
                action = self._chase(player_pos)
            else:
                action = None
        return action

    def _chase(self, player_pos):
        cand = []
        if self.x < player_pos[0]:
            cand.append(0)  # east
        elif player_pos[0] < self.x:
            cand.append(1)  # west
        if self.y < player_pos[1]:
            cand.append(2)  # south
        elif player_pos[1] < self.y:
            cand.append(3)  # north

        if len(cand) == 0:
            logger.error('Unknown pattern occur.')
            sys.exit(1)
        action = random.choice(cand)
        return action
    
    def get_pos(self):
        return [self.x, self.y]

    def set_pos(self, pos):
        self.x, self.y = pos[0], pos[1]
