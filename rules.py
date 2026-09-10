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

    return True