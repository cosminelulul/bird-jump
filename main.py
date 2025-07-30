import sys
import turtle
import random
import os


# ====================== #
# === CONFIGURATIONS === #
# ====================== #


GRAVITY = -0.6
FLAP_STRENGTH = 10
PIPE_SPEED = 5
PIPE_GAP = 150
PIPE_WIDTH = 60
PIPE_INTERVAL = 105  # frames
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# ====================== #
# ===== GAME CORE ===== #
# ====================== #

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
       base_path = sys._MEIPASS
    else:
         base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)



# ====================== #
# ====== SPRITES ======= #
# ====================== #


bird_sprite = get_resource_path("assets/Bird.gif")
skyday_bg = get_resource_path("assets/Sky1.gif")
skynight_bg = get_resource_path("assets/Sky2.gif")


# === Classes ===

class Bird:
    def __init__(self, shape_path):
        self.y_velocity = 0
        self.sprite = turtle.Turtle()
        self.sprite.shape(shape_path)
        self.sprite.penup()
        self.sprite.goto(-100, 0)

    def flap(self):
        self.y_velocity = FLAP_STRENGTH

    def update(self):
        self.y_velocity += GRAVITY
        y = self.sprite.ycor() + self.y_velocity
        self.sprite.sety(y)

    def is_colliding(self, pipes):
        for pipe in pipes:
            if pipe.is_colliding(self.sprite):
                return True
        return self.sprite.ycor() < -SCREEN_HEIGHT // 2 or self.sprite.ycor() > SCREEN_HEIGHT // 2

class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(-100, 100)
        self.upper = turtle.Turtle()
        self.lower = turtle.Turtle()
        for t in [self.upper, self.lower]:
            t.shape("square")
            t.color("green")
            t.shapesize(stretch_wid=20, stretch_len=PIPE_WIDTH // 20)
            t.penup()
        self.update_positions()

    def update_positions(self):
        self.upper.goto(self.x, self.gap_y + PIPE_GAP // 2 + 200)
        self.lower.goto(self.x, self.gap_y - PIPE_GAP // 2 - 200)

    def move(self):
        self.x -= PIPE_SPEED
        self.update_positions()

    def is_offscreen(self):
        return self.x < -SCREEN_WIDTH // 2 - PIPE_WIDTH

    def is_colliding(self, bird_sprite):
        bx, by = bird_sprite.xcor(), bird_sprite.ycor()
        return (
            abs(self.x - bx) < PIPE_WIDTH // 2 + 10 and
            (by > self.gap_y + PIPE_GAP // 2 or by < self.gap_y - PIPE_GAP // 2)
        )

class Game:
    def __init__(self):
        self.window = turtle.Screen()
        self.window.title("Flappy Turtle")
        self.window.bgcolor("skyblue")
        self.window.setup(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.window.tracer(0)

        canvas = self.window.getcanvas()
        root = canvas.winfo_toplevel()
        root.resizable(False, False)

        self.bird_sprite = bird_sprite
        self.window.register_shape(self.bird_sprite)
        self.bird = Bird(self.bird_sprite)
        self.backgrounds = [skyday_bg, skynight_bg]
        self.pipes = []
        self.frame_count = 0
        self.score = 0
        self.highscore = self.load_highscore()
        self.running = False

        for bg in self.backgrounds:
            self.window.register_shape(bg)
        self.window.register_shape(self.bird_sprite)

        self.score_display = turtle.Turtle()
        self.score_display.hideturtle()
        self.score_display.penup()
        self.score_display.goto(0, SCREEN_HEIGHT // 2 - 50)
        self.score_display.color("black")

        self.start_text = turtle.Turtle()
        self.start_text.hideturtle()
        self.start_text.penup()
        self.start_text.color("black")
        self.start_text.write("Press SPACE to Start", align="center", font=("Arial", 24, "bold"))

        self.window.listen()
        self.window.onkey(self.start_game, "space")

    def on_flap(self, x=None, y=None):
        if self.running:
            self.bird.flap()

    def load_highscore(self):
        if os.path.exists("highscore.txt"):
            with open("highscore.txt") as f:
                return int(f.read().strip())
        return 0

    def save_highscore(self):
        with open("highscore.txt", "w") as f:
            f.write(str(self.highscore))

    def start_game(self):
        self.start_text.clear()
        self.running = True
        self.bird.sprite.goto(-100, 0)
        self.bird.y_velocity = 0
        self.pipes.clear()
        self.frame_count = 0
        self.window.bgpic(random.choice(self.backgrounds))
        self.score = 0
        self.window.onkey(self.on_flap, "space")
        self.window.onclick(self.on_flap)
        self.game_loop()

    def game_loop(self):
        if not self.running:
            return

        self.bird.update()

        if self.frame_count % PIPE_INTERVAL == 0:
            self.pipes.append(Pipe(SCREEN_WIDTH // 2 + PIPE_WIDTH))

        for pipe in self.pipes:
            pipe.move()

        self.pipes = [pipe for pipe in self.pipes if not pipe.is_offscreen()]

        if self.bird.is_colliding(self.pipes):
            self.game_over()
            return

        for pipe in self.pipes:
            if not hasattr(pipe, 'passed') and pipe.x < self.bird.sprite.xcor():
                pipe.passed = True
                self.score += 1
                if self.score > self.highscore:
                    self.highscore = self.score

        self.update_score()
        self.window.update()
        self.frame_count += 1
        self.window.ontimer(self.game_loop, 20)

    def update_score(self):
        self.score_display.clear()
        self.score_display.write(f"Score: {self.score}  Highscore: {self.highscore}", align="center", font=("Arial", 16, "bold"))

    def game_over(self):
        self.running = False
        self.save_highscore()
        self.score_display.goto(0, 0)
        self.score_display.write("Game Over! Press SPACE to Restart", align="center", font=("Arial", 18, "bold"))

        # Hide old pipes and bird
        for pipe in self.pipes:
            pipe.upper.hideturtle()
            pipe.lower.hideturtle()
        self.pipes.clear()

        self.bird.sprite.hideturtle()

        self.window.ontimer(self.reset_game, 1)

    def reset_game(self):
        self.bird = Bird(self.bird_sprite)
        self.window.bgpic(random.choice(self.backgrounds))
        self.score_display.clear()
        self.score_display.goto(0, SCREEN_HEIGHT // 2 - 50)
        self.start_text.write("Press SPACE to Start", align="center", font=("Arial", 24, "bold"))
        self.window.onkey(self.start_game, "space")


if __name__ == "__main__":
    Game()
    turtle.mainloop()
