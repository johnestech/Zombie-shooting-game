import os
from tkinter import Canvas, Tk, messagebox, PhotoImage, font
from random import randrange, choice

# Canvas dimensions
Canvaswidth = 1000
Canvasheight = 700
Bullet_speed = 20
Zombie_speed = 1000  # Speed of the zombies in milliseconds
Plane_speed = 20

# Initialize main window
root = Tk()
root.title('Zombie Shooter Game')
C = Canvas(root, width=Canvaswidth, height=Canvasheight, background="black")
C.pack()

# Set the working directory to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Load and scale images
plane_img = PhotoImage(file='plane.png')
simple_zombie_img = PhotoImage(file='simple.png').subsample(2, 2)
hard_zombie_img = PhotoImage(file='hard.png').subsample(2, 2)
harder_zombie_img = PhotoImage(file='harder.png').subsample(2, 2)

# Game properties
score = 0
high_score = 0
lives = 10
zombie_type = [(simple_zombie_img, 1, 1), (hard_zombie_img, 2, 2), (harder_zombie_img, 3, 3)]

# Plane properties
plane = C.create_image(Canvaswidth // 2, Canvasheight - 50, image=plane_img)
plane_x = Canvaswidth // 2
plane_y = Canvasheight - 50
plane_width = plane_img.width()
plane_height = plane_img.height()

# Text displays
game_font = font.nametofont("TkFixedFont")
game_font.config(size=14)
score_text = C.create_text(10, 10, anchor="nw", font=game_font, fill="white", text="Score: " + str(score))
high_score_text = C.create_text(Canvaswidth - 10, 10, anchor="ne", font=game_font, fill="white", text="High Score: " + str(high_score))
lives_text = C.create_text(Canvaswidth // 2, 10, anchor="n", font=game_font, fill="white", text="Lives: " + str(lives))

# High score file handling
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

# Plane movement
def move_plane(event):
    global plane_x, plane_y
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

# Bullet properties and movement
bullets = []

def shoot_bullet(event):
    global plane_x, plane_y
    for offset in [-10, 0, 10]:  # Shoot 3 bullets with offsets
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

# Zombie properties and movement
zombies = []

def spawn_zombie():
    zombie_img, difficulty, health = choice(zombie_type)
    zombie_x = randrange(0, Canvaswidth)
    zombie = C.create_image(zombie_x, 0, image=zombie_img)
    zombies.append((zombie, difficulty, health))
    move_zombie(zombie, difficulty)
    root.after(Zombie_speed, spawn_zombie)

def move_zombie(zombie, difficulty):
    global score, lives, high_score
    zombie_coords = C.coords(zombie)
    if zombie_coords and zombie_coords[1] < Canvasheight:
        C.move(zombie, 0, difficulty)
        root.after(100 - (difficulty * 10), lambda: move_zombie(zombie, difficulty))
    else:
        if zombie in zombies:
            print(f"Zombie {zombie} reached the bottom, deleting")  # Debug statement
            C.delete(zombie)
            zombies[:] = [(z, d, h) for z, d, h in zombies if z != zombie]
            lose_life()
        return

    # Check for collisions with bullets
    for bullet in bullets:
        bullet_coords = C.coords(bullet)
        zombie_bbox = C.bbox(zombie)
        if bullet_coords and zombie_bbox and check_collision(bullet_coords, zombie_bbox):
            C.delete(bullet)
            if bullet in bullets:
                bullets.remove(bullet)
            zombies[:] = [(z, d, h-1) if z == zombie else (z, d, h) for z, d, h in zombies]
            for z, d, h in zombies:
                if z == zombie and h <= 0:
                    C.delete(zombie)
                    zombies.remove((zombie, difficulty, h))
                    score += 10 * difficulty
                    C.itemconfigure(score_text, text="Score: " + str(score))
                    if score > high_score:
                        high_score = score
                        save_highscore()
                        C.itemconfigure(high_score_text, text="High Score: " + str(high_score))
            break

    # Check for collisions with plane
    plane_coords = C.coords(plane)
    zombie_bbox = C.bbox(zombie)
    if plane_coords and zombie_bbox and check_collision(plane_coords, zombie_bbox):
        if zombie in zombies:
            print(f"Zombie {zombie} hit the plane at {zombie_coords}")  # Debug statement
            C.delete(zombie)
            zombies[:] = [(z, d, h) for z, d, h in zombies if z != zombie]
            lose_life()
            reset_plane()

def check_collision(coords1, bbox2):
    if not coords1 or not bbox2:
        return False
    x1, y1 = coords1[0], coords1[1]
    collision = (bbox2[0] <= x1 <= bbox2[2]) and (bbox2[1] <= y1 <= bbox2[3])
    if collision:
        print(f"Collision detected: {coords1} with {bbox2}")  # Debug statement
    return collision

def lose_life():
    global lives
    lives -= 1
    print(f"Lives left: {lives}")  # Debug statement
    C.itemconfigure(lives_text, text="Lives: " + str(lives))
    if lives <= 0:
        game_over()

def reset_plane():
    global plane_x, plane_y
    plane_x = Canvaswidth // 2
    plane_y = Canvasheight - 50
    C.coords(plane, plane_x, plane_y)
    print(f"Plane reset to {plane_x}, {plane_y}")  # Debug statement

def game_over():
    global score
    messagebox.showinfo("Game Over", f"Final Score: {score}")
    root.destroy()

spawn_zombie()
root.mainloop()
