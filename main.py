import pygame
import csv
import constants
from world import World
from character import Character
from weapon import Weapon
from items import Item

# Inicializo o pygame.
pygame.init()

# Chamo o método set_mode() do módulo display do pygame, que irá criar a tela com as configuarções definidas e mudar o título da janela.
screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Dungeon Crawler")

# Crio um objeto do tipo Clock para controlar o FPS do jogo.
clock = pygame.time.Clock()

# Definindo as variáveis do jogo
level = 1
screen_scroll = [0, 0]


# Definir as variáveis do movimento do personagem.
moving_left = False
moving_right = False
moving_up = False
moving_down = False

# Definindo fonte para o texto.
font = pygame.font.Font("/home/lucasfreitas13/vscode/dungeon/assets/fonts/AtariClassic.ttf", 20)

# Criando uma função para scalar a imagem do personagem.
def scale_img(img, scale):
    w = img.get_width()
    h = img.get_height()
    return pygame.transform.scale(img, (w*scale, h*scale))
    
# Carregando imagen de corações
heart_empty = scale_img(pygame.image.load("/home/lucasfreitas13/vscode/dungeon/assets/images/items/heart_empty.png").convert_alpha(), constants.ITEM_SCALE)
heart_half = scale_img(pygame.image.load("/home/lucasfreitas13/vscode/dungeon/assets/images/items/heart_half.png").convert_alpha(), constants.ITEM_SCALE)
heart_full = scale_img(pygame.image.load("/home/lucasfreitas13/vscode/dungeon/assets/images/items/heart_full.png").convert_alpha(), constants.ITEM_SCALE)

# Carregando imagem de moedas.
coin_images = []
for x in range(4):
    img = scale_img(pygame.image.load(f"/home/lucasfreitas13/vscode/dungeon/assets/images/items/coin_f{x}.png").convert_alpha(), constants.ITEM_SCALE)
    coin_images.append(img)

# Carregando imagem de poção.
red_potion = scale_img(pygame.image.load("/home/lucasfreitas13/vscode/dungeon/assets/images/items/potion_red.png").convert_alpha(), constants.POTION_SCALE)

item_images = []
item_images.append(coin_images)
item_images.append(red_potion)


# Carregando imagens das armas.
bow_img = scale_img(pygame.image.load("/home/lucasfreitas13/vscode/dungeon/assets/images/weapons/bow.png").convert_alpha(), constants.WEAPON_SCALE)
arrow_img = scale_img(pygame.image.load("/home/lucasfreitas13/vscode/dungeon/assets/images/weapons/arrow.png").convert_alpha(), constants.WEAPON_SCALE)
fireball_image = scale_img(pygame.image.load("/home/lucasfreitas13/vscode/dungeon/assets/images/weapons/fireball.png").convert_alpha(), constants.FIREBALL_SCALE)

# Carregando imagem dos tiles.
tile_list = []
for x in range(constants.TILES_TYPE):
    tile_image = pygame.image.load(f"/home/lucasfreitas13/vscode/dungeon/assets/images/tiles/{x}.png").convert_alpha()
    tile_image = pygame.transform.scale(tile_image, (constants.TILE_SIZE, constants.TILE_SIZE))
    tile_list.append(tile_image)

# Carrega imagens dos personagens.
mob_animations = []
mob_types = ["elf", "imp", "skeleton","goblin", "muddy", "tiny_zombie", "big_demon"]

animation_types = ["idle", "run"]
for mob in mob_types:
    animation_list = []
    for animation in animation_types:
        # Resetar a lista de imagens temporariamente.
        temp_list = []
        for i in range(4):
            # Carregar a imagem do personagem e o último método serve pra deixar o restante transparente.
            img = pygame.image.load(f"/home/lucasfreitas13/vscode/dungeon/assets/images/characters/{mob}/{animation}/{i}.png").convert_alpha()
            # Configurando o tamanho do personagem.
            img = scale_img(img,constants.SCALE)
            # Adicionando a imagem na lista.
            temp_list.append(img)
        animation_list.append(temp_list)
    mob_animations.append(animation_list)

# Função para mostrar texto na tela.
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

# Função para mostrar informações do jogo.
def draw_info():
    # Desenhando o painel
    pygame.draw.rect(screen, constants.PANEL, (0, 0, constants.SCREEN_WIDTH, 50))
    pygame.draw.line(screen, constants.WHITE, (0, 50), (constants.SCREEN_WIDTH, 50), 2)
    # Desenhando a vidas
    half_hear_drawn = False
    for i in range(5):
        if player.health >= ((i+1) * 20):
            screen.blit(heart_full, (10 + (i * 50), 0))
        elif player.health % 20 >= 0 and half_hear_drawn == False:
            screen.blit(heart_half, (10 + (i * 50), 0))
            half_hear_drawn = True
        else:
            screen.blit(heart_empty, (10 + (i * 50), 0))

    # Mostrando o level.
    draw_text("Level: " + str(level), font, constants.WHITE, constants.SCREEN_WIDTH/2, 15)

    # Desenhando a pontuação
    draw_text(f"X{player.score}", font, constants.WHITE, constants.SCREEN_WIDTH - 100, 15)

# Criar uma lista de tiles vazia
world_data = []
for row in range(constants.ROWS):
    r = [-1] * constants.COLS
    world_data.append(r)
# Importanto dados de level e criando o mundo

with open(f"/home/lucasfreitas13/vscode/dungeon/levels/level{level}_data.csv", newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
world.process_data(world_data, tile_list, item_images, mob_animations)


# Criando uma classe para mostrar o dano tomado.
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, color)  # Método render() do módulo font do pygame para criar o texto.
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)  # Colocando o texto no centro do personagem.
        self.counter = 0

    def update(self):
        # Reposicionando baseado no screen scroll.
        self.rect.x += screen_scroll[0]
        self.rect.y += screen_scroll[1]
        # Movendo o dano para cima.
        self.rect.y -= 1 
        self.counter += 1
        if self.counter > 40:
            self.kill()


# Criando o personagem
player = world.player

# Criando o arco
bow = Weapon(bow_img, arrow_img)

# Extraindo inimigos de world data
enemy_list = world.character_list

# Criando grupos de Sprites
damage_text_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
fireball_group = pygame.sprite.Group()

score_coin = Item(constants.SCREEN_WIDTH - 120, 23, 0, coin_images, True)
item_group.add(score_coin)
# Criação de items através do método World.process_data()
for item in world.item_list:
    item_group.add(item)


# Preciso criar um loop para manter a tela aberta
run = True
while run:
    # Definindo o FPS do jogo.
    clock.tick(constants.FPS)
    screen.fill(constants.BG)

    # Calculando o movimento do jogador, criei uma variável para cada direção.
    # Se estiver se movimentando a posição do personagem é alterada.
    dx = 0
    dy = 0
    if moving_right == True:
        dx = constants.SPEED
    if moving_left == True:
        dx = -constants.SPEED
    if moving_up == True:
        dy = -constants.SPEED
    if moving_down == True:
        dy = constants.SPEED

    # Movimentando o personagem.
    screen_scroll = player.move(dx, dy, world.obstacle_tiles)


    # Atualizando todos os objetos.
    world.update(screen_scroll)
    for enemy in enemy_list:
        fireball = enemy.ai(player, world.obstacle_tiles, screen_scroll, fireball_image)
        if fireball:
            fireball_group.add(fireball)
        if enemy.alive:
            enemy.update()

    player.update()
    arrow = bow.update(player)
    if arrow:
        arrow_group.add(arrow)

    for arrow in arrow_group:
        damage, damage_pos = arrow.update(screen_scroll, world.obstacle_tiles, enemy_list)
        if damage:
            damage_text = DamageText(damage_pos.centerx, damage_pos.y, str(damage), constants.RED)
            damage_text_group.add(damage_text)

    damage_text_group.update()
    fireball_group.update(screen_scroll, player)
    item_group.update(screen_scroll, player)

    # Desenhando o mapa na tela.
    world.draw(screen)

    # Desenho o personagem na tela.
    player.draw(screen)

    # Desenho o inimigo na tela.
    for enemy in enemy_list:
        enemy.draw(screen)

    bow.draw(screen)
    for arrow in arrow_group:
        arrow.draw(screen)

    for fireball in fireball_group:
        fireball.draw(screen)

    damage_text_group.draw(screen)
    item_group.draw(screen)
    draw_info()
    score_coin.draw(screen)
    
    # Verifico se o usuário clicou no botão de fechar a tela para sair do loop (event handler).
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # Verifico se o usuário apertou alguma tecla.
        if event.type == pygame.KEYDOWN:
            # Se o usuário apertou a tecla ESC, saio do loop.
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w:
                moving_up = True
            if event.key == pygame.K_s:
                moving_down = True

        # Verifico se o usuário soltou a tecla.
        if event.type == pygame.KEYUP:
            # Se o usuário apertou a tecla ESC, saio do loop.
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_w:
                moving_up = False
            if event.key == pygame.K_s:
                moving_down = False

    # Atualizando a tela enquanto o while é executado
    pygame.display.update()

# Finalizando o pygame.
pygame.quit()