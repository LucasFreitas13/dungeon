import pygame


class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type, animation_list, dummy_coin = False):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type # 0 - coin, 1 - health potion
        self.animation_list = animation_list
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.dummy_coin = dummy_coin

    def update(self, screen_scroll, player):
        # Não se aplica para dummy_coin que sempre aparece no topo da tela
        if not self.dummy_coin:
            # Reposicionando baseando com movimento da tela.
            self.rect.x += screen_scroll[0]
            self.rect.y += screen_scroll[1]
        # Checando se o item foi pego pelo personagem.
        if self.rect.colliderect(player.rect):
            if self.item_type == 0:   # Moeda
                player.score += 1
            elif self.item_type == 1:   # Poção de vida
                player.health += 10
                if player.health > 100:
                    player.health = 100
            self.kill()
        # Atualizar animação dos itens.
        animation_cooldown = 150
        # Atualizar imagem do item.
        self.image = self.animation_list[self.frame_index]
        # Checar se o tempo atual é maior que o tempo de atualização.
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        # Checar se a animação chegou ao fim.
        if self.frame_index >= len(self.animation_list):
            self.frame_index = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)   