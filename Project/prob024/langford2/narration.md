# Video script: Langford's problem as a CSP

Explanation: 2:48 of animation (`videos/langford_full.mp4`), then about 2 minutes of live demo, so the whole video is under the 3 + 2 minute limit.

The `[cue]` markers say what is on screen when the sentence starts. Scene names are the classes in `langford.py`, and times are where each scene starts and ends in `langford_full.mp4`. The narration is paced at about 150 words per minute: speak calmly and let the pauses breathe.

The thread: **a puzzle with a strange pattern → how the original model attacks it → our extension → our key idea → why the pattern holds → how that proof makes the solver instant → explaining "no solution".**

---

## Part 1: Explanation (0:00 – 2:48)

### 1. `LangfordPuzzle` (0:00 – 0:29)

[title] Here's a puzzle. [blocks fall into line] Take two copies of each number from one to four, and line them up so that [arcs] the two ones have one block between them, the two twos have two, the threes three.

[grid] For which *n* can you do this? [ticks and crosses] A strange pattern shows up. [yellow line] It only ever works when *n* is 0 or 3 mod 4. [question] Why would a puzzle about gaps care about the number four? Hold that thought.

### 2. `BaselineModel` (0:29 – 0:56)

[pairs above the seats] The model we started from gives every copy its own unknown seat, [arcs with +2, +3…] with a rule tying each pair together: the second copy sits *i* plus one seats after the first.

[blocks drop in, the 4 falls off the end] The solver tries seats, and when something doesn't fit, it backs up and tries again. [list] But it only knows pairs, and when there's no solution, it has to rule out every arrangement: fifty-two seconds for thirteen.

### 3. `GeneralisedProblem` (0:56 – 1:07)

[header] So we asked for more: [two lines] *s* copies of each number, with consecutive copies *i* plus *d* apart. [long row] Here are three copies of one to nine.

### 4. `PositionViewpoint` (1:07 – 1:28)

[two 3s, linked] Here's the key idea. If you know where the first 3 sits, you already know where every 3 sits.

[p₃ slides] So in our model, only the first copy is an unknown. Move it, and the rest follow. [yellow line] That's *n* unknowns instead of 2*n*, and the gaps can never be wrong, however many copies.

### 5. `ReversalSymmetry` (1:28 – 1:38)

[row flips] And any solution read backwards is another solution. [cross] So we only keep one of each pair, and the search is cut in half.

### 6. `ParityArgument` (1:38 – 1:59)

[shading] Now, back to that pattern. Shade every other seat.

[4s, then 2s] An even number has an odd gap, so exactly one of its copies lands on a shaded seat. [3s, then 1s] An odd number has an even gap: both copies are shaded, or neither. [yellow line] So on shaded seats, odd numbers always arrive in pairs.

### 7. `ParityThirteen` (1:59 – 2:25)

[13 circles] Try thirteen. There are thirteen shaded seats. [even tiles] The six even numbers take one each, [brace] seven are left, and the odd numbers can only fill them two at a time. [red seat] Seven is odd. One seat is always empty, so no arrangement can work.

[yellow formula] Do the same count for any *n*, and the leftover is even exactly when *n* is 0 or 3 mod 4. That's our pattern.

### 8. `ParityPayoff` (2:25 – 2:37)

[bars] And a proof is something the solver can use. We gave it this count as a constraint, [green bar] and thirteen is now rejected before any search: six hundredths of a second.

### 9. `ExplainerScene` (2:37 – 2:48)

[question and answer] Finally, when there's no solution, our program tells you *why*. [bar] It explains 40 of the 68 impossible cases we tested.

---

## Part 2: Demo (≈ 2:00, live terminal)

Run these in order. Times are from the benchmark machine; yours will differ slightly.

| # | Command | What to say |
|---|---|---|
| 1 | `python3 proj.py 8` | A solution for eight, checked by an independent checker (`valid=True`). |
| 2 | `python3 proj.py 9 -s 3 --all` | The extension: three copies of one to nine, as in the video. All 3 solutions (up to reversal), each checked. The original model can't express this. |
| 3 | `python3 proj.py 6` | No solution, and the program says why. |
| 4 | `python3 proj.py 14 --parity` | With the parity count, proved impossible instantly. |
| 5 | `python3 proj.py 12 --all` then `--no-sym` | Mirror images: 108,144 vs 216,288 solutions. Takes ~8 s and ~15 s. |
| 6 | Show the end of a `--selftest` log | Every option checked against brute force: 1084 runs, zero mismatches. The full self-test is slow; show a saved log. |

---

## Before recording

- Both members must appear on camera; split the scenes between you.
- Scene 7: "Do the same count for any *n*" shows why solutions can *only* exist for 0 or 3 mod 4. That they always exist for those *n* is a known result, not something we prove.
- Scene 9: the sentence on screen is what `proj.py` prints for *n* = 13 (sum 247/2), reworded for viewers.
