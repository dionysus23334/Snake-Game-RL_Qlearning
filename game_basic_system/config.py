


def get_config():
    return {
        'width':600,
        'height':400,
        'snake_size':10,
        'speed':100,
        'snake':[(200, 200), (190, 200), (180, 200)],  # 初始蛇身
        'snake_direction': "Right", # 初始蛇的运动方向
        'food':None, # 初始食物
        'score':0, # 初始分数
        'move_task':None, # 用于存储 move_snake 的定时任务
        "leaderboard_file":"../leaderboard.json" # 榜单的文件路径
    }

