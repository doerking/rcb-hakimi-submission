"""Run GP LOOCV once and cache results."""
import numpy as np
import pandas as pd
import os
from utils import gp_loocv_calibration, DATA_DIR

out_dir = r'I:\hakimi-engineX\outputs\rcb\repo\workspaces\Material_003_20261014_013623\code'
cache_path = os.path.join(out_dir, 'gp_loocv_cache.npz')

if os.path.exists(cache_path):
    print('Loading cached GP results...')
    data = np.load(cache_path)
    gp_res = {k: data[k] for k in data.files}
    gp_res['metrics'] = {k: float(data[k]) for k in ['mae', 'rmse', 'r2', 'bias']}
    print(f'Metrics: {gp_res["metrics"]}')
else:
    df = pd.read_csv(os.path.join(DATA_DIR, 'tg_calibration.csv'))
    print(f'Running GP LOOCV on {len(df)} polymers...')
    gp_res = gp_loocv_calibration(df, verbose=True)
    np.savez(cache_path,
             y_exp=gp_res['y_exp'],
             y_md=gp_res['y_md'],
             preds_delta=gp_res['preds_delta'],
             y_calibrated=gp_res['y_calibrated'],
             mae=gp_res['metrics']['mae'],
             rmse=gp_res['metrics']['rmse'],
             r2=gp_res['metrics']['r2'],
             bias=gp_res['metrics']['bias'])
    print('Cached.')
    print(f'Metrics: {gp_res["metrics"]}')
