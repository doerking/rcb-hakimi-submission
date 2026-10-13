"""structure_map.py — 多立场「交集」结构图：缺席(human/LLM/source) × 注者分歧 × in_paper"""
import yaml, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
d=yaml.safe_load(open(ROOT/"data"/"2111.01152"/"2111.01152.yaml",encoding="utf-8"))
steps=[it for it in d if isinstance(it,dict) and "placeholder" in it]
H=[];L=[];SP=[];INP=[];SRC=[]
for s in steps:
    hp=lp=0; sp=[]
    for k,v in s["placeholder"].items():
        if not isinstance(v,dict): continue
        if v.get("human") in (None,""): hp+=1
        if v.get("LLM") in (None,""): lp+=1
        sc=v.get("score") or {}; a=[sc.get(x) for x in ("Haining","Will","Yasaman")]
        a=[x for x in a if isinstance(x,(int,float))]
        if len(a)==3: sp.append(max(a)-min(a))
    H.append(hp); L.append(lp); SP.append(np.mean(sp) if sp else 0)
    INP.append((s.get("score") or {}).get("in_paper",0)); SRC.append(1 if s.get("source") else 0)
x=np.arange(1,17)
fig,ax=plt.subplots(figsize=(8.4,4.4))
ax.bar(x-0.30, H, width=0.28, color="#777", label="human answer ABSENT (#)")
ax.bar(x-0.02, L, width=0.28, color="tab:red", label="LLM answer ABSENT (#)")
ax.bar(x+0.26, SP, width=0.28, color="tab:orange", label="annotator spread (avg)")
ax.plot(x, INP, "k.--", lw=1, ms=7, label="in_paper (grounding)")
for xi,has in zip(x, SRC):
    if not has: ax.axvline(xi, color="red", alpha=0.15, lw=8)
ax.text(4, max(H)+0.6, "early: annotation present, conventions ambiguous", ha="center", fontsize=8)
ax.text(15, max(H)+0.6, "late: NO LLM answer, NO source anchor", ha="center", fontsize=8, color="red")
ax.set_xticks(x); ax.set_xlabel("derivation step (1..16)"); ax.set_ylabel("count / value")
ax.set_title("Multi-position intersections: absence structure × annotator ambiguity × grounding\n(red bars = absent positions; shaded columns = no source anchor)")
ax.legend(fontsize=7.5, ncol=2); ax.grid(alpha=.3, axis="y")
fig.tight_layout(); fig.savefig(ROOT/"report"/"images"/"structure_map.png", dpi=130)
print("saved; human缺席",sum(H),"LLM缺席",sum(L),"source缺席步",[i+1 for i,s in enumerate(SRC) if not s])
