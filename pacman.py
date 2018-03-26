import sys
import random
import copy

from map import Map
from enemy import Enemy
from my_logger import make_logger
from coloring import coloring

logger = make_logger(__name__)


class Pacman:
    def __init__(self, map_id):
        # Constants and parameters
        self.moves = ((1,0), (-1,0), (0,1), (0,-1))  # E,W,S,N
        self.color = ['BLACK', 'WHITE', 'YELLOW', 'YELLOW', 'GREEN',
                      'RED','BLUE','CYAN','PURPLE']
        self.tile_dict = {'floor':0, 'wall':1, 'coin':2, 'yobi':3, 'agent':4,
                          'enemy1':5,'enemy2':6,'enemy3':7,'enemy4':8, }
        self.map_dir = './map_data/'
        # Variables
        self.agent_pos = None
        self.enemies = []
        self.init_map = None
        self.init_coins = None
        self.coins = None
        self.total_coins = 0
        self.n_step = 0
        self.state = None
        self.load_map(map_id)
        self.map_w = len(self.state[0])
        self.map_h = len(self.state)
        self.parse_init_map()
        self.reward_range = [0,1]
        self.observation_space = (self.map_w, self.map_h)

    def reset(self):
        self.state = copy.deepcopy(self.init_map)
        self.coins = copy.deepcopy(self.init_coins)
        return self.state

    def seed(self, seed=None):
        pass

    def render(self):
        sys.stdout.write('STEP={} 0:floor, 1:wall, 2:coin, 3:warp, 4:agent\n'.format(self.n_step))
        for y, row in enumerate(self.state):
            for x, d in enumerate(row):
                if d == self.tile_dict['floor'] and self.coins[y][x] == 1:
                    d = 2
                sys.stdout.write(coloring(str(d), self.color[d]))
            sys.stdout.write('\n')

    def run(self):
        actions = {'e': 0, 'w': 1, 's':2, 'n': 3}
        arrow_keys = {'\x1b[A': 'n','\x1b[B': 's','\x1b[C': 'e','\x1b[D': 'w'}
        is_done = False

        self.reset()
        while not is_done:
            self.render()
            print('Please input action (e/w/s/n/q):')
            action = input()
            if action == '':
                continue
            if (action in arrow_keys.keys()):
                action = arrow_keys[action]
            if (action in 'ewsn'):
                state, reward, is_done, info = self.step(actions[action])
                if not info['is_movable']:
                    logger.info('Given action is not valid ({}).'.format(info['cause']))
                if info['is_catched']:
                    logger.info('GAME OVER!!')
                    sys.exit(1)
            elif action == 'q':
                sys.exit(1)
            else:
                logger.warn('Unknown action ({}) is given.'.format(action))
            # Enemy turn
            for enemy in self.enemies:
                action = enemy.get_action()
                _, _, _, info = self.step(action, enemy)
                if info['is_catched']:
                    logger.info('GAME OVER!!')
                    sys.exit(1)                
        logger.info('Game is solved at step {}'.format(self.n_step))

    def step(self, action, enemy=None):
        self.n_step += 1
        reward = 0
        info = {'is_movable': True, 'is_catched': False}

        if enemy is None:  # Player agent
            cur_pos = self.agent_pos
        else:
            cur_pos = enemy.get_pos()
        logger.debug('current x:{}, y:{}'.format(cur_pos[0],cur_pos[1]))

        # calc next position with considering the warp tile
        map_mid = int(self.map_h/2)
        if cur_pos[0] == 0 and cur_pos[1] == map_mid and action == 1:
            next_pos = [self.map_w-1, map_mid]
        elif cur_pos[0] == self.map_w-1 and cur_pos[1] == map_mid and action == 0:
            next_pos = [0, map_mid]
        else:
            next_pos = [cur_pos[0]+self.moves[action][0], cur_pos[1]+self.moves[action][1]]

        # move check
        if (next_pos[0]<0 or next_pos[1]<0 or
            self.map_w<=next_pos[0] or self.map_h<=next_pos[1]):
            info['is_movable'] = False
            info['cause'] = 'Map boundary over.'
        elif self.init_map[next_pos[1]][next_pos[0]] == self.tile_dict['wall']:
            info['is_movable'] = False
            info['cause'] = 'There is a wall.'
        if not info['is_movable']:
            return (self.state, 0, False, info)

        # move the player or enemy agent
        if (enemy is None) and self.coins[next_pos[1]][next_pos[0]] == 1:
            reward += 1
            self.total_coins -= 1
            self.coins[next_pos[1]][next_pos[0]] = 0
        # update current position
        self.state[cur_pos[1]][cur_pos[0]] = self.tile_dict['floor']
        # update agent or enemy position
        logger.debug('next x:{}, y:{}'.format(next_pos[0],next_pos[1]))
        if enemy is None:
            if self.state[next_pos[1]][next_pos[0]] >= 5:  # enemy
                info['is_catched'] = True
            self.state[next_pos[1]][next_pos[0]] = self.tile_dict['agent']
            self.agent_pos = [next_pos[0], next_pos[1]]
        else:
            if self.state[next_pos[1]][next_pos[0]] == self.tile_dict['agent']:
                info['is_catched'] = True
            self.state[next_pos[1]][next_pos[0]] = enemy.eid
            enemy.set_pos(next_pos)

        if self.is_solved():
            is_done = True
        else:
            is_done = False
            
        return (self.state, reward, is_done, info)

    def is_solved(self):
        if self.total_coins <= 0:
            return True
        else:
            return False

    def load_map(self, map_id):
        map_file = self.map_dir + 'map' + str(map_id) + '.dat'
        logger.info('Load the map file {}.'.format(map_file))
        self.init_map = Map(map_file).init_map
        self.state = copy.deepcopy(self.init_map)        

    def parse_init_map(self):
        self.init_coins = [[0 for _ in range(self.map_w)] for _ in range(self.map_h)]
        for y, row in enumerate(self.init_map):
            for x, d in enumerate(row):
                if d == self.tile_dict['agent']:
                    self.agent_pos = [x,y]
                elif d == self.tile_dict['floor']:
                    self.total_coins += 1
                    self.init_coins[y][x] = 1
                elif d >= self.tile_dict['enemy1']:
                    logger.debug('Enemy(type={}) is generated at {},{}.'.format(d,x,y))
                    enemy = Enemy(d, x, y)
                    self.enemies.append(enemy)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--map', action='store', type=int, default=0)
    args = parser.parse_args()

    game = Pacman(args.map)
    game.run()
