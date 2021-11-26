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
    UP = 3
    DOWN = 4

#Punto (x,y)
Point = namedtuple('Point', 'x, y')

# Colores
WHITE = (255, 255, 255)
FONDO=(52, 152, 219)

#Tamaño de bloque(cuerpo)
tam_bloque = 20
#Velocidad
velocidad = 40

#Imagen del blooque(cuerpo)
cuerpoImg = pygame.image.load('imagenes/snake/cuerpo.png')
#Imagen de la manzana
manzanaImg = pygame.image.load('imagenes/snake/manzana.png')
#Redimencionando la imagen de la manzana
manzanaImg = pygame.transform.scale(manzanaImg, (20, 20))

#Clase snake
class SnakeGame:
    def __init__(self, w=640, h=480):
        #Ancho y alto del display
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.tiempo = pygame.time.Clock()
        self.reinicio()


    #Reiniciar juego
    def reinicio(self):
        # Estado inicial
        self.direccion= Direccion.RIGHT

        #Cabeza de la serpiente        
        self.cabeza = Point(self.w/2, self.h/2)
        #Cuerpo completo(lista)
        self.snake = [self.cabeza,
                      Point(self.cabeza.x-tam_bloque, self.cabeza.y),
                      Point(self.cabeza.x-(2*tam_bloque), self.cabeza.y)]

        #Inicio de parámetros
        self.puntos = 0
        self.comida = None
        self._pos_comida()
        self.frame_iteracion = 0

    #Posición random de la comida(manzana)
    def _pos_comida(self):
        x = random.randint(0, (self.w-tam_bloque )//tam_bloque )*tam_bloque
        y = random.randint(0, (self.h-tam_bloque )//tam_bloque )*tam_bloque
        self.comida = Point(x, y)
        if self.comida in self.snake:
            self._pos_comida()


    def paso_juego(self, accion):
        self.frame_iteracion += 1
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # Mover según la acción
        self._mover(accion)
        #insertar a la lista
        self.snake.insert(0, self.cabeza)
        
        # Verificar si acabó el juego
        recompensa = 0
        game_over = False
        if self.is_collision() or self.frame_iteracion > 100*len(self.snake):
            game_over = True
            recompensa = -10
            return recompensa, game_over, self.puntos

        # Si colisiona con la comida
        if self.cabeza == self.comida:
            self.puntos += 1
            recompensa = 20
            self._pos_comida()
        else:
            self.snake.pop()
        
        # Actualizar ui y tiempo
        self._update_ui()
        self.tiempo.tick(velocidad)

        # Devuelve el game_over y puntos
        return recompensa, game_over, self.puntos

    def getTime(self):
        return pygame.time.get_ticks()/1000

    #Comprueba si existe colisión
    def is_collision(self, pt=None):
        if pt is None:
            pt = self.cabeza
        # Si colisiona con el límite
        if pt.x > self.w - tam_bloque or pt.x < 0 or pt.y > self.h - tam_bloque or pt.y < 0:
            return True
        # Colisiona consigo mismo
        if pt in self.snake[1:]:
            return True

        return False

    #Actualizar pantalla
    def _update_ui(self):
        self.display.fill(FONDO)
        
        for pt in self.snake:
            #Dibujando cuerpo de serpiente
            self.display.blit(cuerpoImg, (pt.x, pt.y))

        #Dibujar comida
        self.display.blit(manzanaImg, (self.comida.x, self.comida.y))
        #Dibujar puntuación
        text = font.render("Puntuacion: " + str(self.puntos), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()


    def _mover(self, accion):
        # Movimiento: [recto, derecha, izquierda]

        #Para calcular la nueva dirección
        clock_wise = [Direccion.RIGHT, Direccion.DOWN, Direccion.LEFT, Direccion.UP]
        idx = clock_wise.index(self.direccion)

        #La acción es la posición de la variable ac en la cual el valor es 1
        ac=[0,0,0]
        if accion==0:
            ac=[1,0,0]
        elif accion==1:
            ac=[0,1,0]
        elif accion==2:
            ac=[0,0,1]

        if np.array_equal(ac, [1, 0, 0]):
            nueva_dir = clock_wise[idx] #no cambia
        elif np.array_equal(ac, [0, 1, 0]):
            siguiente_idx = (idx + 1) % 4
            nueva_dir = clock_wise[siguiente_idx] # derecha
        else: # [0, 0, 1]
            siguiente_idx = (idx - 1) % 4
            nueva_dir = clock_wise[siguiente_idx] # izquierda

        self.direccion= nueva_dir

        x = self.cabeza.x
        y = self.cabeza.y
        #Dirección
        if self.direccion== Direccion.RIGHT:
            x += tam_bloque
        elif self.direccion== Direccion.LEFT:
            x -= tam_bloque
        elif self.direccion== Direccion.DOWN:
            y += tam_bloque
        elif self.direccion== Direccion.UP:
            y -= tam_bloque

        self.cabeza = Point(x, y)


    #Obtene estado del entorno
    def get_state(self):
        #Se definen las entradas de la red neuronal
        cabeza = self.cabeza
        point_l = Point(cabeza.x - 20, cabeza.y)
        point_r = Point(cabeza.x + 20, cabeza.y)
        point_u = Point(cabeza.x, cabeza.y - 20)
        point_d = Point(cabeza.x, cabeza.y + 20)
        
        dir_l = self.direccion== Direccion.LEFT
        dir_r = self.direccion== Direccion.RIGHT
        dir_u = self.direccion== Direccion.UP
        dir_d = self.direccion== Direccion.DOWN

        #Parámetros del estado
        estado = [
            # peligros al ir recto
            (dir_r and self.is_collision(point_r)) or 
            (dir_l and self.is_collision(point_l)) or 
            (dir_u and self.is_collision(point_u)) or 
            (dir_d and self.is_collision(point_d)),

            # peligros a la derecha
            (dir_u and self.is_collision(point_r)) or 
            (dir_d and self.is_collision(point_l)) or 
            (dir_l and self.is_collision(point_u)) or 
            (dir_r and self.is_collision(point_d)),

            # peligros a la izquierda
            (dir_d and self.is_collision(point_r)) or 
            (dir_u and self.is_collision(point_l)) or 
            (dir_r and self.is_collision(point_u)) or 
            (dir_l and self.is_collision(point_d)),
            
            # Mover a la dirección
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # localización de la comida
            self.comida.x < self.cabeza.x,  # comidaa la izquierda
            self.comida.x > self.cabeza.x,  # comida a la derecha
            self.comida.y < self.cabeza.y,  # comida arriba
            self.comida.y > self.cabeza.y  # comida abajo
            ]

        return np.array(estado, dtype=int)