from rules import is_valid_move
from move_generator import generator
import pygame
import sys
import os

# 1. 初始化 Pygame
pygame.init()

# 2. 窗口与棋盘参数设置
CELL_SIZE = 60  # 每一个棋盘格子的边长（像素）
MARGIN_X, MARGIN_Y = 60, 60  # 棋盘到窗口边缘的距离（留白）
ROWS, COLS = 10, 9  # 中国象棋：10 行横线，9 列竖线

# 计算窗口总宽高
WIDTH = MARGIN_X * 2 + (COLS - 1) * CELL_SIZE
HEIGHT = MARGIN_Y * 2 + (ROWS - 1) * CELL_SIZE

# 颜色定义 (RGB)
BOARD_COLOR = (230, 190, 130)  # 木质黄色背景
LINE_COLOR = (0, 0, 0)  # 网格黑线
RED_COLOR = (200, 30, 30)  # 红色棋子文本/边框颜色
BLACK_COLOR = (30, 30, 30)  # 黑色棋子文本/边框颜色
PIECE_BG_COLOR = (245, 230, 210)  # 棋子圆盘底色（变量名已统一）
SELECT_COLOR = (0, 200, 0)       # 选中状态的高亮绿色框线

# 创建窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("中国象棋 - Xiangqi")

# 3. 字体设置（避开 SysFont 的系统注册表 bug）
# 优先直接使用 Windows 系统自带的楷体文件 simkai.ttf
font_path = "C:/Windows/Fonts/simkai.ttf"
if os.path.exists(font_path):
    font = pygame.font.Font(font_path, 32)
else:
    # 备用方案：如果不是 Windows，尝试黑体 simhei.ttf，或使用默认字体
    font_path_hei = "C:/Windows/Fonts/simhei.ttf"
    if os.path.exists(font_path_hei):
        font = pygame.font.Font(font_path_hei, 32)
    else:
        font = pygame.font.Font(None, 32)

# 棋子名字映射
PIECE_NAMES = {
    'r_r': '車', 'r_n': '馬', 'r_b': '相', 'r_a': '仕', 'r_k': '帥', 'r_c': '砲', 'r_p': '兵',
    'b_r': '車', 'b_n': '馬', 'b_b': '象', 'b_a': '士', 'b_k': '將', 'b_c': '砲', 'b_p': '卒'
}

# 4. 初始化 10x9 棋盘数组 (r=红方, b=黑方)
board = [
    ['b_r', 'b_n', 'b_b', 'b_a', 'b_k', 'b_a', 'b_b', 'b_n', 'b_r'],
    [None,  None,  None,  None,  None,  None,  None,  None,  None ],
    [None,  'b_c', None,  None,  None,  None,  None,  'b_c', None ],
    ['b_p', None,  'b_p', None,  'b_p', None,  'b_p', None,  'b_p'],
    [None,  None,  None,  None,  None,  None,  None,  None,  None ],
    [None,  None,  None,  None,  None,  None,  None,  None,  None ],
    ['r_p', None,  'r_p', None,  'r_p', None,  'r_p', None,  'r_p'],
    [None,  'r_c', None,  None,  None,  None,  None,  'r_c', None ],
    [None,  None,  None,  None,  None,  None,  None,  None,  None ],
    ['r_r', 'r_n', 'r_b', 'r_a', 'r_k', 'r_a', 'r_b', 'r_n', 'r_r']
]

# 交互状态变量
selected_piece = None  # 当前选中的棋子坐标 (r, c)
current_turn = 'r'     # 'r' 代表红方先走，'b' 代表黑方

# 像素坐标转换为棋盘 (row, col)
def get_board_pos(x, y):
    # 允许一定的点击容错判定半径
    for r in range(ROWS):
        for c in range(COLS):
            px = MARGIN_X + c * CELL_SIZE
            py = MARGIN_Y + r * CELL_SIZE
            # 如果点击位置在交叉点 25 像素范围内
            if (x - px) ** 2 + (y - py) ** 2 <= 25 ** 2:
                return r, c
    return None

# 5. 绘制棋盘函数
def draw_board():
    screen.fill(BOARD_COLOR)

    # 绘制 10 条横线
    for r in range(ROWS):
        start_pos = (MARGIN_X, MARGIN_Y + r * CELL_SIZE)
        end_pos = (MARGIN_X + (COLS - 1) * CELL_SIZE, MARGIN_Y + r * CELL_SIZE)
        pygame.draw.line(screen, LINE_COLOR, start_pos, end_pos, 2)

    # 绘制 9 条竖线（中间楚河汉界断开，边缘贯穿）
    for c in range(COLS):
        if c == 0 or c == COLS - 1:
            start_pos = (MARGIN_X + c * CELL_SIZE, MARGIN_Y)
            end_pos = (MARGIN_X + c * CELL_SIZE, MARGIN_Y + (ROWS - 1) * CELL_SIZE)
            pygame.draw.line(screen, LINE_COLOR, start_pos, end_pos, 2)
        else:
            pygame.draw.line(screen, LINE_COLOR,
                             (MARGIN_X + c * CELL_SIZE, MARGIN_Y),
                             (MARGIN_X + c * CELL_SIZE, MARGIN_Y + 4 * CELL_SIZE), 2)
            pygame.draw.line(screen, LINE_COLOR,
                             (MARGIN_X + c * CELL_SIZE, MARGIN_Y + 5 * CELL_SIZE),
                             (MARGIN_X + c * CELL_SIZE, MARGIN_Y + 9 * CELL_SIZE), 2)

    # 绘制九宫格斜线
    pygame.draw.line(screen, LINE_COLOR, (MARGIN_X + 3 * CELL_SIZE, MARGIN_Y),
                     (MARGIN_X + 5 * CELL_SIZE, MARGIN_Y + 2 * CELL_SIZE), 2)
    pygame.draw.line(screen, LINE_COLOR, (MARGIN_X + 5 * CELL_SIZE, MARGIN_Y),
                     (MARGIN_X + 3 * CELL_SIZE, MARGIN_Y + 2 * CELL_SIZE), 2)
    pygame.draw.line(screen, LINE_COLOR, (MARGIN_X + 3 * CELL_SIZE, MARGIN_Y + 7 * CELL_SIZE),
                     (MARGIN_X + 5 * CELL_SIZE, MARGIN_Y + 9 * CELL_SIZE), 2)
    pygame.draw.line(screen, LINE_COLOR, (MARGIN_X + 5 * CELL_SIZE, MARGIN_Y + 7 * CELL_SIZE),
                     (MARGIN_X + 3 * CELL_SIZE, MARGIN_Y + 9 * CELL_SIZE), 2)

# 6. 绘制所有棋子函数
def draw_pieces():
    radius = CELL_SIZE // 2 - 4  # 棋子半径
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece:
                # 交叉点像素坐标
                x = MARGIN_X + c * CELL_SIZE
                y = MARGIN_Y + r * CELL_SIZE

                # 确定红黑颜色
                color = RED_COLOR if piece.startswith('r') else BLACK_COLOR

                # 画棋子圆形背景
                pygame.draw.circle(screen, PIECE_BG_COLOR, (x, y), radius)
                # 画棋子外边框
                pygame.draw.circle(screen, color, (x, y), radius, 2)

                # 如果是当前选中的棋子，画高亮外框
                if selected_piece == (r, c):
                    pygame.draw.circle(screen, SELECT_COLOR, (x, y), radius + 3, 3)

                # 绘制文字
                text_char = PIECE_NAMES[piece]
                text_surface = font.render(text_char, True, color)
                text_rect = text_surface.get_rect(center=(x, y))
                screen.blit(text_surface, text_rect)

def draw_moves():
    if selected_piece is None:
        return
    marked_board = [row[:] for row in board]
    generator(marked_board, selected_piece)
    for r in range(ROWS):
        for c in range(COLS):
            if marked_board[r][c] is True:
                x = MARGIN_X + c * CELL_SIZE
                y = MARGIN_Y + r * CELL_SIZE
                pygame.draw.circle(screen, SELECT_COLOR, (x, y), 6)


# 7. 游戏主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            pos = get_board_pos(mx, my)

            if pos:
                r, c = pos
                clicked_piece = board[r][c]

                # 状态 A：尚未选中任何棋子
                if selected_piece is None:
                    # 只能选择属于当前回合方的棋子
                    if clicked_piece and clicked_piece.startswith(current_turn):
                        selected_piece = (r, c)

                # 状态 B：已经选中了一个棋子，准备落子或改选
                else:
                    sr, sc = selected_piece

                    # 点击了自己的另一个棋子 -> 切换选中
                    if clicked_piece and clicked_piece.startswith(current_turn):
                        selected_piece = (r, c)

                    # 点击了空位或对方棋子 -> 移动/吃子（暂时不限规则）
                    else:
                        if is_valid_move(board,(sr,sc),(r,c)):
                            board[r][c] = board[sr][sc]  # 挪动棋子到新位置
                            board[sr][sc] = None  # 原位置清空
                            selected_piece = None  # 重置选中状态

                            # 轮换行棋方 (红 -> 黑 -> 红)
                            current_turn = 'b' if current_turn == 'r' else 'r'

    draw_board()
    draw_pieces()
    draw_moves()
    pygame.display.flip()

pygame.quit()
sys.exit()