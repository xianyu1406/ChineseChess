"""
game_logic.py
中国象棋游戏逻辑：将军检测、合法走法过滤、将死/困毙判定。
被将军时只能走能解将的棋；将死或困毙直接判负。
"""

from move_generator import generator

ROWS, COLS = 10, 9


def find_king(board, side):
    """找到某方将/帅的位置，返回 (r, c)；找不到返回 None。"""
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece and piece[0] == side and piece[-1] == 'k':
                return (r, c)
    return None


def is_in_check(board, side):
    """
    判断 side 方是否被将军。
    遍历对方所有棋子，只要有一枚能攻击到 side 的将/帅即为将军。
    将/帅已被吃掉也视为被将军（极端情况）。
    """
    king_pos = find_king(board, side)
    if king_pos is None:
        return True

    opponent = 'b' if side == 'r' else 'r'
    kr, kc = king_pos

    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if piece and piece[0] == opponent:
                marked = [row[:] for row in board]
                generator(marked, (r, c))
                if marked[kr][kc] is True:
                    return True
    return False


def get_legal_moves(board, side, disabled_pieces=None, piece_id_map=None):
    """
    获取 side 方全部合法走法。
    合法 = 棋子走法规则允许 且 走完后己方不被将军 且 棋子未被强制停用。

    参数:
        board: 10x9 棋盘
        side: 'r' 或 'b'
        disabled_pieces: 被强制停用的棋子 ID 集合
        piece_id_map: 当前位置 -> 棋子唯一 ID 的映射

    返回:
        [((from_r, from_c), (to_r, to_c)), ...]
    """
    if disabled_pieces is None:
        disabled_pieces = set()

    legal = []
    for r in range(ROWS):
        for c in range(COLS):
            piece = board[r][c]
            if not piece or piece[0] != side:
                continue

            # 被强制停用的棋子不能走
            if piece_id_map and (r, c) in piece_id_map:
                if piece_id_map[(r, c)] in disabled_pieces:
                    continue

            # 生成该棋子所有规则允许的落点
            marked = [row[:] for row in board]
            generator(marked, (r, c))

            for er in range(ROWS):
                for ec in range(COLS):
                    if marked[er][ec] is True:
                        # 模拟走棋
                        nb = [row[:] for row in board]
                        nb[er][ec] = nb[r][c]
                        nb[r][c] = None
                        # 走完后己方不被将军才算合法
                        if not is_in_check(nb, side):
                            legal.append(((r, c), (er, ec)))
    return legal


def is_checkmate(board, side, disabled_pieces=None, piece_id_map=None):
    """将死：被将军 且 没有任何合法走法。"""
    if not is_in_check(board, side):
        return False
    return len(get_legal_moves(board, side, disabled_pieces, piece_id_map)) == 0


def is_stalemate(board, side, disabled_pieces=None, piece_id_map=None):
    """困毙：未被将军 但 没有任何合法走法。中国象棋中困毙判负。"""
    if is_in_check(board, side):
        return False
    return len(get_legal_moves(board, side, disabled_pieces, piece_id_map)) == 0
