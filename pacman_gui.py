import sys
import pygame
from pygame.locals import *

from pacman import Pacman as Pacman
from my_logger import make_logger

logger = make_logger(__name__)


class PacmanGUI(Pacman):
    def __init__(self,map_id):
        super().__init__(map_id)
        self.GS = 32  # pixel size
        self.anim_cycle = 6
        self.fps = 60
        self.screen = None
        self.clock = None
        self.image_dict = None
        self.agent_direction = 's'

    def run(self, debug=True):
        self.init_game()
        frame = 0
        is_done = False
        while not is_done:
            action = None
            dirty_rects = []
            self.clock.tick(self.fps)
            frame += 1
            pose_id = int(frame/self.anim_cycle) % 2
            dirty = self.draw_agent(None, pose_id)
            dirty_rects.append(dirty)
            for e in pygame.event.get():
                if e.type == QUIT:
                    pygame.quit()
                    sys.exit(1)
                if e.type == KEYDOWN:
                    if e.key == K_ESCAPE:
                        sys.exit(1)
                    if e.key == K_RIGHT or e.key == K_e:
                        self.agent_direction = 'e'
                        action = 0
                    if e.key == K_LEFT or e.key == K_w:
                        self.agent_direction = 'w'
                        action = 1
                    if e.key == K_DOWN or e.key == K_s:
                        self.agent_direction = 's'
                        action = 2
                    if e.key == K_UP or e.key == K_n:
                        self.agent_direction = 'n'
                        action = 3
            if action is not None:
                _, _, is_done, info = self.step(action)
                if info['is_movable']:
                    dirties = self.draw_move(action)
                    dirty_rects.extend(dirties)
                if info['is_catched']:
                    logger.info('GAME OVER!!')
                    pygame.quit()
                    sys.exit(1)
                for enemy in self.enemies:
                    action = enemy.get_action(self.agent_pos)
                    if action is not None:
                        _, _, _, info = self.step(action, enemy)
                        if info['is_movable']:
                            dirties = self.draw_move(action, enemy)
                            dirty_rects.extend(dirties)
                        if info['is_catched']:
                            logger.info('GAME OVER!!')
                            pygame.quit()
                            sys.exit(1)
                if debug:
                    self.render()
            pygame.display.update(dirty_rects)
        logger.info('Game is solved at step {}.'.format(self.n_step))

    def init_game(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.map_w*self.GS, self.map_h*self.GS))
        pygame.display.set_caption('Sokoban')
        self.clock = pygame.time.Clock()
        self.load_images()
        self.reset()
        self.draw_init_map()
        pygame.display.update()

    def draw_init_map(self):
        # draw map
        for y, row in enumerate(self.init_map):
            for x, d in enumerate(row):
                self.screen.blit(self.image_dict[d], (x*self.GS, y*self.GS))
        # overwrite the coin
        for y, row in enumerate(self.init_coins):
            for x, d in enumerate(row):
                if d == 1:
                    self.screen.blit(self.image_dict[2], (x*self.GS, y*self.GS))

    def draw_agent(self, enemy, pose_id):
        direction = {'e': 1, 'w': 2, 's': 3, 'n': 4}
        if enemy is None:  # player agent
            agent_pos = self.agent_pos
            if pose_id == 0:
                agent_img = self.pacman_images[0]
            else:
                agent_img = self.pacman_images[direction[self.agent_direction]]
        else:
            agent_pos = enemy.get_pos()
            agent_img = self.image_dict[enemy.eid]
        self.screen.blit(agent_img, (agent_pos[0]*self.GS, agent_pos[1]*self.GS))
        return pygame.Rect(agent_pos[0]*self.GS, agent_pos[1]*self.GS, self.GS, self.GS)

    def draw_move(self, action, enemy=None):
        dirty_rects = []
        if enemy is None:
            agent_pos = self.agent_pos
        else:
            agent_pos = enemy.get_pos()
        # previous position
        map_mid = int(self.map_h/2)
        if agent_pos[0] == 0 and agent_pos[1] == map_mid and action == 0:
            prev_pos = [self.map_w-1, map_mid]
        elif agent_pos[0] == self.map_w-1 and agent_pos[1] == map_mid and action == 1:
            prev_pos = [0, map_mid]
        else:
            prev_pos = [agent_pos[0] - self.moves[action][0],
                        agent_pos[1] - self.moves[action][1]]
        if self.coins[prev_pos[1]][prev_pos[0]] == 1:
            img_id = 2  # coin
        else:
            img_id = self.tile_dict['floor']
        self.screen.blit(self.image_dict[img_id],(prev_pos[0]*self.GS, prev_pos[1]*self.GS))
        dirty_rects.append(pygame.Rect(prev_pos[0]*self.GS, prev_pos[1]*self.GS,
                                       self.GS, self.GS))

        # current position
        if enemy is None:
            img_id = self.tile_dict['agent']
        else:
            img_id = enemy.eid
        self.screen.blit(self.image_dict[img_id],
                         (agent_pos[0]*self.GS, agent_pos[1]*self.GS))
        dirty_rects.append(pygame.Rect(agent_pos[0]*self.GS, agent_pos[1]*self.GS,
                                       self.GS, self.GS))
        return dirty_rects

    def load_image(self, img_file, colorkey=None):
        try:
            image = pygame.image.load(img_file).convert()
        except pygame.error:
            logger.error('Image NOT FOUND : {}'.format(img_file))
            raise SystemExit
        if colorkey is -1:
            colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.locals.RLEACCEL)
        return image, image.get_rect()

    def split_pacman_image(self, img):
        pacman_images = []
        for i in range(5):
            surface = pygame.Surface((self.GS, self.GS))
            surface.blit(img, (0,0), (self.GS*i, 0, self.GS, self.GS))
            colorkey = surface.get_at((0,0))
            surface.set_colorkey(colorkey, pygame.locals.RLEACCEL)
            surface.convert()
            pacman_images.append(surface)  # [close,e,w,s,n]
        return pacman_images
    
    def load_images(self):
        floor_img, _ = self.load_image('./image/floor.png')
        coin_img, _ = self.load_image('./image/coin.png')
        warp_img, _ = self.load_image('./image/warp.gif')
        wall_img, _ = self.load_image('./image/wall4.gif')
        pac, _ = self.load_image('./image/pac.png')
        pac_e, _ = self.load_image('./image/pac_e.png')
        pac_w, _ = self.load_image('./image/pac_w.png')
        pac_s, _ = self.load_image('./image/pac_s.png')
        pac_n, _ = self.load_image('./image/pac_n.png')
        self.pacman_images = [pac, pac_e, pac_w, pac_s, pac_n]
        pacman_img = self.pacman_images[1]
        enemy1, _ = self.load_image('./image/enemy1.gif')
        enemy2, _ = self.load_image('./image/enemy2.gif')
        enemy3, _ = self.load_image('./image/enemy3.gif')
        enemy4, _ = self.load_image('./image/enemy4.gif')
        self.image_dict = {0: floor_img, 1: wall_img, 2: coin_img, 3: warp_img, 4:pacman_img,
                           5: enemy1, 6: enemy2, 7:enemy3, 8:enemy4}

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--map', action='store', type=int, default=0)
    args = parser.parse_args()

    game = PacmanGUI(args.map)
    game.run()
