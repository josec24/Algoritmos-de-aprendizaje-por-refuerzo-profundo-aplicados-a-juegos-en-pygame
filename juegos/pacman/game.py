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

#Tamaño de bloque(pacman)
tam_bloque = 20
#Velocidad
velocidad = 40

#Imagen del blooque(pacman)
pacmanImg = pygame.image.load('imagenes/pacman/pacman.png')

#Redimencionando la imagen de la pacman
pacmanImg = pygame.transform.scale(pacmanImg, (20, 20))

#Imagen del coin
coinImg = pygame.image.load('imagenes/pacman/coin.png')
#Redimencionando la imagen de la coin
coinImg = pygame.transform.scale(coinImg, (13, 13))

enemyImg = pygame.image.load('imagenes/pacman/enemy.png')
#Redimencionando la imagen del enemigo
enemyImg = pygame.transform.scale( enemyImg, (20, 20))


#Clase pacman
class PacmanGame:
    def __init__(self, w=640, h=480):
        #Ancho y alto del display
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Pacman')
        self.tiempo = pygame.time.Clock()
        self.reinicio()


    #Reiniciar juego
    def reinicio(self):
        # Estado inicial
        self.direccion= Direccion.RIGHT

        #Posición del player    
        self.player = Point(self.w/2-200, self.h/2)

        #Inicio de parámetros
        self.puntos = 0
        self.enemy = None
        self._pos_enemy()
        self.comidas=[]
        self._pos_comidas()
        self.comida = None
        self._pos_comida()
        self.frame_iteracion = 0



    #Posición random de la enemy(coin)
    def _pos_enemy(self):
        x = random.randint(0, (self.w-tam_bloque )//tam_bloque )*tam_bloque
        y = random.randint(0, (self.h-tam_bloque )//tam_bloque )*tam_bloque
        self.enemy = Point(x, y)
        if self.enemy in self.player:
            self._pos_enemy()


    #Posición random de la enemy(coin)
    def _pos_comida(self):
        self.comida=random.choice(self.comidas)
        if self.comida in self.player:
            self._pos_comida()

    #Posición random de la enemy(coin)
    def _pos_comidas(self):
        for i in range(21):
            for j in range(16):
                point=Point(i*25+50,j*25+50)
                self.comidas.append(point)
        

    def getTime(self):
            return pygame.time.get_ticks()/1000

    def paso_juego(self, accion):
        self.frame_iteracion += 1
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # Mover según la acción
        self._mover(accion)

        # Verificar si acabó el juego
        recompensa = 0
        game_over = False
        if self.is_collision():
            game_over = True
            recompensa = -10
            return recompensa, game_over, self.puntos

        if len(self.comidas)<2:
            self._pos_comidas()


        if self.is_collision_Coin():
            self.puntos += 1
            recompensa=2

        # # Si colisiona con la enemy
        # if self.player == self.comida:
        if abs(self.player.x-self.comida.x)<30 and abs(self.player.y-self.comida.y)<30:
            self.puntos += 1
            recompensa = 10
            self._pos_comida()
        self.mov_Enemy()



        # self.player=Point(620,0)

        if self.player.y<0:
            self.player=Point(self.player.x,450)

        if self.player.y>450:
            self.player=Point(self.player.x,0)

        if self.player.x>620:
            self.player=Point(0,self.player.y)

        if self.player.x<0:
            self.player=Point(620,self.player.y)

        # print('po: ',self.player)

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
            pt = self.player

        if abs(pt.x-self.enemy.x)<30 and abs(pt.y-self.enemy.y)<30:
            return True

        return False

    #El enemigo se mueve según el player
    def mov_Enemy(self):
        mov_x=self.player.x
        mov_y=self.player.y

        mover_x=0
        mover_y=0

        dir_x=self.enemy.x-mov_x
        dir_y=self.enemy.y-mov_y


        if dir_x>0:
            mover_x=-10
        elif dir_x<0:
            mover_x=10

        if dir_y>0:
            mover_y=-10
        elif dir_y<0:
            mover_y=10

        x=self.enemy.x+mover_x
        y=self.enemy.y+mover_y
        self.enemy = Point(x, y)


    #Comprueba si existe colisión con el coin
    def is_collision_Coin(self, pt=None):
        if pt is None:
            pt = self.player
        # Si colisiona con la recompensa
        for i in self.comidas:
            if abs(self.player.x - i.x)<20 and abs(self.player.y - i.y)<20:
                self.comidas.remove(i) 
                return True

        return False

    #Actualizar pantalla
    def _update_ui(self):
        self.display.fill(FONDO)
        
        #dibujando en lapantalla
        self.display.blit(pacmanImg, (self.player.x, self.player.y))

        #pintando cada coin
        for j in self.comidas:
            self.display.blit(coinImg, (j.x, j.y))    

        #Dibujar enemy
        self.display.blit(enemyImg, (self.enemy.x, self.enemy.y))

        #Dibujar enemy
        self.display.blit(coinImg, (self.comida.x, self.comida.y))

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

        x = self.player.x
        y = self.player.y
        #Dirección
        if self.direccion== Direccion.RIGHT:
            x += tam_bloque
        elif self.direccion== Direccion.LEFT:
            x -= tam_bloque
        elif self.direccion== Direccion.DOWN:
            y += tam_bloque
        elif self.direccion== Direccion.UP:
            y -= tam_bloque

        self.player = Point(x, y)


    #Obtene estado del entorno
    def get_state(self):
        #Se definen las entradas de la red neuronal
        player = self.player
        point_l = Point(player.x - 20, player.y)
        point_r = Point(player.x + 20, player.y)
        point_u = Point(player.x, player.y - 20)
        point_d = Point(player.x, player.y + 20)
        
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
            
            # localización de la enemy
            self.comida.x < self.player.x,  # comidaa la izquierda
            self.comida.x > self.player.x,  # enemy a la derecha
            self.comida.y < self.player.y,  # enemy arriba
            self.comida.y > self.player.y  # enemy abajo

            ]

        return np.array(estado, dtype=int)