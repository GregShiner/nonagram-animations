from typing import Literal
from manim import BLUE, DOWN, RED, UP, AnimationGroup, Arrow, Indicate, Scene, Text, VGroup

from puzzle import LabeledPointer, Line, SegPlacer, SquareState, states_to_cells

UNKNOWN = SquareState.UNKOWN
EMPTY = SquareState.EMPTY
FILLED = SquareState.FILLED

class SegPos(Scene):
    def construct(self):
        line = Line([5], length=10)
        line.set_hint_color(0, BLUE)
        line.create_segments(5)
        line.move_segment_to(0, 2)
        line.set_seg_color(0, BLUE)
        numbers = VGroup()
        for i in range(10):
            number = Text(str(i))
            number.scale_to_fit_height(0.5)
            number.next_to(line.squares_group[i], UP)
            numbers.add(number.copy())
        arrow = Arrow(start=DOWN/2, end=UP).next_to(line.squares_group[2], DOWN)
        self.add(line, numbers, arrow)


"""
from enum import Enum
from typing import List
# Represents the state of an individual square
# An enum type can be one of any of the variants defined
class SquareState(Enum):
    UNKOWN = 0
    FILLED = 1
    EMPTY = 2

# A segment length in a hint
type Segment = int

def find_left_sol(hint: List[Segment], line: List[SquareState]) -> List[SquareState]:
    next_seg_pos = 0
    for segment in hint:
        for i in range(next_seg_pos, next_seg_pos + segment):
            line[i] = SquareState.FILLED
        next_seg_pos += segment + 1

    return line
"""

class BasicSol(Scene):
    def construct(self):
        segs = [1, 2, 3]
        seg_placer = SegPlacer(segs, length=10)

        arrow = LabeledPointer("Next Position")
        arrow.next_to(seg_placer.squares_group[0], DOWN)
        self.add(seg_placer, arrow)

        self.play(seg_placer.animate.move_segment_to(0, 0))
        self.play(arrow.animate.next_to(seg_placer.squares_group[2], DOWN), seg_placer.squares_group[1].animated_set_state(EMPTY))

        self.play(seg_placer.animate.move_segment_to(1, 2))
        self.play(arrow.animate.next_to(seg_placer.squares_group[5], DOWN), seg_placer.squares_group[4].animated_set_state(EMPTY))

        self.play(seg_placer.animate.move_segment_to(2, 5))
        self.play(*(seg_placer.squares_group[i].animated_set_state(EMPTY) for i in range(8, 10)))


class AvoidX(Scene):
    def construct(self):
        segs = [1, 2, 3]
        line = states_to_cells([*(UNKNOWN for _ in range(3)), EMPTY, *(UNKNOWN for _ in range(6))])
        seg_placer = SegPlacer(segs, initial_line=line)
        # Set the x to appear on top of the segments so its still visible
        seg_placer.squares_group[3].set_z_index(5)

        arrow = LabeledPointer("Next Position")
        arrow.next_to(seg_placer.squares_group[0], DOWN)
        self.add(seg_placer, arrow)

        self.play(seg_placer.animate.move_segment_to(0, 0))
        self.play(arrow.animate.next_to(seg_placer.squares_group[2], DOWN), seg_placer.squares_group[1].animated_set_state(EMPTY))

        self.play(seg_placer.animate.move_segment_to(1, 2))
        self.play(Indicate(seg_placer.squares_group[3].x_mark, color=RED, scale_factor=1.3))
        self.play(seg_placer.animate.move_segment_to(1, 3), seg_placer.squares_group[2].animated_set_state(EMPTY))
        self.play(Indicate(seg_placer.squares_group[3].x_mark, color=RED, scale_factor=1.3))
        self.play(seg_placer.animate.move_segment_to(1, 4))
        self.play(arrow.animate.next_to(seg_placer.squares_group[7], DOWN), seg_placer.squares_group[6].animated_set_state(EMPTY))

        self.play(seg_placer.animate.move_segment_to(2, 7))
