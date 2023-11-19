import torch
import random
import numpy as np
from collections import deque
from game import Game

# Maximum memory size
MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LEARNING_RATE = 0.001

class Agent:
    def __init__(self):
        self.n_games = 0

        # Randomness
        self.epsilon = 0

        # Discount rate
        self.gamma = 0
        self.memory = deque(maxlen=MAX_MEMORY)

        # TODO: model, trainer

    def get_state(self,game):
        pass

    def remember(self, state, action, reward, next_state, done):
        pass

    def train_long_memory(self):
        pass

    def train_short_memory(self, state, action, reward, next_state, done):
        pass

    def get_action(self, state):
        pass

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0

    agent = Agent()
    game = Game()

    while True:
        # Get previous state
        state_old = agent.get_state(game)

        # Get move based on previous state
        final_move = agent.get_action(state_old)

        # Preform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # Train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # Remember progress
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # Train long memory
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score

                # agent.model.save()

            print('Game: ', agent.n_games, 'Score: ', score, 'Record: ', record)

            # TODO: plot


if __name__ == "__main__":
    train()