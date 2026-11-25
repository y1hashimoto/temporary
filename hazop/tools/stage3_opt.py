# -*- coding: utf-8 -*-
"""第3段：整数最適化（HiGHS / PuLP）による対策集合の選定"""
import itertools
import time
from collections import defaultdict
import stage3_model as M


def prepare(res, inst, ACC):
    targets, unach, ok = [], [], []
    for r in res.values():
        A = ACC[r["S"]]
        r["A"] = A
        if not r["paths"]:
            r["status0"] = "原因未確定"
            continue
        if r["G"] <= A:
            ok.append(r); r["status0"] = "対策前に受容"
            continue
        mn = sum(p["H"] * M.best_factor(p, inst) for p in r["paths"])
        r["minfreq"] = mn
        if mn <= A * (1 + 1e-9):
            targets.append(r); r["status0"] = "対策で受容可能"
        else:
            unach.append(r); r["status0"] = "追加検討が必要"
    return targets, unach, ok


def solve(res, inst, ACC, mode, log=print):
    targets, unach, ok = prepare(res, inst, ACC)
    meas = [k for k, m in inst.items() if m["f"] is not None]
    cost = {k: inst[k]["ini"] + 10 * inst[k]["ann"] for k in meas}
    # 重要度の重み（第3目的）：重大度4以上の結果事象・経路への適用数
    w = {k: sum(1 for r in res.values() if r["S"] >= 4 for p in r["paths"] for kk, c, _ in p["app"] if kk == k and c) for k in meas}
    wmax = max(w.values()) or 1
    # 集約ユニット：結果事象×適用対策集合
    units = []
    for r in targets:
        agg = defaultdict(float)
        for p in r["paths"]:
            K = tuple(sorted({k for k, c, _ in p["app"] if c}))
            agg[K] += p["H"]
        units.append((r, list(agg.items())))
    used = sorted({k for _, us in units for K, _ in us for k in K})

    import numpy as np
    import highspy
    INF = highspy.kHighsInf

    def build_solve(stage, fix=None):
        h = highspy.Highs()
        h.setOptionValue("output_flag", False)
        h.setOptionValue("time_limit", 600.0)
        h.setOptionValue("mip_rel_gap", 0.0)
        ncol = [0]
        obj = []

        def col(lb, ub, integer=False):
            h.addVar(lb, ub)
            j = ncol[0]; ncol[0] += 1
            if integer:
                h.changeColIntegrality(j, highspy.HighsVarType.kInteger)
            return j

        def row(lo, hi, idx, val):
            h.addRow(lo, hi, len(idx), np.array(idx, dtype=np.int32), np.array(val, dtype=np.float64))
        x = {k: col(0, 1, True) for k in used}
        for r, us in units:
            ridx, rval, const = [], [], 0.0
            for K, H in us:
                if not K:
                    const += H
                    continue
                ys = []
                for n in range(len(K) + 1):
                    for S in itertools.combinations(K, n):
                        y = col(0, 1)
                        for k in K:
                            if k in S:
                                row(-INF, 0, [y, x[k]], [1, -1])
                            else:
                                row(-INF, 1, [y, x[k]], [1, 1])
                        ys.append(y)
                        ridx.append(y); rval.append(H * M.path_factor(S, inst) / r["A"])
                row(1, 1, ys, [1] * len(ys))
            row(-INF, 1.0 - const / r["A"] + 1e-9, ridx, rval)
        xi = [x[k] for k in used]
        cvec = {x[k]: 0.0 for k in used}
        if mode == "A":
            if stage == 1:
                for k in used: cvec[x[k]] = 1.0
            else:
                row(fix, fix, xi, [1] * len(xi))
                for k in used: cvec[x[k]] = cost[k] - 0.01 * w[k] / wmax
        else:
            if stage == 1:
                for k in used: cvec[x[k]] = cost[k]
            else:
                row(-INF, fix + 1e-6, xi, [cost[k] for k in used])
                for k in used: cvec[x[k]] = 1.0 - 0.01 * w[k] / wmax
        for j, c in cvec.items():
            h.changeColCost(j, c)
        h.run()
        stt = h.modelStatusToString(h.getModelStatus())
        sol = h.getSolution().col_value
        info_ = h.getInfo()
        return stt, h.getInfo().objective_function_value, {k: sol[x[k]] for k in used}, ncol[0], info_.mip_node_count

    t0 = time.time()
    st1, v1, _, nvar, nodes1 = build_solve(1)
    log(f"stage1 status {st1} obj {v1}")
    if mode == "A":
        fix = round(v1)
    else:
        fix = v1
    st2, v2, xs, _, nodes2 = build_solve(2, fix)
    sel = [k for k in used if xs[k] > 0.5]
    info = dict(mode=mode, status=(st1, st2), obj1=v1, nvar=nvar, nbin=len(used), nunits=sum(len(us) for _, us in units),
                ntarget=len(targets), nunach=len(unach), nok=len(ok), secs=time.time() - t0, sel=sel,
                cost=sum(cost[k] for k in sel), count=len(sel), candidates=len(meas), nodes=(nodes1, nodes2))
    log(f"[{mode}] status={st1}/{st2} count={len(sel)} cost={info['cost']:.1f} vars={nvar} bins={len(used)} t={info['secs']:.1f}s")
    return info


def greedy(res, inst, ACC, mode):
    """比較用：貪欲法（採用判断には使わない）"""
    targets, _, _ = prepare(res, inst, ACC)
    meas = [k for k, m in inst.items() if m["f"] is not None]
    cost = {k: inst[k]["ini"] + 10 * inst[k]["ann"] for k in meas}
    sel = set()

    def freq(r):
        return sum(p["H"] * M.path_factor([k for k, c, _ in p["app"] if c and k in sel], inst) for p in r["paths"])
    while True:
        bad = [r for r in targets if freq(r) > r["A"] * (1 + 1e-9)]
        if not bad:
            break
        best, bs = None, -1
        for k in meas:
            if k in sel:
                continue
            sel.add(k)
            gain = sum(1 for r in bad if freq(r) <= r["A"] * (1 + 1e-9)) + 1e-3 * sum(1 for r in bad for p in r["paths"] if any(kk == k and c for kk, c, _ in p["app"]))
            sel.discard(k)
            score = gain / (cost[k] if mode == "B" else 1)
            if gain > 0 and score > bs:
                best, bs = k, score
        if best is None:
            break
        sel.add(best)
    return dict(count=len(sel), cost=sum(cost[k] for k in sel), sel=sel)
