# Video script: Langford's problem as a CSP

Target: 3 minutes of explanation (scenes 1–8), then 2 minutes of live demo.
Narration is written at about 150 words per minute. The `[cue]` markers say what is on screen when the sentence starts.
Every number below comes from `results.csv` or from running `proj.py`.

Brief requirements this script covers: all members on camera (add your own shots), AI use described in the video (scene 8), 3 + 2 minute structure.

---

## Part 1: Explanation (≈ 3:00)

### 1. `LangfordPuzzle` (0:00 – 0:20)

[title] Langford's problem, CSPLib problem 24. [blocks fall into line] Two copies of each number from one to four: line them up so that between the two copies of *k* sit exactly *k* blocks. [arc, brace] Three blocks between the 3s; [all arcs] the same for every number.

[grid] It works only for some *n*: [pattern] those congruent to 0 or 3 mod 4. Keep that in mind.

### 2. `GeneralisedProblem` (0:20 – 0:33)

[header] A MiniZinc model already exists, so I extended the problem: [params] *s* copies of each number, with consecutive copies of *i* exactly *i* plus *d* apart. [L(3,9)] Three copies of one to nine; [Nickerson] *d* = 0 is the Nickerson variant.

### 3. `PositionViewpoint` (0:33 – 0:58)

[seats] Asking every seat "which number sits here?" leaves the spacing to be checked afterwards. [coupled 3s] Instead, each number gets one variable, *p_i*, the seat of its first copy. Like a train: place the engine and the carriages follow. [p₃ slides] Move *p₃* and both 3s move, so the spacing is never wrong.

[constraints] What remains: the last copy fits, no two copies share a seat, and a channel to print the sequence. [count] The search branches on *n* variables, not *s* times *n*.

### 4. `ReversalSymmetry` (0:58 – 1:13)

[mirror] Every solution read backwards is another solution. [rule] I keep the one whose positions are lexicographically smaller, compared in the order the search branches so they don't fight. [table] At *n* = 12: half the nodes.

### 5. `ParityArgument` (1:13 – 1:38)

[shaded seats] My favourite idea: shade the odd seats. [4 and 2] An even number has an odd gap, so it takes exactly one odd seat. [3 and 1] An odd number's copies share a colour: they arrive as a couple.

[count] *n* odd seats; the even numbers take one each; couples fill the rest two at a time, so the rest must be even. [last line] That is exactly *n* ≡ 0 or 3 mod 4.

### 6. `ParityThirteen` (1:38 – 1:50)

[13 seats] At 13: six seats for the even numbers, seven left. [pairs] Couples fill six; [red seat] one is always empty. [model] As a constraint, MiniZinc rejects the instance before searching.

### 7. `ParityPayoff` (1:50 – 2:00)

[n = 13] The baseline needs 52 seconds to prove *n* = 13 impossible, my model without the cut 47. With it: six hundredths of a second. [n = 14] At 14, only the cut finishes.

### 8. `ExplainerScene` (2:00 – 2:20)

[terminal] "Unsatisfiable" doesn't say *why*, so `proj.py` explains. [sum] The seat numbers have a fixed total, so the first positions must sum to 287 over 2: [cross] not a whole number. Like a receipt that doesn't add up. [bar] It explains 40 of 68 impossible test instances, every classic one. [limitation] For now, only after the solver answers.

### 9. `HonestResults` (2:20 – 2:35)

[table] Not everything helped: the search modes gave no clear gain, the cardinality constraint changed nothing, and Chuffed was five times slower. [correctness] 1084 runs against brute force, zero mismatches.

### 10. `ToolsUsed` (2:35 – 2:50)

[columns] The generalisation, parity argument, search modes and explainer are my design. Claude Code set up MiniZinc, rewrote the symmetry constraint, wrote the self-test and ran the benchmark. [footer] Claude helped write the report and this animation.

---

## Part 2: Demo (≈ 2:00, live terminal)

Run these in order. Times are from the benchmark machine; yours will differ slightly.

| # | Command | What to say |
|---|---|---|
| 1 | `python3 proj.py 8` | First solution, checked by the independent checker (`valid=True`). |
| 2 | `python3 proj.py 7 -s 3 -d 2 --all` | The extension: three copies, offset 2, all solutions counted. |
| 3 | `python3 proj.py 6` | Impossible instance, solved quickly, and the explainer's sentence. |
| 4 | `python3 proj.py 14 --parity` | The parity cut: proved instantly. |
| 5 | `python3 proj.py 12 --all` then `--no-sym` | Symmetry breaking: 108,144 vs 216,288 solutions. Takes ~8 s and ~15 s. |
| 6 | Show the end of a `--selftest` log and `results.csv` | The full self-test takes long; show a saved log rather than running it live. |

---

## Before recording

- If you present as a pair, change "I/my" to "we/our".
- Scene 1: the numbers shown (3, 4, 7, 8, 11, 12) are where solutions exist. That pattern is a known result; your model and explainer confirm it.
- Scene 8: the terminal text is what `proj.py` prints for n=14, but split across two lines for readability. Replace the time with the one from your own run if it differs.
- The animation code itself was written with Claude. Scene 10 says so; the report's reflection section does not yet. Add one sentence there.
