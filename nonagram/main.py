from itertools import product
from typing import List, Literal, Tuple, override
from manim import BLACK, BLUE, DOWN, GREEN, LEFT, ORIGIN, RED, RIGHT, UP, Add, AnimationGroup, Arrow, Camera, Circle, Create, Cross, FadeIn, LaggedStart, Rectangle, Scene, Transform, Uncreate, VGroup, Text, config
from puzzle import Cell, CellScanner, Game, Grid, Hint, HintSet, Line, SegmentSquares, SquareState, gen_square_mark

class TestCell(Scene):
    def construct(self):
        cell = Cell()
        self.play(Create(cell))
        self.wait(1)
        self.play(cell.set_state(SquareState.FILLED), subcaption="Filled")
        self.wait(1)
        self.play(cell.set_state(SquareState.UNKOWN), subcaption="Unknown")
        self.wait(1)
        self.play(cell.set_state(SquareState.EMPTY), subcaption="Empty")
        self.wait(1)
        self.play(cell.set_state(SquareState.FILLED), subcaption="Filled")
        self.wait(1)
        self.play(cell.set_state(SquareState.EMPTY), subcaption="Empty")


class TestGrid(Scene):
    def construct(self):
        grid = Grid(5, 5)
        self.play(Create(grid))
        self.play(grid.set_cell_state(0, 0, SquareState.FILLED))
        self.play(grid.set_cell_state(0, 1, SquareState.FILLED))
        self.play(grid.set_cell_state(1, 0, SquareState.FILLED))
        self.play(grid.set_cell_state(4, 4, SquareState.EMPTY))

class TestHint(Scene):
    def construct(self):
        # Create a horizontal hint with 5 segments, values [3, 1, 2]
        # This will result in: [empty, empty, 3, 1, 2]
        horizontal_hint = Hint([3, 1, 2], 5, True)
        horizontal_hint2 = Hint([3, 1, 2, 4, 7], 5, True)

        # Create a vertical hint with 4 segments, values [1, 1]
        # This will result in: [empty, empty, 1, 1] from top to bottom
        vertical_hint = Hint([1, 1], 4, False)
        bigger_numbers = Hint([3, 13, 300], 3, True)
        self.play(Create(horizontal_hint))
        self.wait()
        self.play(Uncreate(horizontal_hint))
        self.play(Create(horizontal_hint2))
        self.wait()
        self.play(Uncreate(horizontal_hint2))
        self.play(Create(vertical_hint))
        self.wait()
        self.play(Uncreate(vertical_hint))
        self.play(Create(bigger_numbers))
        self.wait()
        self.play(Uncreate(bigger_numbers))

class TestHintSet(Scene):
    def construct(self):
        # Create row hints for a nonogram
        row_hints = [
            [3],
            [1, 1],
            [2]
        ]
        row_hint_set = HintSet(row_hints, direction="row")

        # Create column hints for the same nonogram
        col_hints = [
            [2],
            [1, 1],
            [2]
        ]
        col_hint_set = HintSet(col_hints, direction="col")
        self.play(Create(row_hint_set))
        self.wait()
        self.play(Uncreate(row_hint_set))
        self.play(Create(col_hint_set))
        self.wait()
        self.play(Uncreate(col_hint_set))

class TestGame(Scene):
    def construct(self):
        # Create row hints for a nonogram
        row_hints = [
            [3],
            [1, 1],
            [1]
        ]

        # Create column hints for the same nonogram
        col_hints = [
            [2],
            [1, 1],
            [2]
        ]
        game = Game(row_hints, col_hints)
        self.play(Create(game))
        self.play(LaggedStart(*game.grid.set_line([SquareState.FILLED, SquareState.FILLED, SquareState.FILLED], 0, "row"), lag_ratio=0.15))
        self.play(LaggedStart(*game.grid.set_line([SquareState.FILLED, SquareState.FILLED, SquareState.EMPTY], 0, "col"), lag_ratio=0.15))
        self.play(LaggedStart(*game.grid.set_line([SquareState.FILLED, SquareState.FILLED, SquareState.EMPTY], 2, "col"), lag_ratio=0.15))
        self.play(LaggedStart(*game.grid.set_line([SquareState.FILLED, SquareState.EMPTY, SquareState.FILLED], 1, "row"), lag_ratio=0.15))
        self.play(LaggedStart(*game.grid.set_line([SquareState.EMPTY, SquareState.FILLED, SquareState.EMPTY], 2, "row"), lag_ratio=0.15))
        self.wait(3)


def parse_solution_file(file_name) -> Tuple[Game, List[Tuple[List[SquareState], int, Literal["row"] | Literal["col"]]]]:
    """
3 # Row Hints
1 1
1

2 # Col Hints
1 1
2

0 row o o o # Solution
0 col o o x
2 col o o x
1 row o x o
2 row x o x
    """
    def parse_square(square: str) -> SquareState:
        match square.strip():
            case "o":
                return SquareState.FILLED
            case "x":
                return SquareState.EMPTY
            case "_":
                return SquareState.UNKOWN
            case _:
                raise ValueError(f"{square} is not 'o', 'x', or '_'")

    with open(file_name, "r") as f:
        row_hint = []
        while (line := f.readline()) != "\n":
            row_hint.append(list(map(lambda x: int(x), line.split(" "))))
        col_hint = []
        while (line := f.readline()) != "\n":
            col_hint.append(list(map(lambda x: int(x), line.split(" "))))
        solution = []
        while (line := f.readline()):
            line_list = line.split(" ")
            i = int(line_list[0])
            if line_list[1] not in {"row", "col"}:
                raise ValueError("Direction must be 'row' or 'col'")
            direction = line_list[1]
            line = list(map(parse_square, line_list[2:]))
            solution.append((line, i, direction))

    return (Game(row_hint, col_hint, 1), solution)

class VisualizeSolution(Scene):
    def construct(self):
        game, solution = parse_solution_file("solution.txt")
        # game.shift(DOWN * 1.3)
        game.move_to(ORIGIN)
        game.scale_to_fit_height(7.5)
        self.play(Create(game))
        for solution_line in solution:
            try:
                self.play(LaggedStart(*game.grid.set_line(*solution_line), lag_ratio=0.15))
            except ValueError:
                pass
        self.wait(3)

class OverlapAlg(Scene):
    def construct(self):
        all_obj = VGroup()
        initial_line = Line([3, 4], length=10)
        initial_line.set_hint_color(0, BLUE)
        initial_line.set_hint_color(1, RED)

        left_line = initial_line.copy()

        solution_line = left_line.copy()

        left_line.create_segments(3, 4)

        left_line.set_seg_color(0, BLUE)
        left_line.set_seg_color(1, RED)

        left_line.move_segment_to(0, 0)
        left_line.move_segment_to(1, 4)

        right_line = left_line.copy()
        right_line.move_segment_to(0, 2)
        right_line.move_segment_to(1, 6)

        initial_text = Text("Initial State")
        left_text = Text("Left Solution")
        right_text = Text("Right Solution")
        sol_text = Text("New Overlap")

        initial_line.shift(UP*2.2)
        right_line.shift(DOWN*1.1)
        solution_line.shift(3.3 * DOWN)

        initial_text.next_to(initial_line, LEFT)
        left_text.next_to(left_line, LEFT)
        right_text.next_to(right_line, LEFT)
        sol_text.next_to(solution_line, LEFT)

        scanner = CellScanner(left_line.squares_group[0], solution_line.squares_group[0])
        scanner.set_z_index(3)

        whacky_arrow = Arrow(start=right_line.get_critical_point(DOWN), end=solution_line.get_critical_point(UP))
        whacky_arrow2 = Arrow(start=initial_line.get_critical_point(DOWN), end=left_line.get_critical_point(UP))

        all_obj.add(initial_line, left_line, right_line, solution_line, scanner, initial_text, left_text, right_text, sol_text, whacky_arrow, whacky_arrow2)
        all_obj.move_to(ORIGIN)
        original_width = all_obj.width
        all_obj.scale_to_fit_width(14)
        ratio = all_obj.width/original_width

        self.play(LaggedStart(
            FadeIn(initial_line, initial_text),
            FadeIn(left_line, whacky_arrow2, left_text, shift=DOWN*1.1),
            FadeIn(right_line, right_text, shift=DOWN*1.1),
            FadeIn(solution_line, whacky_arrow, sol_text, shift=DOWN*1.1),
            lag_ratio=0.5))

        self.play(Create(scanner))

        self.play(scanner.animate.shift_by_cell(RIGHT*ratio))
        self.play(scanner.animate.shift_by_cell(RIGHT*ratio))

        top_blue_copy1 = left_line.segment_group[0][2].copy()
        bot_blue_copy1 = right_line.segment_group[0][0].copy()

        sol_square1 = gen_square_mark(ratio, 0.8)
        sol_square1.set_color(BLUE)
        sol_square1.move_to(solution_line.squares_group[2])
        self.play(Transform(top_blue_copy1, sol_square1), Transform(bot_blue_copy1, sol_square1))

        self.play(scanner.animate.shift_by_cell(RIGHT*ratio))
        self.play(scanner.animate.shift_by_cell(RIGHT*ratio))
        self.play(scanner.animate.shift_by_cell(RIGHT*ratio))
        self.play(scanner.animate.shift_by_cell(RIGHT*ratio))

        top_blue_copy2 = left_line.segment_group[1][2].copy()
        bot_blue_copy2 = right_line.segment_group[1][0].copy()

        sol_square2 = gen_square_mark(ratio, 0.8)
        sol_square2.set_color(RED)
        sol_square2.move_to(solution_line.squares_group[6])
        self.play(Transform(top_blue_copy2, sol_square2), Transform(bot_blue_copy2, sol_square2))

        self.play(scanner.animate.shift_by_cell(RIGHT*ratio))

        top_blue_copy3 = left_line.segment_group[1][3].copy()
        bot_blue_copy3 = right_line.segment_group[1][1].copy()

        sol_square3 = gen_square_mark(ratio, 0.8)
        sol_square3.set_color(RED)
        sol_square3.move_to(solution_line.squares_group[7])
        self.play(Transform(top_blue_copy3, sol_square3), Transform(bot_blue_copy3, sol_square3))

        self.play(scanner.animate.shift_by_cell(RIGHT*ratio))
        self.play(scanner.animate.shift_by_cell(RIGHT*ratio))
        self.play(Uncreate(scanner))
        print(all_obj.height)
        self.wait(3)

class OverlapExplain(Scene):
    def construct(self):
        """
        This animation works by placing a rectangle next to each segment that is being obscured and stretching itself over the segment while the other segments that move over
        """
        all_obj = VGroup()
        initial_line = Line([3, 4], length=10)
        initial_line.set_hint_color(0, BLUE)
        initial_line.set_hint_color(1, RED)

        left_line = initial_line.copy()


        left_line.create_segments(3, 4)

        left_line.set_seg_color(0, BLUE)
        left_line.set_seg_color(1, RED)

        left_line.move_segment_to(0, 0)
        left_line.move_segment_to(1, 4)

        solution_line = left_line.copy()
        # The black box needs to be above the segment squares and below the line outlines
        solution_line.set_z_index(5)
        solution_line.segment_group[0].set_z_index(3)
        solution_line.segment_group[1].set_z_index(1)

        right_line = left_line.copy()

        initial_text = Text("Initial State")
        left_text = Text("Left Solution")
        right_text = Text("Right Solution")
        sol_text = Text("New Overlap")

        initial_line.shift(UP*2.2)
        right_line.shift(DOWN*1.1)
        solution_line.shift(3.3 * DOWN)

        initial_text.next_to(initial_line, LEFT)
        left_text.next_to(left_line, LEFT)
        right_text.next_to(right_line, LEFT)
        sol_text.next_to(solution_line, LEFT)

        whacky_arrow = Arrow(start=right_line.get_critical_point(DOWN), end=solution_line.get_critical_point(UP))
        whacky_arrow2 = Arrow(start=initial_line.get_critical_point(DOWN), end=left_line.get_critical_point(UP))

        left_rect = Rectangle(color=BLACK, width=2, height=1, fill_opacity=1, stroke_opacity=0, z_index = 4)
        left_rect.next_to(solution_line.segment_group[0], LEFT, buff=0)

        right_rect = Rectangle(color=BLACK, width=2, height=1, fill_opacity=1, stroke_opacity=0, z_index = 2)
        right_rect.next_to(solution_line.segment_group[1], LEFT, buff=0)

        all_obj.add(initial_line, left_line, right_line, solution_line, initial_text, left_text, right_text, sol_text, whacky_arrow, whacky_arrow2, left_rect, right_rect)
        # all_obj.add(initial_line, left_line, right_line, solution_line, whacky_arrow, whacky_arrow2)
        all_obj.move_to(ORIGIN)
        original_width = all_obj.width
        all_obj.scale_to_fit_width(14)
        ratio = all_obj.width/original_width

        self.play(LaggedStart(
            FadeIn(initial_line, initial_text),
            FadeIn(left_line, whacky_arrow2, left_text, shift=DOWN*1.1),
            FadeIn(right_line, right_text, shift=DOWN*1.1),
            FadeIn(solution_line, whacky_arrow, sol_text, shift=DOWN*1.1),
            lag_ratio=0.5))

        self.add(left_rect)

        self.add(right_rect)

        self.play(right_rect.animate.shift(ratio*RIGHT*2), right_line.slide_segment(1, ratio*RIGHT*2))
        self.play(left_rect.animate.shift(ratio*RIGHT*2), right_line.slide_segment(0, ratio*RIGHT*2))
        self.wait(3)

class AllPermutations(Scene):
    from itertools import product
    def construct(self):
        lines = VGroup()
        total = 0
        ignored = 0
        actual = 0
        LEFT = 2
        RIGHT = 3
        LEN = 10
        NUM_POSITIONS = LEN - (LEFT + RIGHT)
        print(NUM_POSITIONS)
        for l, r in product(range(0, NUM_POSITIONS), range(LEFT + 1, LEFT + 1 + NUM_POSITIONS)):
            total += 1
            if l + LEFT + 1 > r:
                ignored += 1
                continue
            line = Line([LEFT, RIGHT], length=LEN)
            line.set_hint_color(0, BLUE)
            line.set_hint_color(1, RED)

            line.create_segments(LEFT, RIGHT)

            line.set_seg_color(0, BLUE)
            line.set_seg_color(1, RED)

            line.move_segment_to(0, l)
            line.move_segment_to(1, r)
            lines.add(line)
            actual += 1
        print(total, ignored, actual)
        print(len(range(0, 5)), len(range(3, 8)))
        lines.arrange(DOWN)
        lines.move_to(ORIGIN)
        lines.scale_to_fit_height(7.5)
        self.add(lines)

def calc_permutations(length, hint: List[int]):
    from itertools import product
    def print_line(length, hint: List[int], positions: List[int]):
        line = "_" * length
        assert len(hint) == len(positions)
        for (seg_i, seg), pos in zip(enumerate(hint), positions):
            line = line[:pos] + str(seg_i) * seg + line[pos + seg:]
        print(line)

    def check_line(length, hint: List[int], positions: List[int]):
        line = "_" * length
        assert len(hint) == len(positions)
        for (seg_i, seg), pos in zip(enumerate(hint), positions):
            start = positions[seg_i - 1] + hint[seg_i - 1] + 1 if seg_i else 0
            if any((cell != "_" for cell in line[start:start+seg])):
                return False
            line = line[:pos] + str(seg_i) * seg + line[pos + seg:]
        return True

    # print_line(length, hint, [0, 3])
    hint_sum = sum(hint)
    hint_len = len(hint)
    num_positions = length - hint_sum
    position_ranges = []
    for i, seg in enumerate(hint):
        preceding = hint[hint_len - i:]
        start = sum(preceding) + len(preceding) - 1 if preceding else 0
        end = start + num_positions
        position_ranges.append(range(start, end))

    total = 0
    ignored = 0
    actual = 0
    for positions in product(*position_ranges):
        total += 1
        if not check_line(length, hint, list(positions)):
            ignored += 1
            continue
        print_line(length, hint, list(positions))
        actual += 1
    print(total, ignored, actual)

if __name__ == "__main__":
    calc_permutations(10, [2, 3])

class AllPositions(Scene):
    from itertools import product
    def construct(self):
        left_lines = VGroup()
        for l in range(0, 5):
            line = Line([2, 3], length=10)
            line.set_hint_color(0, BLUE)
            line.set_hint_color(1, RED)

            line.create_segments(2, 3)

            line.set_seg_color(0, BLUE)
            line.set_seg_color(1, RED)

            line.move_segment_to(0, l)
            line.move_segment_to(1, 7)
            left_lines.add(line)
        left_lines.arrange(DOWN)
        right_lines = VGroup()
        for r in range(3, 8):
            line = Line([2, 3], length=10)
            line.set_hint_color(0, BLUE)
            line.set_hint_color(1, RED)

            line.create_segments(2, 3)

            line.set_seg_color(0, BLUE)
            line.set_seg_color(1, RED)

            line.move_segment_to(0, 0)
            line.move_segment_to(1, r)
            right_lines.add(line)
        right_lines.arrange(DOWN)
        all_lines = VGroup()
        all_lines.add(left_lines, right_lines)
        all_lines.arrange(LEFT)
        all_lines.move_to(ORIGIN)
        all_lines.scale_to_fit_width(self.camera.frame_width - 0.5)
        print(self.camera.frame_height)
        print(all_lines.height)
        self.add(all_lines)

class OverlapX(Scene):
    def construct(self):
        all_obj = VGroup()
        initial_line = Line([2, 4], length=10)
        initial_line.set_hint_color(0, BLUE)
        initial_line.set_hint_color(1, RED)

        left_line = initial_line.copy()

        solution_line = left_line.copy()

        initial_line.create_segments(1, 1)
        initial_line.set_seg_color(0, BLUE)
        initial_line.set_seg_color(1, RED)
        initial_line.move_segment_to(0, 1)
        initial_line.move_segment_to(1, 8)

        left_line.create_segments(2, 4)

        left_line.set_seg_color(0, BLUE)
        left_line.set_seg_color(1, RED)

        left_line.move_segment_to(0, 0)
        left_line.move_segment_to(1, 5)

        right_line = left_line.copy()
        right_line.move_segment_to(0, 1)
        right_line.move_segment_to(1, 6)

        initial_text = Text("Initial State")
        left_text = Text("Left Solution")
        right_text = Text("Right Solution")
        sol_text = Text("New Overlap")

        initial_line.shift(UP*2.2)
        right_line.shift(DOWN*1.1)
        solution_line.shift(3.3 * DOWN)

        initial_text.next_to(initial_line, LEFT)
        left_text.next_to(left_line, LEFT)
        right_text.next_to(right_line, LEFT)
        sol_text.next_to(solution_line, LEFT)

        left_xs = VGroup()
        for i in [2, 3, 4, 9]:
            cross = Cross(left_line.squares_group[i], z_index=2, scale_factor=0.8)
            cross.move_to(left_line.squares_group[i])
            left_xs.add(cross)

        right_xs = VGroup()
        for i in [0, 3, 4, 5]:
            cross = Cross(right_line.squares_group[i], z_index=2, scale_factor=0.8)
            cross.move_to(right_line.squares_group[i])
            right_xs.add(cross)

        scanner = CellScanner(left_line.squares_group[0], solution_line.squares_group[0])
        scanner.set_z_index(3)

        whacky_arrow = Arrow(start=right_line.get_critical_point(DOWN), end=solution_line.get_critical_point(UP))
        whacky_arrow2 = Arrow(start=initial_line.get_critical_point(DOWN), end=left_line.get_critical_point(UP))

        all_obj.add(initial_line, left_line, right_line, solution_line, scanner, initial_text, left_text, right_text, sol_text, whacky_arrow, whacky_arrow2, left_xs, right_xs)
        all_obj.move_to(ORIGIN)
        original_width = all_obj.width
        all_obj.scale_to_fit_width(14)
        ratio = all_obj.width/original_width

        self.play(LaggedStart(
            FadeIn(initial_line, initial_text),
            FadeIn(left_line, left_xs, whacky_arrow2, left_text, shift=DOWN*1.1),
            FadeIn(right_line, right_xs, right_text, shift=DOWN*1.1),
            FadeIn(solution_line, whacky_arrow, sol_text, shift=DOWN*1.1),
            lag_ratio=0.5))

        self.play(Create(scanner))

        self.play(scanner.animate.shift_by_cell(RIGHT*ratio))

        top_blue_copy1 = left_line.segment_group[0][1].copy()
        bot_blue_copy1 = right_line.segment_group[0][0].copy()

        sol_square1 = gen_square_mark(ratio, 0.8)
        sol_square1.set_color(BLUE)
        sol_square1.move_to(solution_line.squares_group[1])
        self.play(Transform(top_blue_copy1, sol_square1), Transform(bot_blue_copy1, sol_square1))

        self.play(scanner.animate.shift_by_cell(RIGHT*ratio))
        self.play(scanner.animate.shift_by_cell(RIGHT*ratio))

        top_x_copy1 = left_xs[1].copy()
        bot_x_copy1 = right_xs[1].copy()

        sol_x1 = top_x_copy1.copy()
        sol_x1.move_to(solution_line.squares_group[3])

        self.play(Transform(top_x_copy1, sol_x1), Transform(bot_x_copy1, sol_x1))

        self.play(scanner.animate.shift_by_cell(RIGHT*ratio))

        top_x_copy2 = left_xs[2].copy()
        bot_x_copy2 = right_xs[2].copy()

        sol_x2 = top_x_copy1.copy()
        sol_x2.move_to(solution_line.squares_group[4])

        self.play(Transform(top_x_copy2, sol_x2), Transform(bot_x_copy2, sol_x2))

        self.play(scanner.animate.shift_by_cell(RIGHT*ratio))
        self.play(scanner.animate.shift_by_cell(RIGHT*ratio))

        top_red_copy1 = left_line.segment_group[1][1].copy()
        bot_red_copy1 = right_line.segment_group[1][0].copy()

        sol_square2 = gen_square_mark(ratio, 0.8)
        sol_square2.set_color(RED)
        sol_square2.move_to(solution_line.squares_group[6])
        self.play(Transform(top_red_copy1, sol_square2), Transform(bot_red_copy1, sol_square2))

        self.play(scanner.animate.shift_by_cell(RIGHT*ratio))

        top_red_copy2 = left_line.segment_group[1][2].copy()
        bot_red_copy2 = right_line.segment_group[1][1].copy()

        sol_square3 = gen_square_mark(ratio, 0.8)
        sol_square3.set_color(RED)
        sol_square3.move_to(solution_line.squares_group[7])
        self.play(Transform(top_red_copy2, sol_square3), Transform(bot_red_copy2, sol_square3))

        self.play(scanner.animate.shift_by_cell(RIGHT*ratio))

        top_red_copy3 = left_line.segment_group[1][3].copy()
        bot_red_copy3 = right_line.segment_group[1][2].copy()

        sol_square4 = gen_square_mark(ratio, 0.8)
        sol_square4.set_color(RED)
        sol_square4.move_to(solution_line.squares_group[8])
        self.play(Transform(top_red_copy3, sol_square4), Transform(bot_red_copy3, sol_square4))

        self.play(scanner.animate.shift_by_cell(RIGHT*ratio))
        self.play(Uncreate(scanner))
        print(all_obj.height)
        self.wait(3)
