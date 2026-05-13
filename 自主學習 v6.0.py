import pygame
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




    def update(self,platforms,passibleplatforms,crumbleing_platforms,vertical_platforms):
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
        
        
        # 防止玩家凌空跳
        if not pygame.sprite.spritecollide(self, platforms, False) and \
           not pygame.sprite.spritecollide(self, passibleplatforms, False) and \
           not pygame.sprite.spritecollide(self, crumbleing_platforms, False) and \
           not pygame.sprite.spritecollide(self, vertical_platforms, False):
            self.is_jumping = True




        #偵測是否撞到平台
        for hit in pygame.sprite.spritecollide(self, platforms, False):
            if self.speedy > 0:
                self.rect.bottom = hit.rect.top
                self.speedy = 0
                self.is_jumping = False
            elif self.speedy < 0:
                self.rect.top = hit.rect.bottom
                self.speedy = 0
        
        for hit in pygame.sprite.spritecollide(self, passibleplatforms, False):
            if self.speedy > 0 and hit.rect.bottom >= self.rect.top and self.rect.top <= hit.rect.top <= self.rect.bottom:
                self.rect.bottom = hit.rect.top
                self.speedy = 0
                self.is_jumping = False
                self.rect.x += hit.speedx

        for hit in pygame.sprite.spritecollide(self, crumbleing_platforms, False):
            if self.speedy > 0 and hit.rect.bottom >= self.rect.top and self.rect.top <= hit.rect.top <= self.rect.bottom:
                self.rect.bottom = hit.rect.top
                self.speedy = 0
                self.is_jumping = False
                hit.is_touched = True

        for hit in pygame.sprite.spritecollide(self, vertical_platforms, False):
            if self.speedy >= 0 and self.rect.bottom <= hit.rect.bottom + 10 and self.rect.bottom >= hit.rect.top:
                self.rect.bottom = hit.rect.top
                self.speedy = 0
                self.is_jumping = False

                self.rect.y += hit.speedy


        if self.rect.right > WIDTH: self.rect.right = WIDTH
        if self.rect.left < 0: self.rect.left = 0




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




class VERTICAL_PLATFORM(pygame.sprite.Sprite):
    def __init__(self, x, y, width, speed_y, move_range=100):
        super().__init__()
        self.image = pygame.Surface((width, 15))
        self.image.fill(BLUE) # 用藍色區分
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speedy = speed_y
        self.start_y = y
        self.move_range = move_range
        self.move_range_counter = 0
    
    def update(self):
        self.rect.y += self.speedy
        self.move_range_counter += abs(self.speedy) # 新增一個計數器
        
        if self.move_range_counter > self.move_range:
            self.speedy *= -1
            self.move_range_counter = 0





#文字工具
font_name = pygame.font.match_font(FONT)
def draw_text(surf,text,size,x,y,color=WHITE):
    font = pygame.font.Font(font_name,size)
    text_surface = font.render(text,True,color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x,y)
    surf.blit(text_surface,text_rect)




#平台生成空間檢查(for垂直平台)
def is_space_free(test_rect,all_platforms):
    check_rect = test_rect.inflate(20,40)
    for p in all_platforms:
        if check_rect.colliderect(p.rect):
            return False
    return True




#遊戲重置函式
def reset_game():
    global all_sprites, platforms, passibleplatforms, crumbleing_platforms, vertical_platforms, player
    global danger_y, danger_speed
    global score, total_distance, last_player_y, max_distance, world_offset


    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    passibleplatforms = pygame.sprite.Group()
    crumbleing_platforms = pygame.sprite.Group()
    vertical_platforms = pygame.sprite.Group()



    #分數
    score = 1
    total_distance = 0 #未使用
    max_distance = 0
    world_offset = 0
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
vertical_platforms = pygame.sprite.Group()



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
        vertical_platforms.update()
        player.update(platforms,passibleplatforms,crumbleing_platforms,vertical_platforms)
        



        #死亡線
        danger_y -= danger_speed
        danger_speed = 0.8 + (score * 0.05)
        if danger_speed > 3.5: danger_speed = 3.5




        #鏡頭向下(update) + 分數運算
        if player.rect.top <= CAMARA_UP:
            # 1. 計算位移量
            scroll_dist = CAMARA_UP - player.rect.top
            world_offset += scroll_dist
            danger_y += scroll_dist #死亡線不隨鏡頭移動



            player.rect.top = CAMARA_UP
           
            # 3. 讓所有物件向下移動
            for sprite in all_sprites:
                sprite.rect.y += scroll_dist




            danger_y += scroll_dist #死亡線同步下移
            player.rect.top = CAMARA_UP #重新鎖定玩家位置
            last_player_y = player.rect.y #更新最後位置




       
        elif world_offset > 300 and player.rect.bottom >= HEIGHT * 0.7:
            follow_dist = player.rect.bottom - (HEIGHT * 0.7)


            if follow_dist > 10: follow_dist = 10
            world_offset -= follow_dist
       
            for sprite in all_sprites:
                sprite.rect.y -= follow_dist
           
            danger_y -= follow_dist #死亡線同步上移





        #平台自動生成與回收(update)
        #找出目前畫面中位置最高的平台
        highest_plat = None
        min_y = HEIGHT
        for plat in all_sprites:
            if isinstance(plat, (PLATFORM, PASSIBLEPLATFORM, CRUMBLEING_PLATFORM, VERTICAL_PLATFORM)):
                if plat.rect.y < min_y:
                    min_y = plat.rect.y
                    highest_plat = plat


        # 2. 如果最高平台進入了畫面，就在它上方隨機生成一個新的
        if highest_plat and highest_plat.rect.y > 0:
            placed = False
            attempts = 0
            
            while not placed and attempts < 10:
                new_x = random.randint(0, WIDTH - 150)
                new_y = highest_plat.rect.y - random.randint(100, 140)
                
                # 測試生成矩形 (假設平台寬150, 高20)
                test_rect = pygame.Rect(new_x, new_y, 150, 20)
                
                if is_space_free(test_rect, all_sprites):
                    # 決定生成哪種平台 (包含垂直移動平台)
                    r = random.random()
                    if r > 0.6: # 穿透平台
                        new_plat = PASSIBLEPLATFORM(new_x, new_y, 150, random.randint(2, 5))
                        passibleplatforms.add(new_plat)
                    elif r > 0.3: # 正常平台
                        new_plat = PLATFORM(new_x, new_y, 150)
                        platforms.add(new_plat)
                    elif r > 0.15: # 垂直移動平台 (新增)
                        new_plat = VERTICAL_PLATFORM(new_x, new_y, 100, speed_y=2, move_range=80)
                        # 注意：你需要定義一個新的 vertical_platforms 群組並加進去
                        vertical_platforms.add(new_plat)
                    else: # 碎裂
                        new_plat = CRUMBLEING_PLATFORM(new_x, new_y, 120)
                        crumbleing_platforms.add(new_plat)
                    
                    all_sprites.add(new_plat)
                    placed = True
                
                attempts += 1



        #刪除掉出螢幕底部的平台
        for sprite in all_sprites:
            if isinstance(sprite, (PLATFORM, PASSIBLEPLATFORM,CRUMBLEING_PLATFORM,VERTICAL_PLATFORM)):
                if sprite.rect.top > danger_y + 100:
                    sprite.kill()
       
        #玩家掉到死亡線以下
        if player.rect.bottom > danger_y:
            state = GAMEOVER
    

    
        #分數計算
        current_height = world_offset + (HEIGHT - 50 - player.rect.bottom)

        # 紀錄最高點
        if current_height > max_distance:
            max_distance = current_height

        # 換算成樓層
        score = int(max_distance // 350) + 1
        display_meters = max_distance * (3.0 / 350.0)





    #顯示(輸出)
    screen.fill(BLACK)



    if state == MENU:
        draw_text(screen,"A JUMP GAME",64,WIDTH/2,HEIGHT/4,YELLOW)
        draw_text(screen,"PRESS SPACE TO START",32,WIDTH/2,HEIGHT/2)
   
    elif state == PLAYING:
        all_sprites.draw(screen)


        draw_text(screen, f"{score} F", 40, 60, 40, WHITE)
        draw_text(screen, f"{display_meters:.1f} m", 24, 70, 85, WHITE)


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
        draw_text(screen, f"SCORE: {score} F ({display_meters:.1f} m)", 40, WIDTH/2, HEIGHT/2 - 70, YELLOW)
        draw_text(screen,"Press R to Return Menu",32,WIDTH/2,HEIGHT/2)



    pygame.display.update()






pygame.quit()
