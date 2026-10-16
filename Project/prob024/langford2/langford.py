"""
Langford's problem as a CSP: the explanation part of the project video (~2:30).

Written for ManimGL (3b1b/manim), in the style of the 3b1b/videos repository:
one InteractiveScene per beat, and "# Section" comments inside construct()
so that checkpoint_paste() can replay each block on its own.

Render one scene:      manimgl langford.py LangfordPuzzle -w
Preview, no file:      manimgl langford.py LangfordPuzzle
Render all:            manimgl langford.py -a -w   (renders alphabetically;
                       SCENE_ORDER at the bottom is the order of the video)

The narration for each scene is in narration.md.
Every number shown on screen comes from results.csv or from proj.py.
"""

try:
    from manim_imports_ext import *   # inside a clone of 3b1b/videos
except ImportError:
    from manimlib import *            # plain `pip install manimgl`


# ---------------------------------------------------------------------------
# Data (from results.csv: MiniZinc 2.10.1, Gecode 6.4.0, s=2, d=1,
# median of 3 runs, 60 s timeout; and from proj.py)
# ---------------------------------------------------------------------------

SOLUTION_4 = [4, 1, 3, 1, 2, 4, 3, 2]                       # L(2,4)
FIRST_4 = {1: 2, 2: 5, 3: 3, 4: 1}                          # seat of the first copy in SOLUTION_4
L_3_9 = [int(c) for c in "181915267285296475384639743"]     # L(3,9), d=1, from brute()

UNSAT_13 = [("Original model", 51.82), ("Our model", 47.44), ("+ parity count", 0.06)]
NODES_12 = (2460807, 1230971)                               # n=12 all solutions: without / with symmetry breaking
EXPLAINED = (40, 68)                                        # impossible self-test instances explained / total

PALETTE = [BLUE_C, TEAL_C, GREEN_C, YELLOW_C, ORANGE, RED_C, PINK, PURPLE_C, MAROON_C]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def number_color(i):
    return PALETTE[(i - 1) % len(PALETTE)]


def get_tile(i, size=0.8):
    square = Square(side_length=size)
    square.set_fill(number_color(i), 0.9)
    square.set_stroke(WHITE, 1.5)
    label = Integer(i, font_size=48 * size)
    label.set_color(BLACK)
    label.move_to(square)
    return VGroup(square, label)


def get_tiles(seq, size=0.8, buff=0.1):
    return VGroup(*(get_tile(i, size) for i in seq)).arrange(RIGHT, buff=buff)


def get_position_labels(tiles, font_size=22):
    labels = VGroup()
    for q, tile in enumerate(tiles):
        label = Integer(q + 1, font_size=font_size)
        label.set_color(GREY_B)
        label.next_to(tile, DOWN, SMALL_BUFF)
        labels.add(label)
    return labels


def get_gap_arc(tiles, a, b, color, height_factor=0.55):
    start = tiles[a].get_top() + 0.05 * UP
    end = tiles[b].get_top() + 0.05 * UP
    arc = ArcBetweenPoints(start, end, angle=-PI * height_factor)
    arc.set_stroke(color, 4)
    return arc


def get_all_gap_arcs(tiles, seq):
    arcs = VGroup()
    for i in sorted(set(seq)):
        positions = [q for q, v in enumerate(seq) if v == i]
        for a, b in zip(positions, positions[1:]):
            arcs.add(get_gap_arc(tiles, a, b, number_color(i)))
    return arcs


def get_slots(n_slots, size=0.8, buff=0.1):
    slots = VGroup(*(Square(side_length=size) for _ in range(n_slots)))
    slots.arrange(RIGHT, buff=buff)
    slots.set_stroke(GREY_B, 2)
    slots.set_fill(GREY_E, 1)
    return slots


def get_marked_list(lines, mark_cls=Exmark, font_size=36):
    items = VGroup()
    for line in lines:
        text = TexText(line, font_size=font_size)
        mark = mark_cls().set_height(0.35).next_to(text, LEFT)
        items.add(VGroup(mark, text))
    items.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
    return items


# ---------------------------------------------------------------------------
# 1. The puzzle, and a strange pattern (~25 s)
# ---------------------------------------------------------------------------

class LangfordPuzzle(InteractiveScene):
    def construct(self):
        # Title
        title = Text("Langford's problem", font_size=64)
        subtitle = Text("CSPLib problem 024", font_size=32, color=GREY_B)
        subtitle.next_to(title, DOWN)
        self.play(Write(title), FadeIn(subtitle, shift=0.25 * UP))
        self.play(VGroup(title, subtitle).animate.scale(0.6).to_edge(UP))
        self.wait()

        # Scattered blocks fall into a line
        tiles = get_tiles(SOLUTION_4, size=0.9, buff=0.15)
        tiles.shift(0.3 * DOWN)
        scattered = tiles.copy()
        for tile in scattered:
            tile.shift(np.random.uniform(-2.5, 2.5) * RIGHT + np.random.uniform(-1.5, 1.0) * UP)
            tile.rotate(np.random.uniform(-0.4, 0.4))
        self.play(LaggedStartMap(FadeIn, scattered, shift=0.5 * DOWN, lag_ratio=0.1))
        self.play(Transform(scattered, tiles, lag_ratio=0.05, run_time=1.5))
        self.remove(scattered)
        self.add(tiles)

        # One block between the 1s, two between the 2s, ...
        rule = TexText(R"Between the two $k$'s: exactly $k$ blocks")
        rule.next_to(tiles, UP, buff=1.4)
        arcs = get_all_gap_arcs(tiles, SOLUTION_4)
        self.play(Write(rule))
        for arc in arcs[:3]:
            self.play(ShowCreation(arc), run_time=1.2)
        self.play(ShowCreation(arcs[3]), run_time=1.0)
        self.wait(1.5)

        # For which n?
        self.play(LaggedStartMap(FadeOut, VGroup(arcs, rule, tiles), shift=DOWN))
        question = TexText(R"For which $n$ can it be done?")
        question.next_to(title, DOWN, buff=0.7)
        ns = VGroup(*(Tex(f"n={n}") for n in range(1, 13)))
        ns.arrange_in_grid(n_rows=2, h_buff=0.9, v_buff=0.9)
        ns.next_to(question, DOWN, buff=0.7)
        marks = VGroup(*(
            (Checkmark() if n % 4 in (0, 3) else Exmark()).next_to(n_tex, DOWN, SMALL_BUFF)
            for n, n_tex in zip(range(1, 13), ns)
        ))
        self.play(Write(question), LaggedStartMap(FadeIn, ns, lag_ratio=0.05))
        self.play(LaggedStartMap(FadeIn, marks, shift=0.2 * UP, lag_ratio=0.15, run_time=3))
        pattern = Tex(R"n \equiv 0 \text{ or } 3 \pmod 4", font_size=44)
        pattern.next_to(ns, DOWN, buff=0.8).set_color(YELLOW)
        self.play(Write(pattern))
        self.wait(1.5)

        # The hook
        why = Text("Why would gaps care about 4?", font_size=34, color=GREY_B)
        why.next_to(pattern, DOWN, buff=0.4)
        self.play(FadeIn(why, shift=0.2 * UP))
        self.wait(3)


# ---------------------------------------------------------------------------
# 2. How the original model thinks (~25 s)
# ---------------------------------------------------------------------------

class BaselineModel(InteractiveScene):
    def construct(self):
        # Every copy is its own unknown
        size, buff = 0.7, 0.1
        step = size + buff
        slots = get_slots(8, size, buff).shift(1.4 * DOWN)
        seat_labels = get_position_labels(slots)
        pairs = VGroup(*(get_tiles([i, i], size, 0.1) for i in range(1, 5)))
        pairs.arrange(RIGHT, buff=0.8).shift(1.0 * UP)
        caption = TexText(R"The original model: every copy gets its own unknown seat", font_size=38)
        caption.to_edge(UP)
        self.play(FadeIn(caption), FadeIn(slots), FadeIn(seat_labels))
        self.play(LaggedStartMap(FadeIn, pairs, shift=0.3 * DOWN, lag_ratio=0.2))
        self.wait(1.5)

        # A rule ties each pair together
        bands = VGroup()
        for i, pair in enumerate(pairs, start=1):
            arc = ArcBetweenPoints(pair[0].get_top(), pair[1].get_top(), angle=-0.8 * PI)
            arc.set_stroke(number_color(i), 4)
            label = Tex(f"+{i + 1}", font_size=30).next_to(arc, UP, SMALL_BUFF)
            bands.add(VGroup(arc, label))
        caption2 = TexText(R"and a rule ties each pair: the second sits $i+1$ seats later", font_size=38)
        caption2.to_edge(UP)
        self.play(FadeTransform(caption, caption2), LaggedStartMap(ShowCreation, bands, lag_ratio=0.2))
        self.wait(2)

        # Try, clash, back up
        def seat(q):
            return slots[0].get_center() + (q - 1) * step * RIGHT

        caption3 = TexText(R"The solver tries seats, and backs up when they clash", font_size=38)
        caption3.to_edge(UP)
        pairs.save_state()
        self.play(FadeOut(bands), FadeTransform(caption2, caption3))
        for i, a in [(1, 1), (2, 2), (3, 4), (4, 6)]:
            self.play(
                pairs[i - 1][0].animate.move_to(seat(a)),
                pairs[i - 1][1].animate.move_to(seat(a + i + 1)),
                run_time=0.8,
            )
        overflow = pairs[3][1]
        self.play(overflow[0].animate.set_stroke(RED, 6), FlashAround(overflow, color=RED))
        self.play(Restore(pairs), run_time=0.8)
        self.play(LaggedStart(*(
            AnimationGroup(
                pairs[i - 1][0].animate.move_to(seat(FIRST_4[i])),
                pairs[i - 1][1].animate.move_to(seat(FIRST_4[i] + i + 1)),
            )
            for i in (4, 1, 3, 2)
        ), lag_ratio=0.3, run_time=2))
        self.wait(1.5)

        # Its limits
        limits = get_marked_list([
            R"only pairs, and only gaps of $i+1$",
            R"no solution? it has to rule out every arrangement",
            f"$n = 13$: {UNSAT_13[0][1]:.0f} seconds of search",
        ])
        limits.move_to(0.3 * DOWN)
        self.play(LaggedStartMap(FadeOut, VGroup(caption3, pairs, slots, seat_labels), shift=DOWN))
        self.play(LaggedStartMap(FadeIn, limits, shift=0.2 * RIGHT, lag_ratio=0.7, run_time=4))
        self.wait(3)


# ---------------------------------------------------------------------------
# 3. What we extended (~11 s)
# ---------------------------------------------------------------------------

class GeneralisedProblem(InteractiveScene):
    def construct(self):
        # s copies, gap i + d
        header = Text("Our extension", font_size=48).to_edge(UP)
        params = VGroup(
            TexText(R"$s$ copies of each number"),
            TexText(R"consecutive copies of $i$ are $i+d$ apart"),
        )
        params.arrange(DOWN, buff=0.3)
        params.next_to(header, DOWN, buff=0.5)
        self.play(Write(header))
        self.play(LaggedStartMap(FadeIn, params, shift=0.2 * DOWN, lag_ratio=0.5))

        # Three copies of 1..9
        tiles = get_tiles(L_3_9, size=0.42, buff=0.05)
        tiles.next_to(params, DOWN, buff=1.6)
        arcs = get_all_gap_arcs(tiles, L_3_9)
        label = TexText(R"$s=3,\ n=9,\ d=1$", font_size=36, color=GREY_B)
        label.next_to(tiles, DOWN)
        self.play(LaggedStartMap(FadeIn, tiles, shift=0.3 * DOWN, lag_ratio=0.03), FadeIn(label))
        self.play(LaggedStartMap(ShowCreation, arcs, lag_ratio=0.08, run_time=3))
        self.wait(3)


# ---------------------------------------------------------------------------
# 4. Our idea: one unknown per number (~18 s)
# ---------------------------------------------------------------------------

class PositionViewpoint(InteractiveScene):
    def construct(self):
        # Eight seats
        size, buff = 0.8, 0.1
        step = size + buff
        slots = get_slots(8, size, buff)
        slots.shift(0.6 * UP)
        seat_labels = get_position_labels(slots)
        self.add(slots, seat_labels)

        # Know the first 3, know every 3
        caption = TexText(R"Know where the first 3 sits, and you know where every 3 sits")
        caption.to_edge(UP)
        p3 = ValueTracker(1)
        pair = VGroup(get_tile(3, size), get_tile(3, size))
        coupler = Line(LEFT, RIGHT).set_stroke(number_color(3), 6)

        def update_pair(group):
            x0 = slots[0].get_x() + (p3.get_value() - 1) * step
            group[0].move_to([x0, slots.get_y(), 0])
            group[1].move_to([x0 + 4 * step, slots.get_y(), 0])

        def update_coupler(line):
            line.put_start_and_end_on(pair[0].get_bottom() + 0.6 * DOWN, pair[1].get_bottom() + 0.6 * DOWN)

        pair.add_updater(update_pair)
        coupler.add_updater(update_coupler)
        self.play(Write(caption), FadeIn(pair))
        self.play(ShowCreation(coupler))
        self.wait(2.5)

        # So only the first copy is an unknown
        caption2 = TexText(R"Our model: one unknown per number, the seat of its first copy")
        caption2.to_edge(UP)
        p_label = Tex(R"p_3", font_size=40, color=number_color(3))
        p_label.add_updater(lambda m: m.next_to(pair[0], UP))
        self.play(FadeTransform(caption, caption2), FadeIn(p_label))
        self.play(p3.animate.set_value(4), run_time=3)
        self.play(p3.animate.set_value(3), run_time=1)
        self.wait(1.5)

        # The others follow
        pair.clear_updaters()
        coupler.clear_updaters()
        p_label.clear_updaters()
        others = VGroup()
        for i in (4, 1, 2):
            for j in range(2):
                tile = get_tile(i, size)
                tile.move_to(slots[FIRST_4[i] - 1 + j * (i + 1)])
                others.add(tile)
        self.play(
            FadeOut(coupler), FadeOut(p_label),
            LaggedStartMap(FadeIn, others, shift=0.6 * DOWN, lag_ratio=0.15, run_time=2.5),
        )
        count = VGroup(
            Tex(R"\text{unknowns: } 2n \;\longrightarrow\; n", font_size=44, color=YELLOW),
            TexText(R"gaps can never be wrong, however many copies", font_size=32, color=GREY_B),
        ).arrange(DOWN, buff=0.25)
        count.next_to(seat_labels, DOWN, buff=0.9)
        self.play(Write(count[0]))
        self.play(FadeIn(count[1]))
        self.wait(4.5)


# ---------------------------------------------------------------------------
# 5. Mirror images (~10 s)
# ---------------------------------------------------------------------------

class ReversalSymmetry(InteractiveScene):
    def construct(self):
        # A solution and its mirror image
        tiles = get_tiles(SOLUTION_4, size=0.8, buff=0.12)
        tiles.shift(1.5 * UP)
        self.add(tiles)
        mirror = tiles.copy()
        mirror.shift(2.3 * DOWN)
        self.play(TransformFromCopy(tiles, mirror))
        reversed_targets = mirror.copy()
        for k, tile in enumerate(mirror):
            tile.target = tile.copy().move_to(reversed_targets[len(mirror) - 1 - k])
        self.play(
            LaggedStart(*(MoveToTarget(tile, path_arc=PI / 2) for tile in mirror), lag_ratio=0.05),
            run_time=1.5,
        )
        same = Text("read backwards: another solution", font_size=34, color=GREY_B)
        same.next_to(mirror, DOWN, buff=0.4)
        self.play(FadeIn(same))

        # Keep one of each pair
        cross = Cross(mirror)
        keep = Text("keep one of each pair: half the search", font_size=38, color=YELLOW)
        keep.to_edge(DOWN, buff=1.2)
        nodes = Text(f"n = 12: {NODES_12[0]:,} → {NODES_12[1]:,} search nodes", font_size=26, color=GREY_B)
        nodes.next_to(keep, DOWN)
        self.play(ShowCreation(cross), Write(keep))
        self.play(FadeIn(nodes))
        self.wait(3.5)


# ---------------------------------------------------------------------------
# 6. Why 0 or 3 mod 4: shade every other seat (~18 s)
# ---------------------------------------------------------------------------

class ParityArgument(InteractiveScene):
    def construct(self):
        # Shade every other seat
        tiles = get_tiles(SOLUTION_4, size=0.8, buff=0.12)
        tiles.shift(1.5 * UP)
        positions = get_position_labels(tiles)
        shades = VGroup(*(
            SurroundingRectangle(tiles[q], buff=0.06).set_fill(YELLOW, 0.35).set_stroke(width=0)
            for q in range(0, 8, 2)
        ))
        shades.set_fill(opacity=0)
        self.add(shades, tiles, positions)
        self.play(shades.animate.set_fill(opacity=0.35), run_time=1.5)
        self.wait(1.5)

        def show_pair(i):
            qs = [q for q, v in enumerate(SOLUTION_4) if v == i]
            arc = get_gap_arc(tiles, qs[0], qs[1], number_color(i))
            return arc, [tiles[q] for q in qs]

        # Even numbers: odd gap, one shaded copy
        even_rule = TexText(R"even number $\to$ odd gap $\to$ exactly one copy shaded")
        odd_rule = TexText(R"odd number $\to$ even gap $\to$ both copies shaded, or neither")
        rules = VGroup(even_rule, odd_rule).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        rules.scale(0.85)
        rules.next_to(positions, DOWN, buff=0.8)
        self.play(Write(even_rule))
        for i in (4, 2):
            arc, pair = show_pair(i)
            self.play(ShowCreation(arc), *(FlashAround(t) for t in pair), run_time=1.4)
            self.play(FadeOut(arc), run_time=0.5)

        # Odd numbers: even gap, both copies alike
        self.play(Write(odd_rule))
        for i in (3, 1):
            arc, pair = show_pair(i)
            self.play(ShowCreation(arc), *(FlashAround(t) for t in pair), run_time=1.4)
            self.play(FadeOut(arc), run_time=0.5)

        # The takeaway
        takeaway = Text("on shaded seats, odd numbers come in pairs", font_size=34, color=YELLOW)
        takeaway.next_to(rules, DOWN, buff=0.7)
        self.play(Write(takeaway))
        self.wait(4)


class ParityThirteen(InteractiveScene):
    def construct(self):
        # n = 13: thirteen shaded seats
        title = TexText(R"$n = 13$: 13 shaded seats", font_size=48)
        title.to_edge(UP)
        seats = VGroup(*(Circle(radius=0.32) for _ in range(13)))
        seats.arrange(RIGHT, buff=0.18)
        seats.set_stroke(YELLOW, 2).set_fill(YELLOW, 0.15)
        seats.shift(1.2 * UP)
        self.play(Write(title), LaggedStartMap(ShowCreation, seats, lag_ratio=0.05))
        self.wait(1.5)

        # Six even numbers take one each
        evens = [2, 4, 6, 8, 10, 12]
        even_tiles = VGroup(*(get_tile(i, 0.5).move_to(seats[k]) for k, i in enumerate(evens)))
        label = Text("6 even numbers: one each", font_size=30)
        label.next_to(seats, DOWN, buff=0.6)
        self.play(LaggedStartMap(FadeIn, even_tiles, scale=0.5, lag_ratio=0.15), FadeIn(label))
        self.wait(1.5)

        # Seven left, filled two at a time
        left = seats[6:]
        brace = Brace(left, UP)
        brace_label = brace.get_tex(R"7 \text{ left}")
        self.play(GrowFromCenter(brace), FadeIn(brace_label))
        label2 = Text("odd numbers fill them two at a time", font_size=30)
        label2.move_to(label)
        self.play(FadeTransform(label, label2))
        pair_groups = VGroup()
        for k, i in enumerate([3, 7, 11]):
            a, b = left[2 * k], left[2 * k + 1]
            pair = VGroup(get_tile(i, 0.5).move_to(a), get_tile(i, 0.5).move_to(b))
            link = Line(a.get_bottom(), b.get_bottom()).shift(0.15 * DOWN).set_stroke(number_color(i), 4)
            pair_groups.add(VGroup(pair, link))
        self.play(LaggedStartMap(FadeIn, pair_groups, shift=0.3 * DOWN, lag_ratio=0.5, run_time=3.5))
        self.wait()

        # One seat is always left over
        lonely = left[-1]
        self.play(lonely.animate.set_stroke(RED, 4).set_fill(RED, 0.4), FlashAround(lonely, color=RED))
        verdict = Text("one seat always left over: impossible", font_size=36, color=RED)
        verdict.next_to(label2, DOWN, buff=0.5)
        self.play(Write(verdict))
        self.wait(2.5)

        # Any n
        general = Tex(
            R"\text{left over} = \lceil n/2 \rceil \text{ must be even}"
            R"\quad\iff\quad n \equiv 0 \text{ or } 3 \pmod 4",
            font_size=40,
        )
        general.set_color(YELLOW)
        general.to_edge(DOWN, buff=0.9)
        self.play(Write(general))
        self.wait(5)


# ---------------------------------------------------------------------------
# 7. A proof the solver can use (~10 s)
# ---------------------------------------------------------------------------

class ParityPayoff(InteractiveScene):
    def construct(self):
        # Axis: 0 to 60 s
        unit = 0.12   # scene units per second
        x0 = -2.5
        axis = NumberLine(
            (0, 60, 10), width=60 * unit, include_numbers=True,
            decimal_number_config=dict(num_decimal_places=0, font_size=24),
        )
        axis.move_to([x0 + 30 * unit, -1.6, 0])
        axis_label = Text("seconds to prove n = 13 has no solution", font_size=26, color=GREY_B)
        axis_label.next_to(axis, DOWN)
        self.play(ShowCreation(axis), FadeIn(axis_label))
        self.wait(1.5)

        # One bar per model
        rows = VGroup()
        for k, (name, secs) in enumerate(UNSAT_13):
            y = 1.2 - 0.9 * k
            label = Text(name, font_size=30)
            label.move_to([x0 - 0.3, y, 0], aligned_edge=RIGHT)
            bar = Rectangle(width=max(secs * unit, 0.04), height=0.55)
            bar.set_stroke(width=0)
            bar.set_fill(GREEN if k == 2 else BLUE_D, 1)
            bar.move_to([x0, y, 0], aligned_edge=LEFT)
            value = Text(f"{secs:.2f} s", font_size=28)
            value.next_to(bar, RIGHT, SMALL_BUFF)
            rows.add(VGroup(label, bar, value))
        for label, bar, value in rows:
            self.play(FadeIn(label), GrowFromEdge(bar, LEFT), FadeIn(value),
                      run_time=1.5 if bar.get_width() > 1 else 0.8)

        # Rejected before any search
        highlight = SurroundingRectangle(rows[-1], buff=0.15).set_stroke(YELLOW, 3)
        note = Text("rejected before any search", font_size=34, color=YELLOW)
        note.to_edge(UP, buff=0.6)
        self.play(ShowCreation(highlight), FadeIn(note))
        self.wait(5)


# ---------------------------------------------------------------------------
# 8. Saying why (~13 s)
# ---------------------------------------------------------------------------

class ExplainerScene(InteractiveScene):
    def construct(self):
        # The question and the answer
        question = Text("Why does n = 13 have no solution?", font_size=40)
        question.to_edge(UP, buff=0.8)
        answer = Text(
            "The first copies would have to sit on seats\n"
            "that add up to 247/2, and seats are whole numbers.",
            font_size=32, alignment="LEFT",
        )
        box = SurroundingRectangle(answer, buff=0.35).set_stroke(GREY_C, 2)
        box.round_corners(0.15)
        VGroup(answer, box).next_to(question, DOWN, buff=0.6)
        self.play(Write(question))
        self.play(ShowCreation(box), FadeIn(answer, lag_ratio=0.02, run_time=2))
        self.wait(2)

        # How often it can explain
        explained, total = EXPLAINED
        bar_width = 9.0
        good = Rectangle(width=bar_width * explained / total, height=0.6).set_fill(GREEN, 1).set_stroke(width=0)
        rest = Rectangle(width=bar_width * (total - explained) / total, height=0.6).set_fill(GREY_D, 1).set_stroke(width=0)
        bar = VGroup(good, rest).arrange(RIGHT, buff=0)
        bar.to_edge(DOWN, buff=1.6)
        lab1 = Text(f"{explained} explained", font_size=28).next_to(good, UP)
        lab2 = Text("solver decides", font_size=28, color=GREY_B).next_to(rest, UP)
        caption = Text(f"{total} impossible cases tested", font_size=26, color=GREY_B)
        caption.next_to(bar, DOWN, buff=0.3)
        self.play(GrowFromEdge(good, LEFT), FadeIn(lab1))
        self.play(GrowFromEdge(rest, LEFT), FadeIn(lab2), FadeIn(caption))
        self.wait(3)


SCENE_ORDER = [
    LangfordPuzzle,
    BaselineModel,
    GeneralisedProblem,
    PositionViewpoint,
    ReversalSymmetry,
    ParityArgument,
    ParityThirteen,
    ParityPayoff,
    ExplainerScene,
]
