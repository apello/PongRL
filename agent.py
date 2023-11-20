import torch
import random
import numpy as np
from collections import deque
from model import Linear_QNet, QTrainer
from plot import plot
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
        self.model = Linear_QNet(3,256,3)
        self.trainer = QTrainer(self.model, lr=LEARNING_RATE, gamma=self.gamma)

    def get_state(self,game):
        state = [
            game.left_paddle.y,
            game.pong.y,
            abs(game.pong.y-game.left_paddle.y),
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

        # for state, action, reward, next_state, done in mini_sample:
        #     self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)
        

    # Random moves: tradeoff exploration / exploitation
    def get_action(self, state):

        # Epsilon shrinks as number of games grow
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0]

        # Random option
        if random.randint(0,200) < self.epsilon:
            # Random select move: [up, down, stop]
            move = random.randint(0,2)
            final_move[move] = 1

        # Predict movement
        else:
            state0 = torch.tensor(state, dtype=torch.float) # Tensor e.g., [5.0, 2.4, 2.4]
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

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
                agent.model.save()

            print('Game: ', agent.n_games, 'Score: ', score, 'Record: ', record)

            # TODO: plot
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == "__main__":
    train()