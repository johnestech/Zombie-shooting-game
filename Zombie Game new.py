#importing libraries
import os
from tkinter import Canvas, Tk, messagebox, PhotoImage, font
from random import randrange, choice

# Game Canvas dimensions
Canvaswidth = 1000
Canvasheight = 700
Bullet_speed = 20
Zombie_speed = 50 
Plane_speed = 20

# Initialize game window
root = Tk()
root.title('Zombie Shooter Game')
C = Canvas(root, width=Canvaswidth, height=Canvasheight, background="black")
C.pack()

# Making the code dir same with the images
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Loading and scaling the images
plane_img = PhotoImage(file='plane.png')
harder_zombie_img = PhotoImage(file='simple.png').subsample(2, 2)
hard_zombie_img = PhotoImage(file='hard.png').subsample(2, 2)
simple_zombie_img = PhotoImage(file='harder.png').subsample(2, 2)

# Zombie game properties
score = 0
high_score = 0
lives = 10
zombie_type = [
    (harder_zombie_img, 1, 5),  # 5 Hits to kill harder zombie
    (hard_zombie_img, 2, 3),    # 3 Hits to kill harder zombie
    (simple_zombie_img, 3, 1)   # 1 Hits to kill harder zombie
]
game_active = True

# The plane properties
plane = C.create_image(Canvaswidth // 2, Canvasheight - 50, image=plane_img)
plane_x = Canvaswidth // 2
plane_y = Canvasheight - 50
plane_width = plane_img.width()
plane_height = plane_img.height()

# Game text displays
game_font = font.nametofont("TkFixedFont")
game_font.config(size=14)
score_text = C.create_text(10, 10, anchor="nw", font=game_font, fill="white", text="Score: " + str(score))
high_score_text = C.create_text(Canvaswidth - 10, 10, anchor="ne", font=game_font, fill="white", text="High Score: " + str(high_score))
lives_text = C.create_text(Canvaswidth // 2, 10, anchor="n", font=game_font, fill="white", text="Lives: " + str(lives))

# Handling highscore
def load_highscore():
    global high_score
    try:
        with open("zombie_high_score.txt", "r") as file:
            high_score = int(file.read().strip())
    except (FileNotFoundError, ValueError):
        high_score = 0

def save_highscore():
    with open("zombie_high_score.txt", "w") as file:
        file.write(str(high_score))

load_highscore()
C.itemconfigure(high_score_text, text="High Score: " + str(high_score))

# Plane movements
def move_plane(event):
    global plane_x, plane_y
    if not game_active:
        return
    if event.keysym == 'Left':
        plane_x = max(0, plane_x - Plane_speed)
    elif event.keysym == 'Right':
        plane_x = min(Canvaswidth, plane_x + Plane_speed)
    elif event.keysym == 'Up':
        plane_y = max(0, plane_y - Plane_speed)
    elif event.keysym == 'Down':
        plane_y = min(Canvasheight, plane_y + Plane_speed)
    C.coords(plane, plane_x, plane_y)

root.bind("<Left>", move_plane)
root.bind("<Right>", move_plane)
root.bind("<Up>", move_plane)
root.bind("<Down>", move_plane)

# The Bullet propertie and moves
bullets = []

def shoot_bullet(event):
    global plane_x, plane_y
    if not game_active:
        return
    for offset in [-10, 0, 10]: 
        bullet = C.create_rectangle(plane_x + offset - 2, plane_y - plane_height // 2 - 10, plane_x + offset + 2, plane_y - plane_height // 2, fill="gold")
        bullets.append(bullet)
        move_bullet(bullet)

root.bind("<space>", shoot_bullet)

def move_bullet(bullet):
    if C.coords(bullet) and C.coords(bullet)[1] > 0:
        C.move(bullet, 0, -Bullet_speed)
        root.after(50, lambda: move_bullet(bullet))
    else:
        C.delete(bullet)
        if bullet in bullets:
            bullets.remove(bullet)

# Zombie properties
zombies = []

def spawn_zombie():
    if not game_active:
        return
    zombie_img, difficulty, hit_points = choice(zombie_type)
    zombie_x = randrange(0, Canvaswidth)
    zombie = C.create_image(zombie_x, 0, image=zombie_img)
    zombies.append((zombie, difficulty, hit_points))
    move_zombie(zombie, difficulty, hit_points)
    root.after(1000, spawn_zombie)

def move_zombie(zombie, difficulty, hit_points):
    global score, lives, high_score
    if not game_active or not root.winfo_exists():
        return
    if C.coords(zombie) and C.coords(zombie)[1] < Canvasheight:
        C.move(zombie, 0, difficulty)
        root.after(Zombie_speed, lambda: move_zombie(zombie, difficulty, hit_points))
    else:
        if C.coords(zombie):
            C.delete(zombie)
            zombies[:] = [z for z in zombies if z[0] != zombie]
            print("Zombie touched the bottom and disappear")
            lose_life()

    # Check for hits with bullets
    for bullet in bullets:
        if C.coords(bullet) and C.bbox(zombie) and check_collision(C.coords(bullet), C.bbox(zombie)):
            C.delete(bullet)
            if bullet in bullets:
                bullets.remove(bullet)
            hit_points -= 1
            if hit_points <= 0:
                C.delete(zombie)
                zombies[:] = [z for z in zombies if z[0] != zombie]
                score += 10 * difficulty
                C.itemconfigure(score_text, text="Score: " + str(score))
                print(f"Bullet hit zombie. Score: {score}")
                if score > high_score:
                    high_score = score
                    save_highscore()
                    C.itemconfigure(high_score_text, text="High Score: " + str(high_score))
                break
            else:
                for i in range(len(zombies)):
                    if zombies[i][0] == zombie:
                        zombies[i] = (zombie, difficulty, hit_points)
                        break

    # Check for hits with plane
    if C.bbox(zombie) and check_collision(C.coords(plane), C.bbox(zombie)):
        C.delete(zombie)
        zombies[:] = [z for z in zombies if z[0] != zombie]
        print("Plane hit zombie, plane resets and zombie disappear")
        lose_life()
        reset_plane()

def check_collision(coords1, bbox2):
    if not coords1 or not bbox2:
        return False
    x1, y1 = coords1[0], coords1[1]
    return bbox2[0] <= x1 <= bbox2[2] and bbox2[1] <= y1 <= bbox2[3]

def lose_life():
    global lives, game_active
    lives -= 1
    C.itemconfigure(lives_text, text="Lives: " + str(lives))
    print(f"Lives remaining: {lives}")
    if lives <= 0:
        game_active = False
        game_over()

def reset_plane():
    global plane_x, plane_y
    if not game_active:
        return
    plane_x = Canvaswidth // 2
    plane_y = Canvasheight - 50
    if root.winfo_exists():
        C.coords(plane, plane_x, plane_y)

def game_over():
    global score
    messagebox.showinfo("Game Over", f"Final Score: {score}")
    root.destroy()


root.after(1000, spawn_zombie)
root.mainloop()
