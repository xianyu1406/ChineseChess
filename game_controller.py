"""
game_controller.py
==================
中国象棋游戏控制器 —— 独立模块，不修改 GUI.py 也能接入。

功能：
  1. 将军检测：一方被将军时，只能走能解将的棋。
  2. 将死 / 困毙判定：对方无棋可走时直接判胜负，弹出系统提示框。
  3. 长将限制：同一枚棋子在不超过 2 个固定点位上连续将军累计 >= 3 次，
     该棋子被强制停用（无法选中和移动），只能动其他棋子。
  4. 胜利提示：调用 Windows 系统弹框（MessageBoxW），不在 Pygame 里画。

依赖：game_logic.py（同目录下，由本模块自动导入）

在 GUI.py 中的接入方式（只需改 4 处，见文件末尾注释）：
  --------------------------------------------------------------
  1) 顶部导入：
       from game_controller import GameController

  2) 棋盘初始化后（board 定义完之后）加一行：
       controller = GameController(board)

  3) 选中棋子时加一道过滤（被停用的棋子不能选）：
       if clicked_piece and clicked_piece.startswith(current_turn):
           if not controller.is_piece_disabled((r, c)):      # <-- 加这行
               selected_piece = (r, c)

  4) 原来执行移动的地方（board[r][c]=... 那几行）替换为：
       if controller.try_move((sr, sc), (r, c), current_turn):
           selected_piece = None
           current_turn = 'b' if current_turn == 'r' else 'r'
       else:
           selected_piece = None   # 不合法就取消选中（也可以保留，随你）
  --------------------------------------------------------------
"""

import ctypes
from collections import defaultdict

from game_logic import (
    is_in_check,
    is_checkmate,
    is_stalemate,
    get_legal_moves,
)

ROWS, COLS = 10, 9


class GameController:
    """
    封装一局棋的全部规则状态。
    构造时传入棋盘 board（10x9 二维列表），之后所有操作通过本类方法进行。
    """

    def __init__(self, board):
        self.board = board

        # 棋子唯一 ID 映射：当前位置 (r,c) -> 初始位置 (r,c)
        # 用棋子的初始位置作为它的唯一标识，吃子时移除被吃方的 ID。
        self.piece_id_map = {}
        for r in range(ROWS):
            for c in range(COLS):
                if board[r][c] is not None:
                    self.piece_id_map[(r, c)] = (r, c)

        # 连续将军历史：{'r': [(piece_id, from_pos, to_pos), ...], 'b': [...]}
        # 一方一旦走出一步不将军的棋，该方历史清空（连续将军中断）。
        self.check_history = {'r': [], 'b': []}

        # 被强制停用的棋子 ID 集合（长将违规触发）。
        self.disabled_pieces = set()

        # 游戏结束状态。
        self.game_over = False
        self.winner = None  # 'r' 或 'b'

    # ------------------------------------------------------------------
    #  查询类方法
    # ------------------------------------------------------------------

    def is_piece_disabled(self, pos):
        """指定位置的棋子是否被强制停用。"""
        pid = self.piece_id_map.get(pos)
        return pid is not None and pid in self.disabled_pieces

    def in_check(self, side):
        """side 方是否被将军。"""
        return is_in_check(self.board, side)

    # ------------------------------------------------------------------
    #  核心：尝试走一步棋
    # ------------------------------------------------------------------

    def try_move(self, start, end, current_turn):
        """
        尝试让 current_turn 方从 start 走到 end。

        返回 True 表示走棋成功（已更新棋盘和内部状态）；
        返回 False 表示这步不合法（被将军时不能解将 / 棋子被停用 / 游戏已结束）。

        如果这步走完后对方被将死或困毙：
          - 自动设置 game_over / winner
          - 弹出 Windows 系统提示框显示胜利方
          - 方法仍然返回 True（走棋本身是成功的，只是游戏结束了）
        """
        # 游戏已结束，不再接受任何走棋
        if self.game_over:
            return False

        sr, sc = start
        er, ec = end

        # 被停用的棋子不能动
        moving_pid = self.piece_id_map.get((sr, sc))
        if moving_pid is not None and moving_pid in self.disabled_pieces:
            return False

        # 模拟走棋，检查走完后己方是否还被将军
        # （被将军时只能走能解将的棋；未被将军时也要保证走完不送将）
        sim_board = [row[:] for row in self.board]
        sim_board[er][ec] = sim_board[sr][sc]
        sim_board[sr][sc] = None
        if is_in_check(sim_board, current_turn):
            return False

        # === 正式执行走棋 ===

        # 吃子：从 piece_id_map 移除被吃棋子的 ID
        if (er, ec) in self.piece_id_map:
            del self.piece_id_map[(er, ec)]
        # 更新移动棋子的 ID 映射
        self.piece_id_map.pop((sr, sc), None)
        self.piece_id_map[(er, ec)] = moving_pid

        self.board[er][ec] = self.board[sr][sc]
        self.board[sr][sc] = None

        opponent = 'b' if current_turn == 'r' else 'r'

        # --- 将军记录 & 长将限制检测 ---
        if is_in_check(self.board, opponent):
            self.check_history[current_turn].append(
                (moving_pid, (sr, sc), (er, ec))
            )
            self._check_long_check(current_turn)
        else:
            # 这步没将军，连续将军中断，清空当前方历史
            self.check_history[current_turn].clear()

        # --- 胜负判定：将死 或 困毙 ---
        if is_checkmate(self.board, opponent, self.disabled_pieces, self.piece_id_map) or \
           is_stalemate(self.board, opponent, self.disabled_pieces, self.piece_id_map):
            self.game_over = True
            self.winner = current_turn
            self._show_victory_dialog()

        return True

    # ------------------------------------------------------------------
    #  内部方法
    # ------------------------------------------------------------------

    def _check_long_check(self, side):
        """
        长将限制检测：
        同一枚棋子在不超过 2 个固定点位上连续将军累计 >= 3 次 -> 强制停用。
        """
        # 统计该方每个棋子将军时所处的位置（终点位置，即棋子走完后所在的格）
        piece_positions = defaultdict(list)
        for pid, _from, to in self.check_history[side]:
            piece_positions[pid].append(to)

        for pid, positions in piece_positions.items():
            # 只在 <=2 个点位上将军，且累计次数 >= 3
            if len(set(positions)) <= 2 and len(positions) >= 3:
                self.disabled_pieces.add(pid)

    def _show_victory_dialog(self):
        """
        调用 Windows 系统弹框显示胜利信息。
        使用 ctypes.windll.user32.MessageBoxW，无需安装额外库。
        0x40 = MB_ICONINFORMATION（信息图标）。
        """
        side_name = "红方" if self.winner == 'r' else "黑方"
        try:
            ctypes.windll.user32.MessageBoxW(
                0,
                f"{side_name}胜利！点击确定后关闭游戏。",
                "中国象棋 - 游戏结束",
                0x40,
            )
        except Exception:
            # 非 Windows 环境或弹框失败时，降级为控制台输出
            print(f"\n{'='*40}")
            print(f"  {side_name}胜利！")
            print(f"{'='*40}\n")


# ----------------------------------------------------------------------
#  自测：不启动 GUI，直接验证控制器逻辑
#  运行：python game_controller.py
# ----------------------------------------------------------------------
if __name__ == '__main__':
    def empty():
        return [[None] * COLS for _ in range(ROWS)]

    # --- 测试1：初始局面，控制器正常初始化 ---
    board = [
        ['b_r','b_n','b_b','b_a','b_k','b_a','b_b','b_n','b_r'],
        [None]*9,
        [None,'b_c',None,None,None,None,None,'b_c',None],
        ['b_p',None,'b_p',None,'b_p',None,'b_p',None,'b_p'],
        [None]*9, [None]*9,
        ['r_p',None,'r_p',None,'r_p',None,'r_p',None,'r_p'],
        [None,'r_c',None,None,None,None,None,'r_c',None],
        [None]*9,
        ['r_r','r_n','r_b','r_a','r_k','r_a','r_b','r_n','r_r'],
    ]
    ctrl = GameController(board)
    assert not ctrl.game_over
    assert not ctrl.in_check('r')
    assert not ctrl.in_check('b')
    print("测试1 通过：控制器初始化正常，初始局面无将军")

    # --- 测试2：被将军时，送将的走法被拒绝 ---
    b2 = empty()
    b2[0][4] = 'b_k'
    b2[9][3] = 'r_k'
    b2[0][0] = 'r_r'   # 红车在第0行将军黑将
    ctrl2 = GameController(b2)
    assert ctrl2.in_check('b'), "黑方应被将军"
    # 黑将从 (0,4) 走到 (0,5) —— 仍在第0行，还被车将军，应被拒绝
    assert not ctrl2.try_move((0, 4), (0, 5), 'b'), "送将走法应被拒绝"
    # 黑将从 (0,4) 走到 (1,4) —— 离开第0行，解将，应成功
    assert ctrl2.try_move((0, 4), (1, 4), 'b'), "解将走法应成功"
    assert not ctrl2.in_check('b'), "走完后不应被将军"
    print("测试2 通过：被将军时只允许解将走法")

    # --- 测试3：将死判定 + 胜利弹框（弹框会阻塞，自测时注释掉弹框调用） ---
    b3 = empty()
    b3[0][3] = 'b_k'
    b3[9][4] = 'r_k'
    b3[0][8] = 'r_r'   # 第0行将军
    b3[1][8] = 'r_r'   # 控制第1行，黑将无处可逃
    ctrl3 = GameController(b3)
    assert ctrl3.in_check('b')
    # 黑将没有任何合法走法，随便走一步都会失败
    assert not ctrl3.try_move((0, 3), (0, 4), 'b')
    assert not ctrl3.try_move((0, 3), (1, 3), 'b')
    assert not ctrl3.try_move((0, 3), (1, 4), 'b')
    print("测试3 通过：将死局面所有走法均被拒绝（将死判定由 game_logic 保证）")

    # --- 测试4：长将限制 —— 同一子在两个点位将军3次后被停用 ---
    # 构造一个可以来回将军的局面：
    # 黑将在 (0,4)，红车在 (0,0) 将军，黑将在 (1,4) 躲开，红车退回 (0,1) 不将军...
    # 简化：直接手动构造 check_history 来验证停用逻辑
    b4 = empty()
    b4[0][4] = 'b_k'
    b4[9][3] = 'r_k'
    b4[0][0] = 'r_r'
    ctrl4 = GameController(b4)
    # 手动模拟：红车ID为 (0,0)，在 (0,1) 和 (0,2) 两个点位各将军若干次
    rid = (0, 0)
    ctrl4.check_history['r'] = [
        (rid, (0, 0), (0, 1)),
        (rid, (0, 1), (0, 2)),
        (rid, (0, 2), (0, 1)),  # 第3次将军，只在 { (0,1), (0,2) } 两个点位
    ]
    ctrl4._check_long_check('r')
    assert rid in ctrl4.disabled_pieces, "红车应被强制停用"
    assert ctrl4.is_piece_disabled((0, 0)), "红车当前位置应显示为停用"
    print("测试4 通过：同一子在两个点位将军3次后被强制停用")

    # --- 测试5：被停用的棋子不能走 ---
    assert not ctrl4.try_move((0, 0), (0, 1), 'r'), "被停用的红车不应能走"
    print("测试5 通过：被停用棋子的走法被拒绝")

    print("\n========== 全部自测通过 ==========")
