from move_generator import generator

# 找当前所有合法走法
def generate_all_moves(board,side):
    moves = []

    for sr in range(10):
        for sc in range(9):
            piece = board[sr][sc]
            if piece is None:
                continue
            if piece[0] != side:
                continue
            start = (sr, sc)
            marked_board = [row[:] for row in board]
            generator(marked_board, start)

            for er in range(10):
                for ec in range(9):
                    if marked_board[er][ec] is True:
                        end = (er, ec)
                        moves.append((start, end))
    return moves


# 局面评价函数
def evaluate(board):
    piece_value = {
        'r': 500, 'n': 300, 'b': 200, 'a': 200,
        'k': 10000, 'c': 300, 'p': 100
    }
    score = 0

    for r in range(10):
        for c in range(9):
            piece = board[r][c]
            if piece is None:
                continue

            value = piece_value[piece[-1]]
            if piece[0] == 'r':
                score += value
            else:
                score -= value

    return score

# 二层深度搜索
def search_two_step(board,side):
    if side == 'r':
        other_side = 'b'
    else:
        other_side = 'r'
    best_move = None
    best_score = -float('inf')
    for start, end in generate_all_moves(board, side):
        sr, sc = start
        er, ec = end

        # 能直接吃掉对方将帅，就选这步
        if board[er][ec] == other_side + '_k':
            return start, end

        # 在副本上试走自己这一步
        new_board = [row[:] for row in board]
        new_board[er][ec] = new_board[sr][sc]
        new_board[sr][sc] = None

        # 生成自己走之后对方所有走法
        other_moves = generate_all_moves(new_board, other_side)
        if not other_moves:
            return start, end

        # 对方选让我方得分最低的那一步
        worst_score = float('inf')
        for other_start, other_end in other_moves:
            other_sr, other_sc = other_start
            other_er, other_ec = other_end

            reply_board = [row[:] for row in new_board]
            reply_board[other_er][other_ec] = reply_board[other_sr][other_sc]
            reply_board[other_sr][other_sc] = None

            score = evaluate(reply_board)
            if side == 'b':
                score = -score

            if score < worst_score:
                worst_score = score

        # 比较每种走法的最坏结果，选其中得分最高的
        if worst_score > best_score:
            best_score = worst_score
            best_move = (start, end)

    return best_move