"""
Controls:
    SPACE or UP ARROW -> flap (jump)
    R                 -> restart after game over
    ESC               -> quit
"""

import tkinter as tk
import random

# Window Creation

WIDTH = 400
HEIGHT = 600
FPS_MS = 16  # ~60 frames per second (1000ms / 60 ≈ 16ms per frame)
SKY_BLUE = "#1e1e3c"     
BIRD_COLOR = "#ffdc00"   
PIPE_COLOR = "#00c864"   
GROUND_COLOR = "#c8aa5a"
WHITE = "#ffffff"
RED = "#ff3c3c"


# Game constants
GRAVITY = 0.5
FLAP_STRENGTH = -8
BIRD_SIZE = 20          
PIPE_WIDTH = 60
PIPE_GAP = 150          
PIPE_SPEED = 3
PIPE_SPAWN_MS = 2500    
GROUND_HEIGHT = 40



# Bird
class Bird:
    def __init__(self):
        self.x = WIDTH // 4
        self.y = HEIGHT // 2
        self.velocity = 0

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def get_points(self):
        # Triangle pointing to the right, centered on (x, y)
        # Flattened list because tkinter's create_polygon wants
        # x1, y1, x2, y2, x3, y3 ... in one flat sequence.
        return [
            self.x - BIRD_SIZE, self.y - BIRD_SIZE,
            self.x - BIRD_SIZE, self.y + BIRD_SIZE,
            self.x + BIRD_SIZE, self.y,
        ]

    def get_bounds(self):
        # (x1, y1, x2, y2) bounding box, used for collision detection
        return (self.x - BIRD_SIZE, self.y - BIRD_SIZE,
                self.x + BIRD_SIZE, self.y + BIRD_SIZE)

    def is_dead(self):
        return self.y - BIRD_SIZE <= 0 or self.y + BIRD_SIZE >= HEIGHT - GROUND_HEIGHT


# Pipe (a top rectangle + a bottom rectangle, with a gap)
class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(120, HEIGHT - GROUND_HEIGHT - 120)
        self.passed = False  # used for scoring

    def update(self):
        self.x -= PIPE_SPEED

    def get_top_rect(self):
        # (x1, y1, x2, y2)
        top_height = self.gap_y - PIPE_GAP // 2
        return (self.x, 0, self.x + PIPE_WIDTH, top_height)

    def get_bottom_rect(self):
        bottom_y = self.gap_y + PIPE_GAP // 2
        return (self.x, bottom_y, self.x + PIPE_WIDTH, HEIGHT - GROUND_HEIGHT)

    def off_screen(self):
        return self.x + PIPE_WIDTH < 0



# Obstacle Overlap Check
def rects_overlap(r1, r2):
    x1, y1, x2, y2 = r1
    x3, y3, x4, y4 = r2
    return x1 < x4 and x2 > x3 and y1 < y4 and y2 > y3



# Main game class 
class FlappyBirdGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Flappy Bird (Python / tkinter)")

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                 bg=SKY_BLUE, highlightthickness=0)
        self.canvas.pack()

        # Key bindings
        self.root.bind("<space>", self.on_flap)
        self.root.bind("<Up>", self.on_flap)
        self.root.bind("<r>", self.on_restart)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self.reset_game()
        self.spawn_pipe()   # kick off the repeating pipe-spawn timer
        self.game_loop()    # kick off the repeating game loop

    #Setup & Reset
    def reset_game(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_over = False

    def on_flap(self, event):
        if not self.game_over:
            self.bird.flap()

    def on_restart(self, event):
        if self.game_over:
            self.reset_game()

    # Timers 
    def spawn_pipe(self):
        if not self.game_over:
            self.pipes.append(Pipe(WIDTH))
        # Reschedule itself to run again after PIPE_SPAWN_MS
        self.root.after(PIPE_SPAWN_MS, self.spawn_pipe)

    def game_loop(self):
        if not self.game_over:
            self.update()
        self.draw()
        # Reschedule itself to run again after FPS_MS (this drives the ~60 FPS loop)
        self.root.after(FPS_MS, self.game_loop)

    # -------------------- Update --------------------
    def update(self):
        self.bird.update()

        for pipe in self.pipes:
            pipe.update()
            if not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.x:
                pipe.passed = True
                self.score += 1

        self.pipes = [p for p in self.pipes if not p.off_screen()]

        if self.check_collision():
            self.game_over = True

    def check_collision(self):
        if self.bird.is_dead():
            return True
        bird_box = self.bird.get_bounds()
        for pipe in self.pipes:
            if rects_overlap(bird_box, pipe.get_top_rect()):
                return True
            if rects_overlap(bird_box, pipe.get_bottom_rect()):
                return True
        return False

    #Draw 
    def draw(self):
        self.canvas.delete("all")  # clear everything, then redraw from scratch

        # Pipes
        for pipe in self.pipes:
            x1, y1, x2, y2 = pipe.get_top_rect()
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=PIPE_COLOR, outline="")
            x1, y1, x2, y2 = pipe.get_bottom_rect()
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=PIPE_COLOR, outline="")

        # Bird (triangle)
        self.canvas.create_polygon(self.bird.get_points(), fill=BIRD_COLOR, outline="")

        # Ground
        self.canvas.create_rectangle(0, HEIGHT - GROUND_HEIGHT, WIDTH, HEIGHT,
                                      fill=GROUND_COLOR, outline="")

        # Score
        self.canvas.create_text(WIDTH // 2, 60, text=str(self.score),
                                 fill=WHITE, font=("Helvetica", 40, "bold"))

        # Game over text
        if self.game_over:
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 30, text="GAME OVER",
                                     fill=RED, font=("Helvetica", 36, "bold"))
            self.canvas.create_text(WIDTH // 2, HEIGHT // 2 + 20, text="Press R to restart",
                                     fill=WHITE, font=("Helvetica", 16))


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    game = FlappyBirdGame(root)
    root.mainloop()
