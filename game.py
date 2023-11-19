import pygame
from pygame.locals import *
import random
from enum import Enum
import numpy as np

# Initialize module
pygame.init()
font = pygame.font.Font(None, 32)

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
    - Pass opponent's paddle: +10
    - Ball passes your paddle: -10

Actions:
    - UP: [1,0,0]
    - DOWN: [0,1,0]
    - STOP: [0,0,1]

States (taken from Gymasium Atari Pong):
    - 0:NOOP
    - 1:FIRE
    - 2:RIGHT
    - 3:LEFT
    - 4:RIGHTFIRE
    - 5:LEFTFIRE


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


"""
    - reset()
    - reward 
    - play(action) -> next_action
    - frame_iteration

"""

# class Direction(Enum):
#     STOP = 0
#     UP = 1
#     DOWN = 2

# RBB colors
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

        # If ball hits left or right of screen, return to middle of screen and go the other way
        if self.x <= 0 + self.radius or self.x >= self.window_width - self.radius:
            self.x = self.window_width/2-self.radius

            # Random height value
            self.y = random.randint(self.radius, self.window_height-self.radius)
            self.vel_x *= -1
            self.vel_y *= -1

        # Update position of ball 
        self.x += self.vel_x
        self.y += self.vel_y

    def _is_boundary_collision(self):
        if self.x <= 0 + self.radius:
            return True
        
        return False
    
    def _is_opponent_collision(self):
        if self.x >= self.window_width - self.radius:
            return True
        
        return False

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

        # Initial values for display window
        self.width=1000
        self.height=600
        self.window = pygame.display.set_mode((self.width,self.height))

        # Create title of window
        pygame.display.set_caption('Ping Pong Game')

        self.reset()

    def reset(self):
         # Create paddles
        self.left_paddle = Paddle(self.window, self.width, self.height)
        self.right_paddle = Paddle(self.window, self.width, self.height)

        # Set initial paddle position
        self.left_paddle.set_left_paddle()
        self.right_paddle.set_right_paddle()

        # Create pong
        self.pong = Pong(self.window, self.width, self.height)

        # Initialize values for score
        self.ai_score = 0
        self.player_score = 0
        # self.total_points = 0

        # Initialize iteration count
        self.frame_iteration = 0

    def _move(self,action):
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

        # Functions for pong movement and collisions with paddles
        # 120, 20 represent height and width of paddles respectively
        self.pong.move()

        # [UP, DOWN, STOP]
        if np.array_equal(action, [1,0,0]):
            self.left_paddle.move_up()
        elif np.array_equal(action, [0,1,0]):
            self.left_paddle.move_down()
        else:
            self.left_paddle.stop()

    def _update_ui(self):
        # Refill background to clear previous movement
        self.window.fill(BLACK)

        # Draw pong and paddles
        self.pong.draw()
        self.left_paddle.draw()
        self.right_paddle.draw()

        # Display score
        self.score = font.render(f"Score: [{self.ai_score},{self.player_score}]", True, WHITE, BLACK)
        self.window.blit(self.score, (20,20))

        # Display iteration
        self.iteration = font.render(f"Iteration: {self.frame_iteration}", True, WHITE, BLACK)
        self.window.blit(self.iteration, (self.width-200, 20))

        # Update display
        pygame.display.update()            

    def play_step(self,action):
        # Increment frame interation
        self.frame_iteration += 1

        # Loop through user actions, i.e., user clicks
        for event in pygame.event.get():
            # End game when player closes window
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            # If user clicks up or down arrow key, change velocity of paddle
            elif event.type == pygame.KEYDOWN:
                # Up arrow key
                if event.key == pygame.K_UP:
                    self.right_paddle.move_up()
                # Down arrow key
                elif event.key == pygame.K_DOWN:
                    self.right_paddle.move_down()

            # Once user releases key, stop paddles
            if event.type == pygame.KEYUP:
                self.right_paddle.stop()


        # Functions for pong/paddle movement
        # action = [0,0,1]
        self._move(action)        

        # Initialize value
        reward = 0
        game_over = False

        # Check if game is over
        if self.pong._is_boundary_collision():
            self.player_score += 1
            reward = -10
            game_over = True
            return reward, game_over, self.ai_score
        
        if self.pong._is_opponent_collision():
            self.ai_score += 1
            reward = 10

        self._update_ui()
            
        return reward, game_over, self.ai_score

# if __name__ == "__main__":
#     game = Game()

#     while True:
#         reward,game_over,score = game.play_step(True)
#         if game_over == True:
#             break
    
#     pygame.quit()
