import argparse, csv, statistics, sys, time, warnings
from datetime import timedelta
from fractions import Fraction
from pathlib import Path
import minizinc   # pip install minizinc; the MiniZinc binary is installed separately

# Debian's Gecode library redefines some globals; MiniZinc warns about each one on every solve
warnings.filterwarnings("ignore", message=".*overrides a global constraint file")
# the parity cut proves UNSAT at compile time; that already shows up as status UNSATISFIABLE
warnings.filterwarnings("ignore", message="model inconsistency detected")

# a MiniZinc next to the interpreter (the bundle linked into the venv) wins over the system one,
# which is too old to have Chuffed
LOCAL_MZN = Path(sys.executable).parent / "minizinc"
if LOCAL_MZN.exists():
    minizinc.Driver(LOCAL_MZN).make_default()

def lookup(solver):
    # Solver.lookup returns the first match; with two installs that is the old system Gecode,
    # which the bundled MiniZinc cannot drive. Take the newest version instead.
    found = minizinc.default_driver.available_solvers().get(solver, [])
    if not found:
        raise LookupError(f"solver '{solver}' is not installed (see: minizinc --solvers)")
    return max(found, key=lambda x: [int(v) for v in x.version.split(".") if v.isdigit()])

HERE = Path(__file__).resolve().parent   # models are found next to this file, whatever the cwd
MODEL_FILES = {"baseline": HERE / "langford2.mzn", "improved": HERE / "langford_gen.mzn"}
SEQ_FIELD   = {"baseline": "solution",              "improved": "seq"}

# ---------- explainer: cheap necessary conditions ----------
def explain(n, s=2, d=1):
    N, span = s * n, (s - 1) * (n + d) + 1
    if span > N:
        return False, f"number {n} needs {span} positions but the sequence has only {N}."
    # sum of all positions = N(N+1)/2 = sum_i [ s*p_i + s(s-1)/2 * (i+d) ]  =>  sum(p_i) must be an integer
    sum_p = Fraction(n * (2 * (s * n + 1) - (s - 1) * (n + 1 + 2 * d)), 4)
    if sum_p.denominator != 1:
        extra = f" (the n = 0,3 mod 4 rule; here n mod 4 = {n % 4})" if (s, d) == (2, 1) else ""
        return False, f"the first positions would have to sum to {sum_p}, not an integer{extra}."
    return True, "no simple counting argument rules it out; the solver has to decide."

# ---------- independent checker ----------
def check(seq, n, s=2, d=1):
    if sorted(seq) != sorted(i for i in range(1, n + 1) for _ in range(s)):
        return False
    for i in range(1, n + 1):
        pos = [q for q, v in enumerate(seq) if v == i]
        if any(b - a != i + d for a, b in zip(pos, pos[1:])):
            return False
    return True

# ---------- independent enumerator (pure Python backtracking, small instances only) ----------
def brute(n, s=2, d=1):
    N, seq, used, out = s * n, [0] * (s * n), [False] * (n + 1), []
    def fill(q):   # always fill the leftmost empty position
        while q < N and seq[q]:
            q += 1
        if q == N:
            out.append(tuple(seq)); return
        for i in range(1, n + 1):
            cells = range(q, q + (s - 1) * (i + d) + 1, i + d)
            if not used[i] and cells[-1] < N and not any(seq[c] for c in cells):
                used[i] = True
                for c in cells: seq[c] = i
                fill(q + 1)
                used[i] = False
                for c in cells: seq[c] = 0
    fill(0)
    return out

# ---------- one run ----------
def run(model="improved", solver="gecode", n=8, s=2, d=1, mode=3,
        gcc=False, parity=False, count_all=False, timeout=60, sym=True):
    # with count_all, status SATISFIED (not ALL_SOLUTIONS) means the timeout cut the enumeration short
    inst = minizinc.Instance(lookup(solver), minizinc.Model(MODEL_FILES[model]))
    if model == "baseline":
        inst["k"] = n
    else:
        inst["n"] = n; inst["s"] = s; inst["d"] = d
        inst["search_mode"] = mode
        inst["use_gcc"] = gcc; inst["use_parity_cut"] = parity
        inst["break_symmetry"] = sym
    t0 = time.perf_counter()
    res = inst.solve(all_solutions=count_all, timeout=timedelta(seconds=timeout))
    wall = time.perf_counter() - t0
    raw = res.solution
    sols = [] if raw is None else (raw if isinstance(raw, list) else [raw])
    seqs = [tuple(getattr(x, SEQ_FIELD[model])) for x in sols]
    ok = all(check(q, n, s, d) for q in seqs) if seqs else None   # None: nothing to check
    return {"status": res.status.name, "n_sol": len(set(seqs)), "valid": ok,
            "wall": wall, "stats": res.statistics, "first": seqs[0] if seqs else None}

def report(n, s, d, r, count_all=False):
    if r["first"]:
        cut = " so far (timed out, count incomplete)" if count_all and r["status"] != "ALL_SOLUTIONS" else ""
        print(f"n={n}: {r['status']}, {r['n_sol']} solution(s){cut}, valid={r['valid']}, {r['wall']:.2f}s")
        print("  e.g.", "".join(map(str, r["first"])) if n < 10 else r["first"])
    elif r["status"] == "UNSATISFIABLE":
        print(f"n={n}: UNSATISFIABLE in {r['wall']:.2f}s. Explainer: {explain(n, s, d)[1]}")
    else:
        print(f"n={n}: {r['status']} (probably timeout after {r['wall']:.0f}s)")

# ---------- benchmark ----------
CONFIGS = [  # label, model, solver, mode, gcc, parity, sym
    ("baseline/gecode",     "baseline", "gecode", 0, False, False, True),   # mode/gcc/parity/sym unused
    ("improved-m1/gecode",  "improved", "gecode", 1, False, False, True),
    ("improved-m3/gecode",  "improved", "gecode", 3, False, False, True),
    ("improved-m3-nosym",   "improved", "gecode", 3, False, False, False),
    ("improved-m3+gcc",     "improved", "gecode", 3, True,  False, True),
    ("improved-m3+parity",  "improved", "gecode", 3, False, True,  True),
    ("improved/chuffed",    "improved", "chuffed", 3, False, False, True),
]
KINDS = [("count", [3, 4, 7, 8, 11, 12], True),          # validation
         ("first", [15, 16, 19, 20, 23, 24], False),     # scaling
         ("unsat", [5, 6, 9, 10, 13, 14], False)]        # proving UNSAT

def available(solver):
    try:
        lookup(solver)
        return True
    except LookupError:
        return False

def benchmark(reps=3, timeout=60, out="results.csv"):
    configs = [c for c in CONFIGS if available(c[2])]
    for c in CONFIGS:
        if c not in configs:
            print(f"skipping {c[0]}: solver '{c[2]}' is not installed")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["kind", "config", "n", "status", "n_sol", "valid", "median_s", "nodes"])
        for kind, sizes, count in KINDS:
            for n in sizes:
                for label, model, solver, mode, gcc, par, sym in configs:
                    rs = [run(model, solver, n, 2, 1, mode, gcc, par, count, timeout, sym)]
                    # a timeout would just time out again: only repeat runs that finished
                    while len(rs) < reps and rs[0]["status"] != "UNKNOWN":
                        rs.append(run(model, solver, n, 2, 1, mode, gcc, par, count, timeout, sym))
                    row = [kind, label, n, rs[0]["status"], rs[0]["n_sol"], rs[0]["valid"],
                           round(statistics.median(r["wall"] for r in rs), 3),
                           rs[0]["stats"].get("nodes")]
                    w.writerow(row)
                    f.flush()
                    print(*row)

# ---------- self-test: every model/option against the enumerator ----------
SELFTEST = {2: 10, 3: 10, 4: 9}   # s -> largest n that brute() still enumerates quickly

def selftest(timeout=60):
    solvers = [x for x in ("gecode", "chuffed") if available(x)]
    bad = runs = 0
    def expect(what, r, want):
        nonlocal bad, runs
        runs += 1
        got = r["n_sol"] if r["status"] in ("ALL_SOLUTIONS", "UNSATISFIABLE") else r["status"]
        if got != want or r["valid"] is False:
            bad += 1
            print(f"  MISMATCH {what}: got {got}, expected {want}, valid={r['valid']}")
    for s, top in SELFTEST.items():
        for d in (0, 1, 2):
            for n in range(1, top + 1):
                sols = brute(n, s, d)
                total, orbits = len(sols), len({min(q, q[::-1]) for q in sols})
                tag = f"L(s={s},n={n},d={d})"
                if not all(check(q, n, s, d) for q in sols):
                    bad += 1; print(f"  MISMATCH {tag}: checker rejects an enumerated sequence")
                if total and not explain(n, s, d)[0]:
                    bad += 1; print(f"  MISMATCH {tag}: explainer says impossible, but {total} sequences exist")
                for solver in solvers:
                    kw = dict(solver=solver, n=n, s=s, d=d, count_all=True, timeout=timeout)
                    expect(f"{tag} {solver} no-sym", run(sym=False, **kw), total)
                    for mode in range(4):
                        expect(f"{tag} {solver} mode {mode}", run(mode=mode, **kw), orbits)
                    expect(f"{tag} {solver} gcc", run(gcc=True, **kw), orbits)
                    if (s, d) == (2, 1):
                        expect(f"{tag} {solver} parity", run(parity=True, **kw), orbits)
                        expect(f"{tag} {solver} baseline", run("baseline", **kw), orbits)
            print(f"s={s} d={d}: n=1..{top} done")
    print(f"selftest: {runs} solver runs on {'+'.join(solvers)}, {bad} mismatch(es)")
    return bad == 0

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int, nargs="?", default=8)
    ap.add_argument("-s", type=int, default=2)
    ap.add_argument("-d", type=int, default=1)
    ap.add_argument("--solver", default="gecode")
    ap.add_argument("--mode", type=int, default=3)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--no-sym", action="store_true", help="keep both a sequence and its reverse")
    ap.add_argument("--gcc", action="store_true", help="add the redundant cardinality constraint")
    ap.add_argument("--parity", action="store_true", help="add the parity cut (s=2, d=1 only)")
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--benchmark", action="store_true")
    ap.add_argument("--selftest", action="store_true", help="compare all models with brute force")
    ap.add_argument("--reps", type=int, default=3, help="benchmark repetitions per instance")
    ap.add_argument("--out", default="results.csv", help="benchmark output file")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest(a.timeout) else 1)
    elif a.benchmark:
        benchmark(a.reps, a.timeout, a.out)
    elif not available(a.solver):
        ap.error(f"solver '{a.solver}' is not installed (see: minizinc --solvers)")
    else:
        report(a.n, a.s, a.d, run("improved", a.solver, a.n, a.s, a.d, a.mode, a.gcc, a.parity,
                                  a.all, a.timeout, not a.no_sym), a.all)