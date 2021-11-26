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
    UP = 1
    DOWN = 2

#Punto (x,y)
Point = namedtuple('Point', 'x, y')

# Colores
WHITE = (255, 255, 255)
FONDO=(52, 152, 219)

#Tamaño de paso
tam_bloque = 15
#Velocidad
velocidad = 40

#Imagen del pajaro
playerImg = pygame.image.load('imagenes/flappy/player.png')
manzanaImg = pygame.image.load('imagenes/flappy/manzana.png')
#Imagen tubo
tuboImg = pygame.image.load('imagenes/flappy/tubo.png')
tuboImg_up = pygame.image.load('imagenes/flappy/tubo_up.png')
# Parámetros de imágenes
playerW=60
playerH=60
tuboW=60
tuboH=300
# Redimencionando imágenes
playerImg = pygame.transform.scale(playerImg, (playerW, playerH))
manzanaImg = pygame.transform.scale(manzanaImg, (20, 20))
tuboImg = pygame.transform.scale(tuboImg, (tuboW, tuboH))
tuboImg_up = pygame.transform.scale(tuboImg_up, (tuboW, tuboH))

#Clase flappy bird
class FlappyBirdGame:
    def __init__(self, w=640, h=480):
        #Ancho y alto del display
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('FlappyBird')
        self.tiempo = pygame.time.Clock()
        self.reinicio()


    #Reiniciar juego
    def reinicio(self):
        # Estado inicial
        self.direccion= Direccion.DOWN
        
        #Posición inicial del pajaro
        self.player = Point(self.w/2-200, self.h/2)

        #Inicio de parámetros
        self.puntos = 0
        self.comida = None
        #tubo
        self.tubo = None
        self._pos_tubo()
        self.tubo_up = None
        self._pos_tubo_up()
        self._pos_comida()
        self.frame_iteracion = 0

    #Definiendo la posición de la comida
    def _pos_comida(self):
        x = self.w+10
        y = self.h+10
        self.comida = Point(x, y)

    #Definiendo posición del tubo
    def _pos_tubo(self):
        x = self.w+10
        y = random.randint(200, 400)
        self.tubo = Point(x, y)
    
    #definiendo posición del tubo superior
    def _pos_tubo_up(self):
        x = self.w+10
        y = random.randint(200, 400)
        self.tubo_up = Point(x, y)
        # print(self.tubo)

    #mover tubo
    def mover_tubo(self,mover):
        self.mover=mover
        if self.tubo.x<-10:
            x=self.w+10
            y=random.randint(200, 400)
        else:
            x=self.tubo.x+mover
            y=self.tubo.y
        self.tubo = Point(x, y)

    #mover tubo de arriba
    def mover_tubo_up(self,mover):
        if self.tubo_up.x<-10:
            x=self.w+10
        else:
            x=self.tubo.x
        y=self.tubo.y-400
        self.tubo_up = Point(x, y)

    #mover manzana(sirve como punto base para ganar puntos)
    def mover_manzana(self,mover):
        x=self.tubo.x
        y=self.tubo.y-60
        self.comida = Point(x, y)

    def paso_juego(self, acc):
        self.frame_iteracion += 1
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # Mover según la acción
        self._mover(acc) 

        
        # Verificar si acabó el juego
        recompensa = 0
        game_over = False
        if self.is_collision() :
            game_over = True
            recompensa = -10
            return recompensa, game_over, self.puntos

        # Si pasa entre los tubos(verifica el el player este a la derecha de la manzana)
        # if self.player.y > self.comida.y-20 and self.player.y < self.comida.y+20 and self.player.x > self.comida.x:
        if self.player.x==self.comida.x and self.player.y > self.comida.y-40 and self.player.y < self.comida.y+30:    
            self.puntos += 1
            recompensa = 15

        # Actualizar ui y tiempo
        self._update_ui()
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

        #Si colisioa con el tubo superior
        if (pt.x <self.tubo_up.x+tuboW and pt.x >self.tubo_up.x-playerW and pt.y >self.tubo_up.y-playerH/2 and pt.y <self.tubo_up.y+tuboH-30):
            return True
        #Si no colisiona devuelve False
        return False

    #Actualizar pantalla
    def _update_ui(self):
        self.display.fill(FONDO)
        
        #dibujando en lapantalla
        self.display.blit(playerImg, (self.player.x, self.player.y))

        self.display.blit(manzanaImg, (self.comida.x, self.comida.y))
        #Movimiento
        self.mover_tubo(-10)
        self.mover_tubo_up(-10)
        self.mover_manzana(-10)
        self.display.blit(tuboImg, (self.tubo.x, self.tubo.y))
        self.display.blit(tuboImg_up, (self.tubo_up.x, self.tubo_up.y))
        #Dibujar puntuación
        text = font.render("Puntuacion: " + str(self.puntos), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _mover(self, acc):
        #Movimiento: [arriba, abajo]

        #Para calcular la nueva dirección
        clock_wise = [Direccion.DOWN, Direccion.UP]
        idx = clock_wise.index(self.direccion)
        
        #La acción es la posición de la variable ac en la cual el valor es 1
        accion=[0,0]
        if acc==0:
            accion=[1,0]
        if acc==1:
            accion=[0,1]

        if np.array_equal(accion, [1, 0]):
            nueva_dir = clock_wise[idx] #no cambia
        else:
            siguiente_idx = (idx + 1) % 2
            nueva_dir = clock_wise[siguiente_idx]  # [0,1]

        self.direccion= nueva_dir

        x = self.player.x
        y = self.player.y

        #Dirección
        if self.direccion== Direccion.DOWN:
            y += tam_bloque
        elif self.direccion== Direccion.UP:
            y -= tam_bloque

        self.player = Point(x, y)

    #Obtene estado del entorno
    def get_state(self):
        #Se definen las entradas de la red neuronal
        player = self.player
        point_u = Point(player.x, player.y - 15)
        point_d = Point(player.x, player.y + 15)
        
        dir_u = self.direccion== Direccion.UP
        dir_d = self.direccion== Direccion.DOWN

        #Parámetros del estado
        estado = [
            # peligros al ir recto
            (dir_u and self.is_collision(point_u)) or 
            (dir_d and self.is_collision(point_d)),


            # peligros de ir en contra
            (dir_d and self.is_collision(point_u)) or 
            (dir_u and self.is_collision(point_d)),
            
            # Mover a la dirección
            dir_u,
            dir_d,
            
            # localización de la comida
            self.comida.x < self.player.x,  # comida la izquierda
            self.comida.x > self.player.x,  # comida a la derecha
            self.comida.y < self.player.y,  # comida arriba
            self.comida.y > self.player.y  # comida abajo
            ]

        return np.array(estado, dtype=int)