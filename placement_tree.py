from mimetypes import init
from typing import Hashable, List, Sequence, Tuple, override
from click.core import F
from manim import DOWN, RIGHT, UP, Cross, DiGraph, Dot, ManimColor, Mobject, ParsableManimColor, Square, SurroundingRectangle, Text, VGroup, VMobject
from manim.mobject.graph import GenericGraph
from puzzle import CELL_SIZE, Cell, Hint, SquareState, gen_square_mark

FILLED = SquareState.FILLED

# def generate_all_solutions(initial_line: List[Cell]) -> Iterable[tuple]:
#     pass

def generate_nodes_from_leaves(leaf_nodes: Sequence[tuple]):
    # Use a set to avoid duplicate nodes
    all_nodes = set(leaf_nodes)

    # Find the maximum depth (length of tuples)
    if not leaf_nodes:
        return []

    max_depth = len(leaf_nodes[0])

    # Generate ancestor nodes for each level
    for level in range(max_depth - 1, 0, -1):
        current_level_nodes = set()

        # For each existing node that has a value at the current level
        for node in all_nodes:
            # Create parent by replacing values with None from current level onwards
            parent = list(node[:level])
            while len(parent) < max_depth:
                parent.append(None)
            current_level_nodes.add(tuple(parent))

        # Add these parent nodes to our collection
        all_nodes.update(current_level_nodes)

    # Convert back to list and sort by level order and then by values
    def sort_key(node):
        # Count non-None values for level
        level = sum(1 for val in node if val is not None)
        # Use the values themselves as secondary sort key
        return (level, node)

    return [tuple(None for _ in range(max_depth))] + sorted(all_nodes, key=sort_key)

def edge_list_from_nodes(nodes: Sequence[tuple]):
        # Helper function to get the level of a node (count of non-None values)
    def get_level(node):
        return sum(1 for val in node if val is not None)

    # Helper function to check if one node is a parent of another
    def is_parent(potential_parent, potential_child):
        parent_level = get_level(potential_parent)
        child_level = get_level(potential_child)

        # Parent should have exactly one fewer non-None value
        if child_level != parent_level + 1:
            return False

        # For the root node (all None), any first-level node is a child
        if all(val is None for val in potential_parent):
            return child_level == 1

        # All non-None values in parent should match the child's corresponding values
        parent_values = [i for i, val in enumerate(potential_parent) if val is not None]
        for idx in parent_values:
            if potential_parent[idx] != potential_child[idx]:
                return False

        return True

    # Sort nodes by level and then by values
    # sorted_nodes = sorted(nodes, key=lambda node: (get_level(node), node))
    sorted_nodes = sorted(nodes, key=lambda node: (get_level(node), [val if val is not None else -float('inf') for val in node]))

    # Generate edges
    edges = []
    for i, child in enumerate(sorted_nodes):
        child_level = get_level(child)
        if child_level == 0:  # Skip the root node as it has no parent
            continue

        # Find the parent node
        for potential_parent in sorted_nodes:
            if is_parent(potential_parent, child):
                edges.append((potential_parent, child))
                break

    return edges


CELL_SIZE = 1.0
class StaticCell(Square):
    def __init__(self, state: SquareState, cell_size = CELL_SIZE, **kwargs) -> None:
        super().__init__(side_length=cell_size, z_index=0, **kwargs)
        self.cell_size = cell_size

        self.state = state
        self.square_mark = gen_square_mark(cell_size)
        self.x_mark = Cross(self, z_index=2, scale_factor=0.7)
        if state == SquareState.FILLED:
            self.add(self.square_mark)
        elif state == SquareState.EMPTY:
            self.add(self.x_mark)

    def set_state(self, state: SquareState):
        match state:
            case SquareState.FILLED:
                self.square_mark.move_to(self.get_center())
                self.add(self.square_mark)
            case SquareState.EMPTY:
                self.x_mark.move_to(self.get_center())
                self.add(self.x_mark)
            case SquareState.UNKOWN:
                raise ValueError("Can't unset StaticCell")


# Basically a Line but stripped to just be the cells
class LineCells(VMobject):
    def __init__(self, hint: List[int], initial_states: List[SquareState] | None = None, length: int | None = None, cell_size = CELL_SIZE, **kwargs):
        super().__init__(**kwargs)
        self.hint = hint
        self.squares_group = VGroup()
        self.cell_size = cell_size
        if not initial_states:
            if length is None:
                raise ValueError("initial_line or length must be specified")
            self.squares_group.add(StaticCell(SquareState.UNKOWN) for _ in range(length))
            self.length = length
        else:
            self.length = len(initial_states)
            initial_line = []
            for state in initial_states:
                cell = StaticCell(state)
                initial_line.append(cell)
                self.squares_group.add(*initial_line)
        self.squares_group.arrange(RIGHT, buff=0)
        self.squares_group.center()
        self.add(self.squares_group)

    def place_seg(self, seg_index: int, pos: int, color: ParsableManimColor | None = None):
        seg = self.hint[seg_index]
        for i in range(pos, pos + seg):
            self.squares_group[i].set_state(FILLED)
            if color:
                self.squares_group[i].square_mark.set_color(color)


class PlacementTreeNode(LineCells):
    def __init__(self, key: Tuple[int | None, ...], colors: Sequence[ParsableManimColor], *args, **kwargs):
        super().__init__(*args, **kwargs)
        for seg_index, pos in enumerate(key):
            if pos is None:
                continue
            self.place_seg(seg_index, pos, colors[seg_index])


class PlacementTree(DiGraph):
    def __init__(
            self,
            placements: Sequence[Tuple[int | None, ...]],
            hint: List[int],
            initial_states: List[SquareState] | None = None,
            length: int | None = None,
            *args,
            **kwargs
    ) -> None:
        # Each vertex in the tree is keyed by a tuple with a length of the number of segments
        # Each value is the index in the array where the corresponding segment is placed, and None if not placed
        vertext_keys = generate_nodes_from_leaves(placements)
        edges = edge_list_from_nodes(vertext_keys)

        n_segs = len(hint)
        self.colors = [ManimColor.from_hsv((i / n_segs, 1.0, 1.0)) for i in range(n_segs)]
        self.hint_obj = Hint(hint, len(hint), True, CELL_SIZE)
        for hint_cell, color in zip(self.hint_obj.segments, self.colors):
            hint_cell.text.set_color(color)

        self.vertex_config = {
            vertex: {
                "key": vertex,
                "hint": hint,
                "initial_states": initial_states,
                "length": length,
                "colors": self.colors
            } for vertex in vertext_keys
        }

        super().__init__(
            vertext_keys,
            edges,
            layout="tree",
            vertex_type=PlacementTreeNode,
            root_vertex=vertext_keys[0],
            vertex_config=self.vertex_config,
            *args,
            **kwargs
        )

        self.hint_obj.next_to(self, UP, buff=1)
        self.hint_box = SurroundingRectangle(self.hint_obj, buff=0.2)
        self.hint_label = Text("Hint").next_to(self.hint_box, UP)
        self.add(self.hint_obj, self.hint_box, self.hint_label)

    @override
    def add_vertices(self: GenericGraph, *vertices: Hashable):
        return super().add_vertices(*vertices, vertex_type=PlacementTreeNode, vertex_config=self.vertex_config)

    # Overriden to put edges on centers
    def _populate_edge_dict(
        self, edges: list[tuple[Hashable, Hashable]], edge_type: type[Mobject]
    ):
        u, v = edges[0]
        self.edges = {
            (u, v): edge_type(
                # These 2 lines are changed
                self[u].get_edge_center(DOWN),
                self[v].get_edge_center(UP),
                z_index=-1,
                **self._edge_config[(u, v)],
            )
            for (u, v) in edges
        }

        for (u, v), edge in self.edges.items():
            edge.add_tip(**self._tip_config[(u, v)])

