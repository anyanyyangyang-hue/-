import pygame
import os
import random



FPS = 60
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
PURPLE = (128,0,128)
HEIGHT = 600
WIDTH = 800
CAMARA_UP = HEIGHT // 3 #螢幕捲動
FONT = 'comic sans ms' #原本是'arial'字形
#遊戲狀態
MENU = 0
PLAYING = 1
GAMEOVER = 2
state = MENU #初始遊戲狀態
score = 0 #分數




pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("First game")






#物件
class PLAYER(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50,40))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT - 50
        self.speedx = 8
       
        self.speedy = 0
        self.gravity = 0.8
        self.jump_power = -16
        self.is_jumping = False




    def update(self,platforms):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_d] or key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_a] or key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx
        if self.rect.left > WIDTH:
            self.rect.right = 0




        if (key_pressed[pygame.K_UP] or key_pressed[pygame.K_w]) and not self.is_jumping:
            self.speedy = self.jump_power
            self.is_jumping = True
       
        self.speedy += self.gravity
        self.rect.y += self.speedy




        #偵測是否撞到平台
        unpass_hits = pygame.sprite.spritecollide(self, platforms, False)
        for hit in unpass_hits:
            if self.speedy > 0:  # 正在往下掉 -> 踩到地板
                self.rect.bottom = hit.rect.top
                self.speedy = 0
                self.is_jumping = False
            elif self.speedy < 0: # 正在往上跳 -> 撞到天花板 (禁止穿透)
                self.rect.top = hit.rect.bottom
                self.speedy = 0




        pass_hits = pygame.sprite.spritecollide(self,passibleplatforms, False)
        for hit in pass_hits:
            #只有在「向下掉」且「碰撞前腳底在平台上方」時才擋住
            if self.speedy > 0 and hit.rect.bottom >= self.rect.top and self.rect.top <= hit.rect.top <= self.rect.bottom:
                self.rect.bottom = hit.rect.top
                self.speedy = 0
                self.is_jumping = False
                self.rect.x += hit.speedx
       
        crumble_hits = pygame.sprite.spritecollide(self,crumbleing_platforms, False)
        for hit in crumble_hits:
            #只有在「向下掉」且「碰撞前腳底在平台上方」時才擋住
            if self.speedy > 0 and hit.rect.bottom >= self.rect.top and self.rect.top <= hit.rect.top <= self.rect.bottom:
                self.rect.bottom = hit.rect.top
                self.speedy = 0
                self.is_jumping = False
                hit.is_touched = True #讓平台被踩
       
        #死亡(掉落)
        if player.rect.bottom < danger_y:
            state = GAMEOVER



        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0




class PLATFORM(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height=20):
        super().__init__()
        self.image = pygame.Surface((width,height))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y




class PASSIBLEPLATFORM(pygame.sprite.Sprite):
    def __init__(self,x,y,width,speedx,height=10):
        super().__init__()
        self.image = pygame.Surface((width,height))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speedx = speedx
        self.start_x = x  #平台移動起始位置
   
    def update(self):
        self.rect.x += self.speedx
        # 設定移動範圍
        if self.rect.x > self.start_x + 200 or self.rect.x < self.start_x:
            self.speedx *= -1
       
class CRUMBLEING_PLATFORM(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height=15):
        super().__init__()
        self.image = pygame.Surface((width,height))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_touched = False
        self.timer = 40 #碎裂時間(frame)
   
    def update(self):
        if self.is_touched:
            self.timer -= 1
            if self.timer <= 15:
                self.image.fill(WHITE)
           
            if self.timer == 0:
                self.kill()



#文字工具
font_name = pygame.font.match_font(FONT)
def draw_text(surf,text,size,x,y,color=WHITE):
    font = pygame.font.Font(font_name,size)
    text_surface = font.render(text,True,color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x,y)
    surf.blit(text_surface,text_rect)




#遊戲重置函式
def reset_game():
    global all_sprites, platforms, passibleplatforms, crumbleing_platforms, player
    global danger_y, danger_speed
    global score, total_distance, last_player_y , max_distance


    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    passibleplatforms = pygame.sprite.Group()
    crumbleing_platforms = pygame.sprite.Group()



    #分數
    score = 1
    total_distance = 0
    max_distance = 0
    player = PLAYER()
    last_player_y = player.rect.y #玩家上一幀的位置


    danger_y = HEIGHT + 100
    danger_speed = 0.8




    #建立初始平台
    player = PLAYER()
    all_sprites.add(player)
    ground = PLATFORM(0,HEIGHT-50,WIDTH,50)
    all_sprites.add(ground)
    platforms.add(ground)



    p1 = PLATFORM(400,450,150)
    all_sprites.add(p1)
    platforms.add(p1)



    pp1 = PASSIBLEPLATFORM(300,350,150,3)
    all_sprites.add(pp1)
    passibleplatforms.add(pp1)



    c1 = CRUMBLEING_PLATFORM(400,250,150)
    all_sprites.add(c1)
    crumbleing_platforms.add(c1)






all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
passibleplatforms = pygame.sprite.Group()
crumbleing_platforms = pygame.sprite.Group()



player = PLAYER()
all_sprites.add(player)
ground = PLATFORM(0,HEIGHT-50,WIDTH,50)
all_sprites.add(ground)
platforms.add(ground)

p1 = PLATFORM(400,450,150)
all_sprites.add(p1)
platforms.add(p1)

pp1 = PASSIBLEPLATFORM(300,350,150,3)
all_sprites.add(pp1)
passibleplatforms.add(pp1)

c1 = CRUMBLEING_PLATFORM(400,250,150)
all_sprites.add(c1)
crumbleing_platforms.add(c1)



running = True
while running:
    clock.tick(FPS)



    #輸入
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
       
        if event.type == pygame.KEYDOWN:
            if state == MENU:
                if event.key == pygame.K_SPACE:
                    reset_game()
                    state = PLAYING
            elif state == GAMEOVER:
                if event.key == pygame.K_r:
                    state = MENU




    #更新
    if state == PLAYING:
   
        passibleplatforms.update()
        crumbleing_platforms.update()
        player.update(platforms)






        if player.rect.y < last_player_y:
            total_distance += (last_player_y - player.rect.y)
        last_player_y = player.rect.y




        #死亡線
        danger_y -= danger_speed
        danger_speed = 0.8 + (score * 0.1)
        if danger_speed > 3.5:
            danger_speed = 3.5




        #鏡頭向下(update) + 分數運算
        if player.rect.top <= CAMARA_UP:
            # 1. 計算位移量
            scroll_dist = CAMARA_UP - player.rect.top
            danger_y += scroll_dist #死亡線不隨鏡頭移動
            total_distance += scroll_dist #鏡頭移動轉換分數



            player.rect.top = CAMARA_UP
           
            # 3. 讓所有物件向下移動
            for sprite in all_sprites:
                sprite.rect.y += scroll_dist




            danger_y += scroll_dist #死亡線同步下移
            player.rect.top = CAMARA_UP #重新鎖定玩家位置
            last_player_y = player.rect.y #更新最後位置




       
        elif total_distance > 300 and player.rect.bottom >= HEIGHT * 0.7:
            follow_dist = player.rect.bottom - (HEIGHT * 0.7)


            if follow_dist > 10: follow_dist = 10
       
            for sprite in all_sprites:
                sprite.rect.y -= follow_dist
           
            danger_y -= follow_dist #死亡線同步上移
            total_distance -= follow_dist #總位移也要扣除，否則分數會變多


           
            if total_distance > max_distance:
                max_distance = total_distance
       


        score = (max_distance // 350) + 1



        #平台自動生成與回收(update)
        #找出目前畫面中位置最高的平台
        highest_plat = None
        min_y = HEIGHT
        for plat in platforms:
            if plat.rect.y < min_y:
                min_y = plat.rect.y
                highest_plat = plat
               
        for plat in passibleplatforms:
            if plat.rect.y < min_y:
                min_y = plat.rect.y
                highest_plat = plat
       
        for plat in crumbleing_platforms:
            if plat.rect.y < min_y:
                min_y = plat.rect.y
                highest_plat = plat




        # 2. 如果最高平台進入了畫面，就在它上方隨機生成一個新的
        if highest_plat and highest_plat.rect.y > 0:



            min_x = max(0, highest_plat.rect.x - 250)
            max_x = min(WIDTH - 150, highest_plat.rect.x + 250)
            new_x = random.randint(min_x, max_x)
            # 確保新平台在舊平台上方 100~130 像素
            new_y = highest_plat.rect.y - random.randint(100, 130)
           
            # 3. 隨機決定生成哪種平台
            r = random.random()
            if r > 0.4: # 可穿透平台
                new_plat = PASSIBLEPLATFORM(new_x, new_y, 150, random.randint(2, 5))
                passibleplatforms.add(new_plat)
                all_sprites.add(new_plat)
            elif r > 0.1: # 固體平台
                new_plat = PLATFORM(new_x, new_y, 150)
                platforms.add(new_plat)
                all_sprites.add(new_plat)
            else: #碎裂平台
                new_plat = CRUMBLEING_PLATFORM(new_x, new_y, 120)
                crumbleing_platforms.add(new_plat)
                all_sprites.add(new_plat)



        #刪除掉出螢幕底部的平台
        for sprite in all_sprites:
            if isinstance(sprite, (PLATFORM, PASSIBLEPLATFORM,CRUMBLEING_PLATFORM)):
                if sprite.rect.top > HEIGHT:
                    sprite.kill()
       
        #玩家掉到死亡線以下
        if player.rect.bottom > danger_y:
            state = GAMEOVER




    #顯示(輸出)
    screen.fill(BLACK)



    if state == MENU:
        draw_text(screen,"A JUMP GAME",64,WIDTH/2,HEIGHT/4,YELLOW)
        draw_text(screen,"PRESS SPACE TO START",32,WIDTH/2,HEIGHT/2)
   
    elif state == PLAYING:
        all_sprites.draw(screen)
        current_meters = (total_distance * (3.0 / 350.0))


        draw_text(screen, f"{score} F", 40, 60, 40, WHITE)
        draw_text(screen, f"{current_meters:.1f} m", 24, 70, 85, WHITE)


        danger_overlay = pygame.Surface((WIDTH, HEIGHT))
        danger_overlay.set_alpha(160)      # 設定透明度 (0-255)
        danger_overlay.fill((80, 80, 80))  # 填滿深灰色 (煙塵感)


        #將這個半透明層貼到螢幕上
        #死亡線以下都會變灰
        screen.blit(danger_overlay, (0, danger_y))


        #畫一條醒目的紅線作為邊界提醒
        pygame.draw.line(screen, RED, (0, danger_y), (WIDTH, danger_y), 5)




    elif state == GAMEOVER:
        draw_text(screen,"GAME OVER",64,WIDTH/2,HEIGHT/4,RED)
        draw_text(screen, f"SCORE: {score} F ({current_meters:.1f} m)", 40, WIDTH/2, HEIGHT/2 - 70, YELLOW)
        draw_text(screen,"Press R to Return Menu",32,WIDTH/2,HEIGHT/2)



    pygame.display.update()






pygame.quit()