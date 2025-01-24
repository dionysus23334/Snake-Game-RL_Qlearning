
import random
import numpy as np
import time

class QLearningSnakeAgent:
    def __init__(self, game, epsilon=0.1, alpha=0.1, gamma=0.9):
        self.game = game
        self.epsilon = epsilon  # 探索的概率
        self.alpha = alpha  # 学习率
        self.gamma = gamma  # 折扣因子
        self.q_table = {}  # 状态-动作 Q 表

    def get_state(self):
        # 创建一个状态表示，可以包括蛇头的位置，蛇的方向，食物的位置
        head_x, head_y = self.game.snake[0]
        food_x, food_y = self.game.food
        return (head_x, head_y, self.game.snake_direction, food_x, food_y)
    
    def get_possible_actions(self):
        return ["Up", "Down", "Left", "Right"]
    
    def choose_action(self, state):
        if random.uniform(0, 1) < self.epsilon:  # 探索
            return random.choice(self.get_possible_actions())
        else:  # 利用
            if state not in self.q_table:
                return random.choice(self.get_possible_actions())
            return max(self.q_table[state], key=self.q_table[state].get)
    
    def update_q_value(self, state, action, reward, next_state):

        # 初始化当前状态在 Q 表中的记录
        if state not in self.q_table:
            self.q_table[state] = {action: 0 for action in self.get_possible_actions()}

        if next_state not in self.q_table:
            self.q_table[next_state] = {action: 0 for action in self.get_possible_actions()}
        
        current_q = self.q_table[state].get(action, 0)
        next_max_q = max(self.q_table[next_state].values())
        new_q = current_q + self.alpha * (reward + self.gamma * next_max_q - current_q)
        self.q_table[state][action] = new_q

    def get_reward(self):
        head_x, head_y = self.game.snake[0]
        if (head_x, head_y) == self.game.food:
            return 1  # 吃到食物
        elif head_x < 0 or head_x >= self.game.WIDTH or head_y < 0 or head_y >= self.game.HEIGHT:
            return -1  # 撞墙
        elif (head_x, head_y) in self.game.snake[1:]:
            return -1  # 撞到自己
        else:
            return 0  # 其他情况没有奖励

    def move_snake(self):
        current_state = self.get_state()
        action = self.choose_action(current_state)
        self.game.change_agent_direction(action)  # 控制蛇的方向
        # game_over = self.game.move_snake()

        # 获取奖励并更新 Q 表
        reward = self.get_reward()  # 获取奖励
        next_state = self.get_state()
        self.update_q_value(current_state, action, reward, next_state)
        # return game_over

    def is_game_over(self):
        head_x, head_y = self.game.snake[0]

        if self.game.snake_direction == "Right":
            new_head = (head_x + self.game.SNAKE_SIZE, head_y)
        elif self.game.snake_direction == "Left":
            new_head = (head_x - self.game.SNAKE_SIZE, head_y)
        elif self.game.snake_direction == "Up":
            new_head = (head_x, head_y - self.game.SNAKE_SIZE)
        elif self.game.snake_direction == "Down":
            new_head = (head_x, head_y + self.game.SNAKE_SIZE)

        self.game.snake = [new_head] + self.game.snake[:-1]

        # 判断蛇是否撞到自己或者墙
        if new_head in self.game.snake[1:] or not (0 <= new_head[0] < self.game.WIDTH and 0 <= new_head[1] < self.game.HEIGHT):
            self.game.game_over()
            return True

        return False

    def print_q_table(self):
        # 打印 Q 表
        print("Q Table:")
        for state, actions in self.q_table.items():
            print(f"State: {state}")
            for action, value in actions.items():
                print(f"  Action: {action} -> Q-value: {value}")

    # 定义训练过程的每一步
    def train(self):
        self.move_snake()  # 让智能体移动一次        
        self.game.root.after(500, self.train)  # 100ms后继续调用train_step

