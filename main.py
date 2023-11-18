import pygame
from pygame.locals import *

"""
Information for training model

Training:
    - state = get_state(game)
    - action = get_move(state) -> model.predict()
    - reward,game_over,score = game.play_step(action)
    - new_state = get_state(game)
    - remember
    - model.train()

Rewards:
    - Win game: +10
    - Pong collision: +5
    - Pong hits wall: -5
    - Lose game: -10

Action:
    - [1,0,0] -> move up 
    - [0,1,0] -> move down
    - [0,0,1] -> paddle stop

State:
 [
    
 ]

Bellman Equation: NewQ(s,a) = Q(s,a) + alpha[R(s,a) + gamma(maxQ'(s',a')) - Q(s,a)]
    - NewQ(s,a) -> New Q value for the state and action
    - Q(s,a) -> Current Q value
    - alpha -> Learning rate
    - R(s,a) -> Reward for taking action at that state
    - gamma -> Discount rate
    - maxQ'(s',a') - Q(s,a) -> Maximum expected future reward given new s' and all possible actions at the new state

Q update rules:
    - Q = model.predict(state)
    - Q(new) = R (reward) + gamma (discount rate) * max(Q(state))

Loss function: loss = (Qnew - Q)^2

"""


# Colors
BLUE = (0,0,255)
WHITE = (255,255,255)
BLACK = (0,0,0)

class Pong:
    def __init__(self,parent_window, window_width, window_height):

        # Display window infromation
        self.parent_window = parent_window
        self.window_width,self.window_height = window_width, window_height

        # Initial values for ball: radius, x, y
        self.radius = 15
        self.x = self.window_width/2-self.radius
        self.y = self.window_height/2-self.radius

        # Velocity (x,y) of ball
        self.vel_x, self.vel_y = 7,7
       

    # Keep ball within window dimensions
    def move(self):
        # If ball hits bottom of screen, bounce up
        if self.x <= 0 + self.radius or self.y >= self.window_height - self.radius:
            self.vel_y *= -1

        # If ball hits top of screen, bounce down
        if self.y <= 0 + self.radius:
            self.vel_y *= -1

        # If ball hits left of screen , return to center of screen and go the other way
        if self.x <= 0 + self.radius:
            self.x, self.y = self.window_width/2-self.radius, self.window_height/2-self.radius
            self.vel_x *= -1
            self.vel_y *= -1

        # If ball hits right of screen , return to center of screen and go the other way
        if self.x >= self.window_width - self.radius:
            self.x, self.y = self.window_width/2-self.radius, self.window_height/2-self.radius
            self.vel_x *= -1
            self.vel_y *= -1

        # Update position of ball 
        self.x += self.vel_x
        self.y += self.vel_y

    def handle_scoring(self, ai_points, player_points):
         # If ball hits left of screen, increase player's points
        if self.x <= 0 + self.radius:
            ai_points += 1

        # If ball hits right of screen, increase AI's points
        if self.x >= self.window_width - self.radius:
            player_points += 1

        return [ai_points,player_points]

    # Paddle/ball collisions
    def handle_collisions(
            self, 
            left_paddle_x,
            left_paddle_y,
            right_paddle_x,
            right_paddle_y,
            paddle_height,
            paddle_width
    ):
        
        # If ball position is within the position (width, height) of the left paddle, reverse ball velocity
        if left_paddle_x <= self.x <= left_paddle_x + paddle_width:
            if left_paddle_y <= self.y <= left_paddle_y + paddle_height:
                self.x = left_paddle_x + paddle_width
                self.vel_x *= -1

        # If ball position is within the position (width, height) of the right paddle, reverse ball velocity
        if right_paddle_x <= self.x <= right_paddle_x + paddle_width:
            if right_paddle_y <= self.y <= right_paddle_y + paddle_height:
                self.x = right_paddle_x - paddle_width
                self.vel_x *= -1


    # Draw ball
    def draw(self):
        pygame.draw.circle(self.parent_window, BLUE, (self.x, self.y), self.radius)


class Paddle:
    def __init__(self,parent_window, window_width, window_height):

        # Display window information
        self.parent_window = parent_window
        self.window_width,self.window_height = window_width, window_height

        # Initial values for paddle
        self.width = 20
        self.height = 120
        self.x = 0
        self.y = self.window_height/2 - self.height/2
        self.vel = 0
        

    # Set a paddle on the left side
    def set_left_paddle(self):
        self.x = 50-self.width/2
        self.is_left_paddle = True

    # set a paddle on the right side
    def set_right_paddle(self):
        self.x = self.window_width - self.width - 50

    def move_up(self):
        self.vel = -5

    def move_down(self):
        self.vel = 5

    def stop(self):
        self.vel = 0

    def move(self):
        self.y += self.vel

        # Keep paddle within window dimensions
        if self.y >= self.window_height - self.height:
            self.y = self.window_height - self.height

        if self.y <= 0:
            self.y = 0

    def draw(self):
        pygame.draw.rect(self.parent_window, WHITE, pygame.Rect(self.x, self.y, self.width, self.height))

    # Return location information for pong to handle paddle/pong collisions
    def get_information(self):
        return [self.x,self.y]


class Game:
    def __init__(self):
        # Initialize module
        pygame.init()

        # Initial values for display window
        self.width=1000
        self.height=600
        self.window = pygame.display.set_mode((self.width,self.height))
        self.font = pygame.font.Font(None, 32)

        # Create title of window
        pygame.display.set_caption('Ping Pong Game')

        # Create paddles
        self.left_paddle = Paddle(self.window, self.width, self.height)
        self.right_paddle = Paddle(self.window, self.width, self.height)

        # Set initial paddle position
        self.left_paddle.set_left_paddle()
        self.right_paddle.set_right_paddle()

        # Create pong
        self.pong = Pong(self.window, self.width, self.height)

        # Initialize values for score
        self.ai_points = 0
        self.player_points = 0
        self.total_points = 2
        self.score = None
        self.score_rect = None

    # reward, game_over, score
    def play_step(action):
        pass

    def play(self):
        # Refill background to clear previous movement
        self.window.fill(BLACK)

        # Draw pong and paddles
        self.pong.draw()
        self.left_paddle.draw()
        self.right_paddle.draw()

        # Functions for pong movement and collisions with paddles
        # 120, 20 represent height and width of paddles respectively
        self.pong.move()

        # Update score
        self.ai_points,self.player_points = self.pong.handle_scoring(self.ai_points,self.player_points)
        
        # Grab location information from paddles
        left_paddle_x,left_paddle_y = self.left_paddle.get_information()
        right_paddle_x,right_paddle_y = self.right_paddle.get_information()

        self.pong.handle_collisions(
            left_paddle_x,
            left_paddle_y,
            right_paddle_x,
            right_paddle_y,
            120,
            20
        )

        # Move paddles
        self.left_paddle.move()
        self.right_paddle.move()

        # Display score
        self.score = self.font.render(f"Score: [{self.ai_points},{self.player_points}]", True, WHITE, BLACK)
        self.window.blit(self.score, (20,20))

        # Update display
        pygame.display.update()            

    def run(self):
        # Main game loop
        run = True
        while run:
            # Functions for display window, and for pong/paddle movement
            game.play()           

            # End game
            if self.ai_points >= self.total_points or self.player_points >= self.total_points:
                # winner = "AI wins!" if self.ai_points >= self.total_points else "Player wins!"
                # result = self.font.render(f"Game over! {winner}", True, WHITE, BLACK)
                # result_rect = result.get_rect()
                # result_rect.center = (self.width //2, self.height//2)

                # self.window.blit(result, result_rect)

                run = False

            # Loop through user actions, i.e., user clicks
            for event in pygame.event.get():
                # End game when player closes window
                if event.type == pygame.QUIT:
                    run = False
                # If user clicks up or down arrow key, change velocity of paddle
                elif event.type == pygame.KEYDOWN:
                    # Up arrow key
                    if event.key == pygame.K_UP:
                        self.right_paddle.move_up()
                    # Down arrow key
                    elif event.key == pygame.K_DOWN:
                        self.right_paddle.move_down()
                    # W key
                    elif event.key == pygame.K_w:
                        self.left_paddle.move_up()
                    # S key
                    elif event.key == pygame.K_s:
                        self.left_paddle.move_down()

                # Once user releases key, stop paddles
                if event.type == pygame.KEYUP:
                    self.left_paddle.stop()
                    self.right_paddle.stop()

if __name__ == "__main__":
    game = Game()
    game.run()
