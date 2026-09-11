from move_rules import is_valid_move

ROWS, COLS = 10, 9


def generator(board, start):
    sr, sc = start
    if not (0 <= sr < ROWS and 0 <= sc < COLS):
        return
    if board[sr][sc] is None:
        return

    if board[sr][sc][-1] == 'r':
        car_generator(board, start)
    if board[sr][sc][-1] == 'n':
        horse_generator(board, start)
    if board[sr][sc][-1] == 'b':
        elephant_generator(board, start)
    if board[sr][sc][-1] == 'a':
        guard_generator(board, start)
    if board[sr][sc][-1] == 'k':
        king_generator(board, start)
    if board[sr][sc][-1] == 'c':
        cannon_generator(board, start)
    if board[sr][sc][-1] == 'p':
        pawn_generator(board, start)



def car_generator(board, start):
    original_board = [row[:] for row in board]
    sr, sc = start

    # 沿上下左右四个方向走，遇到第一枚棋子就停止。
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        r, c = sr + dr, sc + dc
        while 0 <= r < ROWS and 0 <= c < COLS:
            end = (r, c)
            if is_valid_move(original_board, start, end):
                board[r][c] = True
            if original_board[r][c] is not None:
                break
            r += dr
            c += dc


def horse_generator(board, start):
    original_board = [row[:] for row in board]
    sr, sc = start

    if sr + 1 < ROWS and original_board[sr + 1][sc] is None:
        end = (sr + 2, sc + 1)
        end1 = (sr + 2, sc - 1)
        if is_valid_move(original_board, start, end):
            board[end[0]][end[1]] = True
        if is_valid_move(original_board, start, end1):
            board[end1[0]][end1[1]] = True

    if sr - 1 >= 0 and original_board[sr - 1][sc] is None:
        end = (sr - 2, sc + 1)
        end1 = (sr - 2, sc - 1)
        if is_valid_move(original_board, start, end):
            board[end[0]][end[1]] = True
        if is_valid_move(original_board, start, end1):
            board[end1[0]][end1[1]] = True

    if sc + 1 < COLS and original_board[sr][sc + 1] is None:
        end = (sr + 1, sc + 2)
        end1 = (sr - 1, sc + 2)
        if is_valid_move(original_board, start, end):
            board[end[0]][end[1]] = True
        if is_valid_move(original_board, start, end1):
            board[end1[0]][end1[1]] = True

    if sc - 1 >= 0 and original_board[sr][sc - 1] is None:
        end = (sr + 1, sc - 2)
        end1 = (sr - 1, sc - 2)
        if is_valid_move(original_board, start, end):
            board[end[0]][end[1]] = True
        if is_valid_move(original_board, start, end1):
            board[end1[0]][end1[1]] = True


def elephant_generator(board, start):
    original_board = [row[:] for row in board]
    sr, sc = start
    side = original_board[sr][sc][0]

    # 检验四个方向的象眼；红相在第 5～9 行，黑象在第 0～4 行。
    if sr - 1 >= 0 and sc - 1 >= 0 and original_board[sr - 1][sc - 1] is None:
        end = (sr - 2, sc - 2)
        if (side == 'r' and end[0] >= 5) or (side == 'b' and end[0] <= 4):
            if is_valid_move(original_board, start, end):
                board[end[0]][end[1]] = True

    if sr - 1 >= 0 and sc + 1 < COLS and original_board[sr - 1][sc + 1] is None:
        end = (sr - 2, sc + 2)
        if (side == 'r' and end[0] >= 5) or (side == 'b' and end[0] <= 4):
            if is_valid_move(original_board, start, end):
                board[end[0]][end[1]] = True

    if sr + 1 < ROWS and sc - 1 >= 0 and original_board[sr + 1][sc - 1] is None:
        end = (sr + 2, sc - 2)
        if (side == 'r' and end[0] >= 5) or (side == 'b' and end[0] <= 4):
            if is_valid_move(original_board, start, end):
                board[end[0]][end[1]] = True

    if sr + 1 < ROWS and sc + 1 < COLS and original_board[sr + 1][sc + 1] is None:
        end = (sr + 2, sc + 2)
        if (side == 'r' and end[0] >= 5) or (side == 'b' and end[0] <= 4):
            if is_valid_move(original_board, start, end):
                board[end[0]][end[1]] = True


def guard_generator(board, start):
    original_board = [row[:] for row in board]
    sr, sc = start
    side = original_board[sr][sc][0]

    # 士、仕只在己方九宫内斜走一步。
    for dr, dc in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        end = (sr + dr, sc + dc)
        if not 3 <= end[1] <= 5:
            continue
        if side == 'r' and not 7 <= end[0] <= 9:
            continue
        if side == 'b' and not 0 <= end[0] <= 2:
            continue
        if is_valid_move(original_board, start, end):
            board[end[0]][end[1]] = True


def king_generator(board, start):
    original_board = [row[:] for row in board]
    sr, sc = start
    side = original_board[sr][sc][0]

    # 将、帅只在己方九宫内上下左右走一步。
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        end = (sr + dr, sc + dc)
        if not 3 <= end[1] <= 5:
            continue
        if side == 'r' and not 7 <= end[0] <= 9:
            continue
        if side == 'b' and not 0 <= end[0] <= 2:
            continue
        if is_valid_move(original_board, start, end):
            board[end[0]][end[1]] = True

    # 将帅同列且中间没有棋子时，可以直接吃掉对方将帅。
    for dr in (-1, 1):
        r = sr + dr
        while 0 <= r < ROWS:
            target = original_board[r][sc]
            if target is not None:
                end = (r, sc)
                if target[-1] == 'k' and is_valid_move(original_board, start, end):
                    board[r][sc] = True
                break
            r += dr


def cannon_generator(board, start):
    original_board = [row[:] for row in board]
    sr, sc = start

    # 炮架前可走空位；越过一个炮架后，只能吃遇到的第一枚敌子。
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        r, c = sr + dr, sc + dc
        has_screen = False
        while 0 <= r < ROWS and 0 <= c < COLS:
            end = (r, c)
            if not has_screen:
                if original_board[r][c] is None:
                    if is_valid_move(original_board, start, end):
                        board[r][c] = True
                else:
                    has_screen = True
            elif original_board[r][c] is not None:
                if is_valid_move(original_board, start, end):
                    board[r][c] = True
                break
            r += dr
            c += dc


def pawn_generator(board, start):
    original_board = [row[:] for row in board]
    sr, sc = start
    side = original_board[sr][sc][0]

    # 红兵向上，黑卒向下；过河后增加左右两个方向，不能后退。
    if side == 'r':
        end = (sr - 1, sc)
    else:
        end = (sr + 1, sc)
    if is_valid_move(original_board, start, end):
        board[end[0]][end[1]] = True

    if (side == 'r' and sr <= 4) or (side == 'b' and sr >= 5):
        end = (sr, sc - 1)
        end1 = (sr, sc + 1)
        if is_valid_move(original_board, start, end):
            board[end[0]][end[1]] = True
        if is_valid_move(original_board, start, end1):
            board[end1[0]][end1[1]] = True
