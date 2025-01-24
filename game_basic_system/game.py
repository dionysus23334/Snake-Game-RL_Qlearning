import os
import json
import tkinter as tk
import random
import config
from agent import QLearningSnakeAgent

class SnakeGame:

    def __init__(self, config=config.get_config()):
        # 游戏设置
        self.WIDTH = config['width']
        self.HEIGHT = config['height']
        self.SNAKE_SIZE = config['snake_size']
        self.SPEED = config['speed']  # 控制游戏速度
        self.leaderboard_file = config['leaderboard_file']
        self.leaderboard=[]

        self.root = tk.Tk()
        self.root.title("Snake Game")

        self.full_screen_menu = tk.Frame(self.root, width=self.WIDTH, height=self.HEIGHT, bg="black")
        self.full_screen_menu.pack_propagate(False)
        self.full_screen_menu.pack()

        self.canvas = tk.Canvas(self.root, width=self.WIDTH, height=self.HEIGHT, bg="black")
        self.score_label = tk.Label(self.root, text="得分: 0", font=("Arial", 14))

        self.snake = config['snake']
        self.snake_direction = config['snake_direction']
        self.food = config['food']
        self.score = config['score']
        self.move_task = config['move_task']

        self.game_menu = None

    def reset(self,config=config.get_config()):
        self.SNAKE_SIZE = config['snake_size']
        self.SPEED = config['speed']  # 控制游戏速度
        self.snake = config['snake']
        self.snake_direction = config['snake_direction']
        self.food = config['food']
        self.score = config['score']
        self.move_task = config['move_task']

    # 加载排行榜数据
    def load_leaderboard(self):
        if os.path.exists(self.leaderboard_file):
            with open(self.leaderboard_file, "r") as file:
                self.leaderboard = json.load(file)
        else:
            self.leaderboard = []

    # 保存排行榜数据
    def save_leaderboard(self):
        with open(self.leaderboard_file, "w") as file:
            json.dump(self.leaderboard, file)

    # 更新分数
    def update_score(self):
        if hasattr(self, 'score_label') and self.score_label.winfo_exists():
            self.score_label.config(text=f"得分: {self.score}")
        else:
            self.score_label = tk.Label(self.root, text=f"得分: {self.score}", font=("Arial", 14))
            self.score_label.pack()
    # 创建食物
    def create_food(self):
        food_x = random.randint(0, (self.WIDTH - self.SNAKE_SIZE) // self.SNAKE_SIZE) * self.SNAKE_SIZE
        food_y = random.randint(0, (self.HEIGHT - self.SNAKE_SIZE) // self.SNAKE_SIZE) * self.SNAKE_SIZE
        self.food = (food_x, food_y)
        self.canvas.create_rectangle(food_x, food_y, food_x + self.SNAKE_SIZE, food_y + self.SNAKE_SIZE, fill="red", tags="food")

    # 画蛇
    def draw_snake(self):
        self.canvas.delete("snake")
        for segment in self.snake:
            x, y = segment
            self.canvas.create_rectangle(x, y, x + self.SNAKE_SIZE, y + self.SNAKE_SIZE, fill="green", tags="snake")
    
    # 蛇移动逻辑
    def move_snake(self):
        head_x, head_y = self.snake[0]

        if self.snake_direction == "Right":
            new_head = (head_x + self.SNAKE_SIZE, head_y)
        elif self.snake_direction == "Left":
            new_head = (head_x - self.SNAKE_SIZE, head_y)
        elif self.snake_direction == "Up":
            new_head = (head_x, head_y - self.SNAKE_SIZE)
        elif self.snake_direction == "Down":
            new_head = (head_x, head_y + self.SNAKE_SIZE)

        self.snake = [new_head] + self.snake[:-1]

        # 判断蛇是否撞到自己或者墙
        if new_head in self.snake[1:] or not (0 <= new_head[0] < self.WIDTH and 0 <= new_head[1] < self.HEIGHT):
            self.game_over()
            return True

        # 判断蛇是否吃到食物
        if new_head == self.food:
            self.snake.append(self.snake[-1])  # 增加蛇的长度
            self.score += 1
            self.update_score()
            self.canvas.delete("food")  # 删除旧的食物
            self.create_food()  # 创建新的食物

        self.draw_snake()
        self.move_task = self.root.after(self.SPEED, self.move_snake)  # 重新设置定时器

    # 游戏结束
    def game_over(self):

        self.canvas.create_text(self.WIDTH / 2, self.HEIGHT / 2, text="游戏结束", fill="white", font=('Arial', 30), tags="game_over")
        self.canvas.create_text(self.WIDTH / 2, self.HEIGHT / 2 + 40, text=f"最终得分: {self.score}", fill="white", font=('Arial', 20), tags="game_over")
        
        # 更新排行榜
        self.leaderboard.append(self.score)
        self.leaderboard.sort(reverse=True)  # 降序排列
        
        # 保证排行榜最多有10个得分
        if len(self.leaderboard) > 10:
            self.leaderboard = self.leaderboard[:10]

        # 保存排行榜
        self.save_leaderboard()

    # 控制蛇的方向
    def change_direction(self, event):
        if event.keysym == "Left" or event.keysym == "a":
            if self.snake_direction != "Right":
                self.snake_direction = "Left"
        elif event.keysym == "Right" or event.keysym == "d":
            if self.snake_direction != "Left":
                self.snake_direction = "Right"
        elif event.keysym == "Up" or event.keysym == "w":
            if self.snake_direction != "Down":
                self.snake_direction = "Up"
        elif event.keysym == "Down" or event.keysym == "s":
            if self.snake_direction != "Up":
                self.snake_direction = "Down"

    # 创建重新开始和返回菜单按钮
    def show_game_menu(self):

        self.game_menu = tk.Menu(self.root)
        self.root.config(menu=self.game_menu)

        # 添加菜单项
        self.game_menu.add_command(label="重新开始", command=self.restart_game)
        self.game_menu.add_command(label="返回菜单", command=self.return_to_menu)


    # 返回到全屏菜单
    def return_to_menu(self,config=config.get_config()):

        # 取消之前的定时器任务
        if self.move_task:
            self.root.after_cancel(self.move_task)

        # 清除画布上的所有元素
        self.canvas.delete("all")
        # 重置游戏相关变量
        self.snake = config['snake']
        self.snake_direction = config['snake_direction']
        self.score = config['score']
        self.update_score()

        self.canvas.pack_forget()  # 隐藏游戏画布
        self.score_label.pack_forget()  # 隐藏分数标签

        self.show_full_screen_menu() 

        self.root.config(menu=None)

    # 重新开始游戏
    def restart_game(self,config=config.get_config()):
        # 删除旧的游戏结束提示文本和食物
        self.canvas.delete("game_over")
        self.canvas.delete("food")
        
        # 取消之前的定时器任务
        if self.move_task:
            self.root.after_cancel(self.move_task)
        
        # 重新初始化游戏
        self.snake = config['snake']
        self.snake_direction = config['snake_direction']
        self.score = config['score']
        self.update_score()
        self.create_food()
        self.move_snake()  # 重新开始游戏
        self.show_game_menu()  # 显示游戏菜单

    def restart_agent_game(self):
        self.restart_game()

    # 查看排行榜
    def show_leaderboard(self):
        leaderboard_window = tk.Toplevel(self.root)
        leaderboard_window.title("排行榜")
        leaderboard_window.geometry("300x300")
        
        leaderboard_text = tk.Label(leaderboard_window, text="得分排行榜", font=("Arial", 20))
        leaderboard_text.pack(pady=10)

        # 显示排行榜
        for index, score in enumerate(self.leaderboard, start=1):
            self.score_label = tk.Label(leaderboard_window, text=f"{index}. {score}", font=("Arial", 14))
            self.score_label.pack()

    # 创建智能体模式函数
    def ai_mode(self):
        
        print("进入智能体模式，智能体将在此控制蛇的行为。")
        agent = QLearningSnakeAgent(self)

        # 进入游戏画面
        self.full_screen_menu.pack_forget()  # 隐藏菜单
        self.canvas.pack()  # 显示游戏画布

        # 如果没有 score_label 或者 score_label 被销毁了，重新创建
        if not hasattr(self, 'score_label') or not self.score_label.winfo_exists():
            self.score_label = tk.Label(self.root, text="得分: 0", font=("Arial", 14))
            self.score_label.pack()  # 显示得分标签
        else:
            self.score_label.pack()  # 如果已存在，直接显示

        self.create_food()  # 创建食物
        self.move_snake()  # 启动蛇的移动
        self.show_game_menu()  # 显示游戏菜单（暂停游戏时用）
        
        # 开始智能体训练
        agent.train()


    # 显示全屏菜单
    def show_full_screen_menu(self):
        self.full_screen_menu.pack()
        self.canvas.pack_forget()
        self.score_label.pack_forget()

        # 创建开始游戏和退出的按钮
        start_button = tk.Button(self.full_screen_menu, text="开始游戏", command=self.start_game, font=("Arial", 20))
        start_button.place(relx=0.5, rely=0.2, anchor="center")
        
        leaderboard_button = tk.Button(self.full_screen_menu, text="排行榜", command=self.show_leaderboard, font=("Arial", 20))
        leaderboard_button.place(relx=0.5, rely=0.4, anchor="center")

        ai_mode_button = tk.Button(self.full_screen_menu, text="智能体模式", command=self.ai_mode, font=("Arial", 20))
        ai_mode_button.place(relx=0.5, rely=0.6, anchor="center")

        quit_button = tk.Button(self.full_screen_menu, text="退出游戏", command=self.root.quit, font=("Arial", 20))
        quit_button.place(relx=0.5, rely=0.8, anchor="center")
        self.root.config(menu=None)
        
    # 启动游戏
    def start_game(self):
        self.full_screen_menu.pack_forget()  # 隐藏菜单
        self.canvas.pack()  # 显示游戏画布

        # 如果没有 score_label 或者 score_label 被销毁了，重新创建
        if not hasattr(self, 'score_label') or not self.score_label.winfo_exists():
            self.score_label = tk.Label(self.root, text="得分: 0", font=("Arial", 14))
            self.score_label.pack()  # 显示得分标签
        else:
            self.score_label.pack()  # 如果已存在，直接显示

        self.create_food()  # 创建食物
        self.move_snake()  # 启动蛇的移动
        self.show_game_menu()  # 显示游戏菜单（暂停游戏时用）

    def run(self):
        # 初始化游戏
        self.load_leaderboard()  # 加载排行榜
        self.show_full_screen_menu()

        # 绑定键盘事件
        self.root.bind("<Left>", self.change_direction)
        self.root.bind("<Right>", self.change_direction)
        self.root.bind("<Up>", self.change_direction)
        self.root.bind("<Down>", self.change_direction)
        self.root.bind("a", self.change_direction)
        self.root.bind("d", self.change_direction)
        self.root.bind("w", self.change_direction)
        self.root.bind("s", self.change_direction)

        # 调用 focus_set 来确保键盘事件生效
        self.canvas.focus_set()

        # 开始游戏
        self.root.mainloop()

    def change_agent_direction(self, direction):
        if direction == "Left" and self.snake_direction != "Right":
            self.snake_direction = "Left"
        elif direction == "Right" and self.snake_direction != "Left":
            self.snake_direction = "Right"
        elif direction == "Up" and self.snake_direction != "Down":
            self.snake_direction = "Up"
        elif direction == "Down" and self.snake_direction != "Up":
            self.snake_direction = "Down"


if __name__ == "__main__":

    snakegame=SnakeGame()
    snakegame.run()
