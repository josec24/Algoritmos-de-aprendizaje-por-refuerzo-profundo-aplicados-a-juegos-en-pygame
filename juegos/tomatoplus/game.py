import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

#Inicializador de pygame
pygame.init()
#Fuente usada
font = pygame.font.Font('fuente/arial.ttf', 25)

#Dirección del player
class Direccion(Enum):
    RIGHT = 1
    LEFT = 2

#Punto (x,y)
Point = namedtuple('Point', 'x, y')

# Colores
WHITE = (255, 255, 255)
FONDO=(52, 152, 219)

#Tamaño de paso
tam_bloque = 20
#Velocidad
velocidad = 40

#Imagen del pajaro
playerImg = pygame.image.load('imagenes/tomato/player.png')
manzanaImg = pygame.image.load('imagenes/tomato/manzana.png')
#Imagen tubo
tuboImg = pygame.image.load('imagenes/tomato/roca.png')
pastoImg = pygame.image.load('imagenes/tomato/pasto.png')
# Parámetros de imágenes
playerW=60
playerH=60
tuboW=100
tuboH=450
# Redimencionando imágenes
playerImg = pygame.transform.scale(playerImg, (playerW, playerH))
manzanaImg = pygame.transform.scale(manzanaImg, (20, 20))
tuboImg = pygame.transform.scale(tuboImg, (tuboW, tuboH))

#Clase flappy bird
class TomatoPlusGame:
    def __init__(self, w=640, h=480):
        #Ancho y alto del display
        self.w = w
        self.h = h
        self.lim='abajo'
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('tomatoPlus')
        self.tiempo = pygame.time.Clock()
        self.reinicio()


    #Reiniciar juego
    def reinicio(self):
        # Estado inicial
        self.direccion= Direccion.LEFT
        
        #Posición inicial del pajaro
        self.player = Point(self.w/2-200, self.h-100)

        #Inicio de parámetros
        self.puntos = 0
        self.comida = None
        #tubo
        self.tubo = None
        self._pos_tubo()

        self._pos_comida()
        self.frame_iteracion = 0

    #Definiendo la posición de la comida
    def _pos_comida(self):
        x = random.randrange(60, 600,20)
        y = self.h-100
        self.comida = Point(x, y)
        if self.comida in self.player:
            self._pos_comida()

    #Definiendo posición del tubo
    def _pos_tubo(self):
        x = self.w+10
        y = random.randint(-450, -10)
        self.tubo = Point(x, y)
        if self.tubo in self.player:
            self._pos_tubo()

    def jug(self,pt=None):
        if pt is None:
            pt = self.player
        if pt.x>self.w-100:
            x=self.w-100
            self.player = Point(x, pt.y)
        if pt.x<100:
            self.player = Point(100, pt.y)

    #mover tubo
    def mover_tubo(self,mover):
        self.mover=mover
        if self.tubo.x<-50:
            x=self.w+50
            y = random.randint(-450, -10)
        else:
            x=self.tubo.x+mover
            y=self.tubo.y
        self.tubo = Point(x, y)

    def tubo_lim(self,pt=None):
        if self.lim==None:
            self.lim='abajo'

        if self.tubo.y>=-10:

            self.lim='arriba'

        if self.tubo.y<=-450:
            self.lim='abajo'

        if self.lim=='abajo':
            y=self.tubo.y+20
            self.tubo = Point(self.tubo.x, y)
        elif self.lim=='arriba':
            y=self.tubo.y-20
            self.tubo = Point(self.tubo.x, y)


    def paso_juego(self, acc):
        self.frame_iteracion += 1
        
        accion=[0,0]
        if acc==0:
            accion=[1,0]
        if acc==1:
            accion=[0,1]

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # Mover según la acción
        self._mover(accion)

        
        # Verificar si acabó el juego
        recompensa = 0
        game_over = False
        if self.is_collision() :
            game_over = True
            recompensa = -10
            return recompensa, game_over, self.puntos

        # Si pasa entre los tubos(verifica el el player este a la derecha de la manzana)
        # if self.player.y > self.comida.y-20 and self.player.y < self.comida.y+20 and self.player.x > self.comida.x:
        if self.player.x>self.comida.x-30 and self.player.x<self.comida.x+30:
            self.puntos += 1
            recompensa = 5
            self._pos_comida()

        # Actualizar ui y tiempo
        self._update_ui()
        self.jug()
        self.tubo_lim()
        self.tiempo.tick(velocidad)
        # Devuelve el game_over y puntos
        return recompensa, game_over, self.puntos

    def getTime(self):
        return pygame.time.get_ticks()/1000

    #Comprueba si existe colisión
    def is_collision(self, pt=None):
        self.colis=0
        if pt is None:
            pt = self.player
        # Si colisiona con el límite
        if pt.y > self.h - playerH or pt.y < 0:
            return True

        #Si colisioa con el tubo inferior
        if (pt.x <self.tubo.x+tuboW and pt.x >self.tubo.x-playerW and pt.y >self.tubo.y-playerH/2 and pt.y <self.tubo.y+tuboH-30):
            return True

        #Si no colisiona devuelve False
        return False

    #Actualizar pantalla
    def _update_ui(self):
        self.display.fill(FONDO)
        
        #dibujando en lapantalla
        self.display.blit(playerImg, (self.player.x, self.player.y))

        self.display.blit(manzanaImg, (self.comida.x, self.comida.y))
        
        self.display.blit(pastoImg, (0, 432))
        
        #Movimiento
        self.mover_tubo(-15)
        self.display.blit(tuboImg, (self.tubo.x, self.tubo.y))
        #Dibujar puntuación
        text = font.render("Puntuacion: " + str(self.puntos), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _mover(self, accion):
        #Movimiento: [arriba, abajo]

        #Para calcular la nueva dirección
        clock_wise = [Direccion.LEFT, Direccion.RIGHT]
        idx = clock_wise.index(self.direccion)
        
        if np.array_equal(accion, [1, 0]):
            nueva_dir = clock_wise[idx] #no cambia
        else:
            siguiente_idx = (idx + 1) % 2
            nueva_dir = clock_wise[siguiente_idx]  # [0,1]

        self.direccion= nueva_dir

        x = self.player.x
        y = self.player.y

        #Dirección
        if self.direccion== Direccion.LEFT:
            x += tam_bloque
        elif self.direccion== Direccion.RIGHT:
            x -= tam_bloque

        self.player = Point(x, y)

    #Obtene estado del entorno
    def get_state(self):
        #Se definen las entradas de la red neuronal
        player = self.player
        point_l = Point(player.x-20, player.y)
        point_r = Point(player.x+20, player.y)
        
        dir_r = self.direccion== Direccion.RIGHT
        dir_l = self.direccion== Direccion.LEFT

        #Parámetros del estado
        estado = [
            # peligros al ir recto
            (dir_r and self.is_collision(point_r)) or 
            (dir_l and self.is_collision(point_l)),


            # peligros de ir en contra
            (dir_r and self.is_collision(point_l)) or 
            (dir_l and self.is_collision(point_r)),
            
            # Mover a la dirección
            dir_r,
            dir_l,
            
            # localización de la comida
            self.comida.x < self.player.x,  # comida la izquierda
            self.comida.x > self.player.x,  # comida a la derecha
            self.comida.y < self.player.y,  # comida arriba
            self.comida.y > self.player.y  # comida abajo
            ]

        return np.array(estado, dtype=int)