import os
import random
import sys
import pygame as pg
import time
import math


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP:(0,-5), #上
    pg.K_DOWN:(0,+5), #下
    pg.K_LEFT:(-5,0), #左
    pg.K_RIGHT:(+5,0), #右
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRect or 爆弾Rect
    戻り値：判定結果タプル(横判定結果、縦判定結果)
    True：画面内/False：画面外
    """
    yoko, tate = True, True 
    if rct.left < 0 or WIDTH < rct.right: #横方向判定
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom: #縦方向判定
        tate = False
    return yoko, tate


def gameover(scrren: pg.Surface) -> None:
    go_img = pg.Surface((WIDTH, HEIGHT))
    pg.draw.rect(go_img, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
    go_img.set_alpha(180)
    scrren.blit(go_img, [0, 0])

    fonto = pg.font.Font(None, 80)
    txt = fonto.render("Game Over", True, (255, 255, 255))
    txt_rct = txt.get_rect(center=(WIDTH//2, HEIGHT//2))
    scrren.blit(txt, txt_rct)

    kk_img = pg.image.load("fig/8.png")
    kk_rct1 = kk_img.get_rect(center=(WIDTH//2 - 200, HEIGHT//2))
    kk_rct2 = kk_img.get_rect(center=(WIDTH//2 + 200, HEIGHT//2))
    scrren.blit(kk_img, kk_rct1)
    scrren.blit(kk_img, kk_rct2)

    pg.display.update()
    time.sleep(5)


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)] # 加速度のリスト [1, 2, ..., 10]
    
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        bb_img.set_colorkey((0, 0, 0))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_imgs.append(bb_img)
        
    return bb_imgs, bb_accs


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動量タプルと対応する画像Surfaceの辞書を返す
    """
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img_flip = pg.transform.flip(img0, True, False) # 左右反転

    kk_dict = {
        (0, 0): img0,
        (+5, 0): img_flip,
        (+5, -5): pg.transform.rotozoom(img_flip, 45, 1.0),
        (0, -5): pg.transform.rotozoom(img_flip, 90, 1.0),
        (-5, -5): pg.transform.rotozoom(img0, -45, 1.0),
        (-5, 0): img0,
        (-5, +5): pg.transform.rotozoom(img0, 45, 1.0),
        (0, +5): pg.transform.rotozoom(img_flip, -90, 1.0),
        (+5, +5): pg.transform.rotozoom(img_flip, -45, 1.0),
    }
    return kk_dict
    
       
def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    """
    爆弾がこうかとんに向かって移動するベクトルを計算する
    """
    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery
    norm = math.sqrt(dx**2 + dy**2)
    
    # 距離が300未満なら、慣性として計算前の方向ベクトルを返す
    if norm < 300:
        return current_xy
        
    # ノルムが√50になるように正規化する
    target_norm = math.sqrt(50)
    vx = (dx / norm) * target_norm
    vy = (dy / norm) * target_norm
    
    return vx, vy

    
def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")  
    #こうかとんの初期化
    kk_imgs = get_kk_imgs()       # ← 辞書を取得
    kk_img = kk_imgs[(0, 0)]      # ← 初期画像は静止状態
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    #爆弾の初期
    bb_img = pg.Surface((20, 20)) #爆弾用の空のSurface
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), (10)) #半径10の赤い円を描画
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect() #爆弾rect
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT) #横初期座標、縦初期座標
    vx, vy = +5, +5

    clock = pg.time.Clock()
    tmr = 0

    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = bb_imgs[0] # 初期画像を設定

    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0, 0)] # 初期画像

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        if kk_rct.colliderect(bb_rct): #こうかとんrctと爆弾rctがぶつかったら
            gameover(screen)
            return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        # if key_lst[pg.K_UP]:
        #     sum_mv[1] -= 5
        # if key_lst[pg.K_DOWN]:
        #     sum_mv[1] += 5
        # if key_lst[pg.K_LEFT]:
        #     sum_mv[0] -= 5
        # if key_lst[pg.K_RIGHT]:
        #     sum_mv[0] += 5
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0] #横方向移動
                sum_mv[1] += mv[1] #縦方向移動

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1]) #動きをなかったことにする
        kk_img = kk_imgs[tuple(sum_mv)]   # ← 移動方向に応じて画像を切り替え
        screen.blit(kk_img, kk_rct)

        bb_rct.move_ip(vx, vy)
        yoko, tate = check_bound(bb_rct)
        if not yoko: #横方向にはみ出していたら
            vx *= -1
        if not tate: #縦方向にはみ出していたら
            vy *= -1
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)

        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))

        avx = vx * bb_accs[min(tmr // 500, 9)] # 現在の加速度を反映した速度
        avy = vy * bb_accs[min(tmr // 500, 9)]
        bb_img = bb_imgs[min(tmr // 500, 9)]

        # Surfaceの大きさが変わったら、Rectのサイズも更新する
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height
        
        bb_rct.move_ip(avx, avy) # vx, vy の代わりに avx, avy を使う

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
