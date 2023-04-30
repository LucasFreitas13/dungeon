import pygame
import math
import constants
import weapon
from constants import *

class Character():
    def __init__(self, x, y, health, mob_animations, char_type, boss, size):
        self.char_type = char_type
        self.boss = boss
        self.score = 0
        self.flip = False # Personagem começa olhando para a direita.
        self.animation_list = mob_animations[char_type]
        self.frame_index = 0
        self.action = 0 # 0= Parado, 1= Correndo
        self.update_time = pygame.time.get_ticks()
        self.running = False
        self.health = health
        self.alive = True
        self.hit = False
        self.last_hit = pygame.time.get_ticks()
        self.last_attack = pygame.time.get_ticks()
        self.stunned = False


        # Passando para aceitar uma imagem como parâmetro.
        self.image = self.animation_list[self.action][self.frame_index]
        # Criando um retângulo para representar o personagem.
        self.rect = pygame.Rect(0, 0, constants.TILE_SIZE * size, constants.TILE_SIZE * size)
        # Definindo a posição inicial do personagem.
        self.rect.center = (x, y)

    def move(self, dx, dy, obstacle_tiles):
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

        # Checando por colisões com o mapa na direção x.
        self.rect.x += dx
        for obstacle in obstacle_tiles:
            # Checando por colisões.
            if obstacle[1].colliderect(self.rect):
                # Verificando de qual lado está vindo a colisão.
                if dx > 0:
                    self.rect.right = obstacle[1].left
                if dx < 0:
                    self.rect.left = obstacle[1].right

        # Checando por colisões com o mapa na direção y.
        self.rect.y += dy
        for obstacle in obstacle_tiles:
            # Checando por colisões.
            if obstacle[1].colliderect(self.rect):
                # Verificando de qual lado está vindo a colisão.
                if dy < 0:
                    self.rect.top = obstacle[1].bottom
                if dy > 0:
                    self.rect.bottom = obstacle[1].top        

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
    
    def ai(self, player, obstacle_tiles, screen_scroll, fireball_image):
        clipped_line = ()
        stun_cooldown = 100
        ai_dx = 0
        ai_dy = 0
        fireball = None
        # Reposicionando os mobs baseado no screen scroll
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]

        # Criando uma linha de visão para o inimigo (ver o jogador)
        line_of_sight = ((self.rect.centerx, self.rect.centery), (player.rect.centerx, player.rect.centery))
        # Verificando se o jogador está no campo de visão do inimigo
        for obstacle in obstacle_tiles:
            if obstacle[1].clipline(line_of_sight):
                clipped_line = obstacle[1].clipline(line_of_sight)

        # Verificando a distância entre o jogador e o inimigo
        dist = ((self.rect.centerx - player.rect.centerx)**2 + (self.rect.centery - player.rect.centery)**2)**0.5
        if not clipped_line and dist > constants.RANGE:
            if self.rect.centerx > player.rect.centerx:
                ai_dx = -constants.ENEMY_SPEED
            if self.rect.centerx < player.rect.centerx:
                ai_dx = constants.ENEMY_SPEED
            if self.rect.centery > player.rect.centery:
                ai_dy = -constants.ENEMY_SPEED
            if self.rect.centery < player.rect.centery:
                ai_dy = constants.ENEMY_SPEED

        if self.alive:
            if not self.stunned:
                self.move(ai_dx, ai_dy, obstacle_tiles)
                # Atacando o personagem.
                if dist < constants.ATTACK_RANGE and player.hit == False:
                    player.health -= constants.ENEMY_DAMAGE
                    player.hit = True
                    player.last_hit = pygame.time.get_ticks()

            # Lançamento de bolas de fogo do boss.
            fireball_cooldown = 700
            if self.boss:
                if dist < 500:
                    if (pygame.time.get_ticks() - self.last_attack) >= fireball_cooldown:
                        self.last_fireball = pygame.time.get_ticks()
                        fireball = weapon.Fireball(fireball_image, self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery)
                        self.last_attack = pygame.time.get_ticks()

            # Checando se sofreu um hit
            if self.hit == True:
                self.hit = False
                self.last_hit = pygame.time.get_ticks()
                self.stunned = True 
                self.running = False
                self.update_action(0)
            
            if (pygame.time.get_ticks() - self.last_hit) > stun_cooldown:
                self.stunned = False

        return fireball

    def update(self):
        # Verificando se personagem está vivo.
        if self.alive <= 0:
            self.health = 0
            self.alive = False

        # Resetando o dano recebido pelo personagem.
        hit_cooldown = 1000
        if self.char_type == 0:
            if self.hit == True and (pygame.time.get_ticks() - self.last_hit) > hit_cooldown:
                self.hit = False

        
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
