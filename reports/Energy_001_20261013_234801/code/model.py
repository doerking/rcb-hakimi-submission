"""
PyPSA-GB 20-bus reduced model - Energy_001
==========================================
Reproduces Lyden et al. 2024 case study: wind curtailment in Scotland 2035
(Leading the Way scenario), Figs 5(a) and 5(b).

Data:
  - 20 AC buses: Bus1-5 Scotland, Bus6-20 England
  - Scottish onshore wind: 10 GW per bus x 5 buses = 50 GW total
  - English onshore wind: 0.5 GW per bus x 15 buses = 7.5 GW total
  - Gas: ~500 MW per bus, 20 buses total ~10.6 GW
  - Nuclear: 3 buses (Bus2, Bus8, Bus14) x 1200 MW = 3.6 GW
  - PHS storage: Bus1 (300/1800), Bus3 (250/1500), Bus12 (200/1200)
  - 5 SCOT-ENG interlinks @ 1500 MW each (total export cap 7.5 GW)
  - 4 SCOT internal chain links @ 5000 MW
  - 14 ENG internal chain links @ 5000 MW

Two scenarios solved per hour via LP:
  - Constrained: link capacities enforced  -> transmission bottleneck => curtailment
  - Unconstrained: link capacities removed -> all wind dispatched, 0 curtailment
"""
import os
import json
import numpy as np
import pandas as pd
from scipy.optimize import linprog

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs')
IMG_DIR = os.path.join(os.path.dirname(__file__), '..', 'report', 'images')
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)


def load_data():
    buses = pd.read_csv(os.path.join(DATA_DIR, 'buses.csv'))
    gen = pd.read_csv(os.path.join(DATA_DIR, 'generators.csv'))
    links = pd.read_csv(os.path.join(DATA_DIR, 'links.csv'))
    storage = pd.read_csv(os.path.join(DATA_DIR, 'storage.csv'))
    demand = pd.read_csv(os.path.join(DATA_DIR, 'demand.csv'), header=0)
    wind_cf = pd.read_csv(os.path.join(DATA_DIR, 'wind_cf.csv'), header=0)
    return buses, gen, links, storage, demand, wind_cf


def build_caps(buses, gen, links):
    """Extract capacity vectors aligned to bus order."""
    bnames = list(buses['name'])
    n_b = len(bnames)

    wind_gen = gen[gen['carrier'] == 'onshore wind'].set_index('bus')
    gas_gen = gen[gen['carrier'] == 'gas'].set_index('bus')
    nuc_gen = gen[gen['carrier'] == 'nuclear'].set_index('bus')

    wind_cap = np.array([
        float(wind_gen.loc[b, 'p_nom']) if b in wind_gen.index else 0.0
        for b in bnames
    ])
    gas_cap = np.array([
        float(gas_gen.loc[b, 'p_nom']) if b in gas_gen.index else 0.0
        for b in bnames
    ])
    nuc_cap = np.array([
        float(nuc_gen.loc[b, 'p_nom']) if b in nuc_gen.index else 0.0
        for b in bnames
    ])
    return wind_cap, gas_cap, nuc_cap


def build_link_topology(links, bnames):
    """Return matrix [bus_i, link_j] -> +1 if bus_i is bus0 (outflow),
    -1 if bus_i is bus1 (inflow), 0 otherwise."""
    n_b = len(bnames)
    n_l = len(links)
    bidx = {b: i for i, b in enumerate(bnames)}
    M = np.zeros((n_b, n_l))
    for j, row in links.iterrows():
        b0 = bidx[row['bus0']]
        b1 = bidx[row['bus1']]
        M[b0, j] = -1.0  # outflow
        M[b1, j] = +1.0  # inflow
    return M


def solve_hour(dem, wind_avail, wind_cap, gas_cap, nuc_cap, link_cap, M,
               constrain=True, cost_gas=50.0, cost_nuc=10.0, cost_ls=1e5):
    """
    Variables (order):
      0..19   : p_w  wind dispatch per bus
      20..39  : p_g  gas dispatch per bus
      40..59  : p_n  nuclear dispatch per bus (0 for most buses)
      60..82  : f    link flows (signed, |f|<=p_nom if constrain)
      83..102 : ls   load shedding per bus
    """
    n_b = 20
    n_l = len(link_cap)
    N = 20 + 20 + 20 + n_l + 20

    # Objective: minimize cost
    c = np.zeros(N)
    c[20:40] = cost_gas
    c[40:60] = cost_nuc
    c[83 + n_l: 103 + n_l] = cost_ls  # Wait, offset should be 83..83+19 = 102, and n_l=23 means indices 83..102 in the layout. Let me redo.
    # Actually layout: 0-19 p_w, 20-39 p_g, 40-59 p_n, 60-(60+n_l-1) f, (60+n_l)..(60+n_l+19) ls
    c[:] = 0.0
    c[20:40] = cost_gas
    c[40:60] = cost_nuc
    c[(60 + n_l):(60 + n_l + 20)] = cost_ls

    # Bounds
    bounds = []
    bounds += [(0.0, wind_avail[b]) for b in range(20)]   # p_w
    bounds += [(0.0, gas_cap[b]) for b in range(20)]       # p_g
    bounds += [(0.0, nuc_cap[b]) for b in range(20)]       # p_n
    if constrain:
        bounds += [(-link_cap[l], link_cap[l]) for l in range(n_l)]
    else:
        bounds += [(-1e6, 1e6) for l in range(n_l)]
    bounds += [(0.0, dem[b]) for b in range(20)]            # ls (shedding limited by demand)

    # Power balance: for each bus b:
    #   p_w[b] + p_g[b] + p_n[b] - demand[b] + ls[b]
    #     + sum_l M[b,l] * f[l]  = 0
    # => p_w + p_g + p_n + ls + M f = demand
    A_eq = np.zeros((n_b, N))
    b_eq = dem.copy()
    for b in range(n_b):
        A_eq[b, b] = 1.0
        A_eq[b, 20 + b] = 1.0
        A_eq[b, 40 + b] = 1.0
        A_eq[b, 60 + n_l + b] = 1.0
        A_eq[b, 60:60 + n_l] = M[b, :]
        b_eq[b] = dem[b]

    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    if not res.success:
        return None, None, None
    x = res.x
    return x, res.fun, res.success


def run_all():
    buses, gen, links, storage, demand, wind_cf = load_data()
    wind_cap, gas_cap, nuc_cap = build_caps(buses, gen, links)
    link_cap = links['p_nom'].values.astype(float)
    M = build_link_topology(links, list(buses['name']))

    n_hours = demand.shape[0]
    wind_avail = wind_cf.values * wind_cap  # [n_hours, 20]

    # Solve constrained case
    print("Solving constrained LP per hour ...")
    p_w_c = np.zeros((n_hours, 20))
    p_g_c = np.zeros((n_hours, 20))
    p_n_c = np.zeros((n_hours, 20))
    f_c = np.zeros((n_hours, len(link_cap)))
    ls_c = np.zeros((n_hours, 20))
    for t in range(n_hours):
        x, cost, ok = solve_hour(demand.iloc[t].values, wind_avail[t],
                                 wind_cap, gas_cap, nuc_cap, link_cap, M,
                                 constrain=True)
        if x is None:
            print(f"  hour {t}: FAILED")
            continue
        p_w_c[t] = x[0:20]
        p_g_c[t] = x[20:40]
        p_n_c[t] = x[40:60]
        f_c[t] = x[60:60 + len(link_cap)]
        ls_c[t] = x[60 + len(link_cap):]

    # Solve unconstrained case
    print("Solving unconstrained LP per hour ...")
    p_w_u = np.zeros((n_hours, 20))
    for t in range(n_hours):
        x, cost, ok = solve_hour(demand.iloc[t].values, wind_avail[t],
                                 wind_cap, gas_cap, nuc_cap, link_cap, M,
                                 constrain=False)
        if x is None:
            print(f"  hour {t} (unc): FAILED")
            continue
        p_w_u[t] = x[0:20]

    # Curtailment
    curt_c = wind_avail - p_w_c
    curt_u = wind_avail - p_w_u

    tot_avail = wind_avail.sum()
    tot_curt_c = curt_c.sum()
    tot_curt_u = curt_u.sum()
    tot_disp_c = p_w_c.sum()
    tot_disp_u = p_w_u.sum()
    rate_c = 100.0 * tot_curt_c / tot_avail
    rate_u = 100.0 * tot_curt_u / tot_avail

    print(f"Total available wind: {tot_avail/1e6:.4f} TWh")
    print(f"Constrained: dispatched={tot_disp_c/1e6:.4f} TWh, "
          f"curtailed={tot_curt_c/1e6:.4f} TWh, rate={rate_c:.2f}%")
    print(f"Unconstrained: dispatched={tot_disp_u/1e6:.4f} TWh, "
          f"curtailed={tot_curt_u/1e6:.4f} TWh, rate={rate_u:.2f}%")

    # Scottish curtailment breakdown
    scot_avail = wind_avail[:, :5].sum()
    scot_curt = curt_c[:, :5].sum()
    print(f"Scottish only: avail={scot_avail/1e6:.4f} TWh, "
          f"curt={scot_curt/1e6:.4f} TWh, rate={100*scot_curt/scot_avail:.2f}%")

    # Load shedding
    tot_ls = ls_c.sum()
    print(f"Load shedding total: {tot_ls/1e6:.4f} TWh "
          f"({100*tot_ls/demand.values.sum():.2f}% of demand)")

    # Save
    out = {
        'p_w_constrained': p_w_c,
        'p_g_constrained': p_g_c,
        'p_n_constrained': p_n_c,
        'f_constrained': f_c,
        'ls_constrained': ls_c,
        'p_w_unconstrained': p_w_u,
        'wind_avail': wind_avail,
        'curt_c': curt_c,
        'curt_u': curt_u,
        'demand': demand.values,
        'wind_cap': wind_cap,
        'gas_cap': gas_cap,
        'nuc_cap': nuc_cap,
        'link_cap': link_cap,
        'links': links,
        'buses': buses,
        'totals': {
            'avail_TWh': tot_avail / 1e6,
            'disp_c_TWh': tot_disp_c / 1e6,
            'curt_c_TWh': tot_curt_c / 1e6,
            'rate_c_pct': rate_c,
            'disp_u_TWh': tot_disp_u / 1e6,
            'curt_u_TWh': tot_curt_u / 1e6,
            'rate_u_pct': rate_u,
            'scot_rate_pct': 100 * scot_curt / scot_avail,
            'ls_MWh': tot_ls,
        }
    }
    np.savez(os.path.join(OUT_DIR, 'results.npz'), **{k: v for k, v in out.items()
              if isinstance(v, np.ndarray)})
    with open(os.path.join(OUT_DIR, 'totals.json'), 'w') as fh:
        json.dump(out['totals'], fh, indent=2)
    with open(os.path.join(OUT_DIR, 'links.json'), 'w') as fh:
        json.dump(out['links'].to_dict(orient='records'), fh, indent=2)
    with open(os.path.join(OUT_DIR, 'buses.json'), 'w') as fh:
        json.dump(out['buses'].to_dict(orient='records'), fh, indent=2)

    return out


if __name__ == '__main__':
    run_all()
