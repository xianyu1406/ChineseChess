#具体的子规则
def is_car_rule(board,start,end):
    sr,sc = start
    er,ec = end
    if sr == er:
        start_col = min(sc,ec)
        end_col = max(sc,ec)
        for c in range(start_col + 1,end_col):
            if board[sr][c] is not None:
                return False
        return True
    if sc == ec:
        start_row = min(sr,er)
        end_row = max(sr,er)
        for r in range(start_row + 1,end_row):
            if board[r][sc] is not None:
                return False
        return True
    return False

#分函数
def is_inside(x,y):
    return 0 <= x < 10 and 0 <= y < 9
def has_piece(board,sr,sc):
    return board[sr][sc] is not None
def is_same_side(board,start,end):
    sr, sc = start
    er, ec = end

    piece = board[sr][sc]
    target = board[er][ec]
    if target is None:
        return False
    return piece[0] == target[0]
def check_piece_rule(board,start,end):
    if board[start[0]][start[1]][-1] == 'r':
        return is_car_rule(board,start,end)
    return False
# 总函数
def is_valid_move(board,start,end):
    sr,sc = start
    er,ec = end
    if not is_inside(sr,sc):
        return False
    if not is_inside(er,ec):
        return False
    if not has_piece(board,sr,sc):
        return False
    if is_same_side(board,start,end):
        return False
    if not check_piece_rule(board,start,end):
        return False
    return True