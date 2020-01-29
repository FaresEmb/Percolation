import random

import pygame
from pygame.locals import *


class Tree:
   BURNED = 0
   BURNING = 1
   ALIVE = 2
   WATER = 3
   def __init__(self):
       self.state = self.ALIVE
   def __repr__(self):
       s = {self.BURNED:'BURNED', self.BURNING:'BURNING', self.ALIVE:'ALIVE'}[self.state]
       return '<Tree ' + s + '>'

class World:
   def __init__(self, s, p, d):
       self.map = [list([Tree() for i in range(s)]) for j in range(s)]
       self.burning = []
       self.new_burning = []
       self.burned = []
       self.water = []

       laclength = 100
       lacdepth = 50
       x = random.randint(int(laclength/2), len(self.map) - 1 - int(laclength/2))
       y = random.randint(int(lacdepth/2), len(self.map) - int(lacdepth/2) - 1)
       for i in range(int(x - laclength / 2), int(x + laclength / 2)):
           for j in range(int(y - lacdepth / 2), int(y + lacdepth / 2)):
               self.water.append((i, j))
               self.map[i][j].state = Tree.WATER
       for i in range(int(d*s*s)):
           if not self.map[x][y].state == Tree.WATER:
               x = random.randint(0,len(self.map)-1)
               y = random.randint(0, len(self.map)-1)
               self.burned.append((x,y))
               self.map[x][y].state = Tree.BURNED
           else:
               i -= 1


           self.burned.append((x, y))
           self.map[x][y].state = Tree.BURNED

       self.there_is_fire = False

       self.nb_init_alive = s ** 2 - int(d * s) - laclength*lacdepth
       self.nb_alive = s ** 2 - int(d*s) - laclength*lacdepth
       self.nb_burned = 0

       self.surface = pygame.Surface((s,s))
       self.surface.fill((0,255,0))

       self.font = pygame.font.Font(None,24)
       self.txt = None

       self.p = p
       self.s = s
       self.d = d
       self.d2 = d - (self.nb_burned/(s ** 2))

   def fire_on(self, pos):
       x,y = pos
       if x<0 or x>=len(self.map) or y<0 or y>=len(self.map):
           return
       if self.map[x][y].state is not Tree.ALIVE:
           return
       self.map[x][y].state = Tree.BURNING
       if not self.there_is_fire:
           self.burning = [(x,y)]
           self.there_is_fire = True
           self.nb_burned = 0

       self.nb_burned += 1
       self.new_burning.append((x,y))

   def on_update(self):
       if not self.there_is_fire:
           self.d2 = self.d - (self.nb_burned / (self.s ** 2))
           self.txt = self.font.render("{} % d'arbres brûlés".format(round(self.nb_burned/self.nb_alive * 100, 2)), \
                                       True, (0,0,0), (50,200,255))
           self.txt2 = self.font.render("{} % d'arbres sur la map".format(round(self.d2 * 100, 2)), \
                                       True, (0, 0, 0), (50, 200, 255))
           return
       elif self.txt:
           self.txt = None
       elif self.txt2:
           self.txt2 = None
       self.there_is_fire = False

       self.new_burning = []

       #self.surface.fill((0,255,0))
       burner = lambda : random.random() < self.p

       for x,y in self.burned:
           self.surface.set_at((x,y),(0,0,0))

       for x, y in self.water:
           self.surface.set_at((x, y), (0, 0, 255))

       self.burned = []

       for x,y in self.burning:
           self.there_is_fire = True
           self.surface.set_at((x,y), (255,0,0))

           self.map[x][y].state = Tree.BURNED

           up = burner()
           down = burner()
           left = burner()
           right = burner()
           if up:
               self.fire_on((x,y+1))
           if down:
               self.fire_on((x,y-1))
           if left:
               self.fire_on((x-1,y))
           if right:
               self.fire_on((x+1,y))

           self.burned.append((x,y))
       self.burning = self.new_burning[:]

   def on_render(self,dst):
       dst.blit(self.surface, (0,0))
       if self.txt:
           dst.blit(self.txt, (0,24))
       if self.txt2:
           dst.blit(self.txt2, (0, 48))

class App:
   def __init__(self):
       self.window = pygame.display.set_mode((512, 512))
       self.running = False

       self.world = World(512, 0.5,0.4)


       self.font = pygame.font.Font(None, 24)


       self.menu2 = self.font.render("Click to Start !", \
                                    True, (0, 0, 0), (50, 200, 255))
       self.menu = self.font.render("Appuyez sur 'R' pour ré-initialiser la simulation.", \
                                    True, (0,0,0),(50,200,255))


       self.clock= pygame.time.Clock()

   def on_event(self, e):
       if e.type == QUIT:
           self.running = False
       elif e.type == MOUSEBUTTONDOWN:
           self.world.fire_on(e.pos)
       elif e.type == KEYDOWN:
           if e.key == K_r:
               p = self.world.p
               d = self.world.d
               self.world = World(512,p,d)
           elif e.key == K_LEFT:
               self.world.p -= 0.1
               if self.world.p < 0:
                   self.world.p = 0
           elif e.key == K_RIGHT:
               self.world.p += 0.1
               if self.world.p > 1:
                   self.world.p = 1

   def on_render(self):
       self.world.on_render(self.window)
       if not self.world.there_is_fire:
           prob_txt = "Probabilité : < {} >".format(str(round(self.world.p,2)))
           prob = self.font.render(prob_txt, True, (0,0,0), (50,200,255))
           x = (self.window.get_width() - self.menu.get_width()) // 2
           y = (self.window.get_height() - self.menu.get_height()) // 2
           self.window.blit(self.menu,(x,y))
           x = (self.window.get_width() - self.menu2.get_width()) // 2
           self.window.blit(self.menu2, (x, y-50))
           x = (self.window.get_width() - prob.get_width()) // 2
           y += 1.2 * self.menu.get_height()
           self.window.blit(prob, (x,y))

   def on_update(self):
       self.world.on_update()

   def on_mainloop(self):
       self.running = True

       while self.running:
           for e in pygame.event.get():
               self.on_event(e)
           self.on_update()
           self.on_render()
           pygame.display.flip()
           #pygame.display.set_caption(str(round(self.clock.get_fps(),2))+" FPS")
           self.clock.tick(10)

if __name__ == "__main__":
   pygame.init()
   a = App()
   a.on_mainloop()
   pygame.quit()