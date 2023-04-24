import pygame
import math
import constants
from constants import *

class Character():
    def __init__(self, x, y, health, mob_animations, char_type):
        self.char_type = char_type
        self.score = 0
        # Personagem começa olhando para a direita.
        self.flip = False
        self.animation_list = mob_animations[char_type]
        #
        self.frame_index = 0
        self.action = 0 # 0=Parado, 1= Correndo
        self.update_time = pygame.time.get_ticks()
        self.running = False
        self.health = health
        self.alive = True


        # Passando para aceitar uma imagem como parâmetro.
        self.image = self.animation_list[self.action][self.frame_index]
        # Criando um retângulo para representar o personagem.
        self.rect = pygame.Rect(0, 0, constants.TILE_SIZE, constants.TILE_SIZE)
        # Definindo a posição inicial do personagem.
        self.rect.center = (x, y)

    def move(self, dx, dy):
        screen_scroll = [0, 0]
        self.running = False
        # Verificando se o personagem está se movimentando.
        if dx != 0 or dy != 0:
            self.running = True
        if dx < 0:
            self.flip = True
        if dx > 0:
            self.flip = False
        # Controle da velocidade diagonal.
        if dx != 0 and dy != 0:
            dx *= (math.sqrt(2)/2)
            dy *= (math.sqrt(2)/2)
        # Alterando a posição do personagem.
        self.rect.x += dx
        self.rect.y += dy

        # Movimento da imagem apenas para o jogador.
        if self.char_type == 0:
            # Atualizando scroll da imagem baseado na posição do jogador.
            # Movimento da tela para esquerda ou direita.
            if self.rect.right > constants.SCREEN_WIDTH - constants.SCROLL_THRESH:
                screen_scroll[0] = (constants.SCREEN_WIDTH - constants.SCROLL_THRESH) - self.rect.right
                self.rect.right = constants.SCREEN_WIDTH - constants.SCROLL_THRESH

            if self.rect.left < constants.SCROLL_THRESH:
                screen_scroll[0] = (constants.SCROLL_THRESH) - self.rect.left
                self.rect.left = constants.SCROLL_THRESH

            # Movimento da tela para cima e para baixo.
            if self.rect.bottom > constants.SCREEN_HEIGHT - constants.SCROLL_THRESH:
                screen_scroll[1] = (constants.SCREEN_HEIGHT - constants.SCROLL_THRESH) - self.rect.bottom
                self.rect.bottom = constants.SCREEN_HEIGHT - constants.SCROLL_THRESH

            if self.rect.top < constants.SCROLL_THRESH:
                screen_scroll[1] = (constants.SCROLL_THRESH) - self.rect.top
                self.rect.top = constants.SCROLL_THRESH

        return screen_scroll
    
    def ai(self, screen_scroll):
        # Reposicionando os mobs baseado no screen scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]


    def update(self):
        # Verificando se personagem está vivo.
        if self.alive <= 0:
            self.health = 0
            self.alive = False
        # Verificando qual ação o personagme está fazendo.
        if self.running == True:
            self.update_action(1)
        else:
            self.update_action(0)

        # Controlar a velocidade da animação.
        animation_cooldown = 70
        # Atualizar a imagem do personagem.
        self.image = self.animation_list[self.action][self.frame_index]
        # Verificando se o tempo atual é maior que o tempo de atualização.
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        # Verificando se o frame atual é maior que o número de frames.
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        # Verificando se a ação atual é diferente da nova ação.
        if new_action != self.action:
            self.action = new_action
            # Atualizando o frame.
            self.frame_index = 0
            # Atualizando o tempo de atualização.
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        flipped_image = pygame.transform.flip(self.image, self.flip, False)
        # Desenhando o personagem no retângulo definido.
        if self.char_type == 0:
            surface.blit(flipped_image, (self.rect.x, self.rect.y - constants.SCALE * constants.OFFSET))
        else:
            surface.blit(flipped_image, self.rect)
        # Desenhando o personagem na tela.
        pygame.draw.rect(surface, RED, self.rect, 1)
        
