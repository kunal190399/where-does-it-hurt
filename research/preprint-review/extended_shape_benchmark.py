"""Mask-level synthetic extension for irregular and disconnected ground-truth regions.

This is deliberately distinct from the original convex-hull pipeline: it tests the
consensus-vs-intersection aggregation question when annotations preserve arbitrary
region masks. It must not be described as a direct validation of original polygon clipping.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.path import Path as MplPath
from shapely.affinity import rotate, scale, translate
from shapely.geometry import Polygon, MultiPolygon
from synthetic_pain_mapping import (NOISE_LEVELS, ANNOTATOR_COUNTS, CONSENSUS_THRESHOLDS,
                                    make_grid, iou, precision_recall, bootstrap_mean_ci)

GRID=100

def ellipse(cx, cy, rx, ry, n=120, angle=0):
    t=np.linspace(0,2*np.pi,n,endpoint=False)
    pts=np.c_[rx*np.cos(t),ry*np.sin(t)]
    c,s=np.cos(angle),np.sin(angle)
    return Polygon(pts @ np.array([[c,s],[-s,c]]) + [cx,cy])

def make_truth(kind, rng):
    cx,cy=rng.uniform(.40,.60,2)
    if kind=='ellipse':
        return ellipse(cx,cy,rng.uniform(.12,.18),rng.uniform(.09,.15),angle=rng.uniform(0,2*np.pi))
    if kind=='irregular':
        n=int(rng.integers(8,15)); angles=np.sort(rng.uniform(0,2*np.pi,n))
        radii=rng.uniform(.075,.17,n)
        pts=np.c_[cx+radii*np.cos(angles),cy+radii*np.sin(angles)]
        geom=Polygon(pts).buffer(0)
        if not geom.is_valid or geom.area<.002: return make_truth(kind,rng)
        return geom
    if kind=='disconnected':
        sep=rng.uniform(.07,.12)
        a=ellipse(cx-sep/2,cy,rng.uniform(.045,.075),rng.uniform(.05,.08),angle=rng.uniform(0,2*np.pi))
        b=ellipse(cx+sep/2,cy+rng.uniform(-.03,.03),rng.uniform(.045,.075),rng.uniform(.05,.08),angle=rng.uniform(0,2*np.pi))
        return MultiPolygon([a,b])
    raise ValueError(kind)

def polygons(geom):
    if geom.geom_type=='Polygon': return [geom]
    if geom.geom_type=='MultiPolygon': return list(geom.geoms)
    if geom.geom_type=='GeometryCollection': return [g for g in geom.geoms if g.geom_type=='Polygon']
    return []

def rasterize(geom, points, size=GRID):
    mask=np.zeros(len(points),dtype=bool)
    for poly in polygons(geom):
        mask |= MplPath(np.asarray(poly.exterior.coords),closed=True).contains_points(points)
        for ring in poly.interiors:
            mask &= ~MplPath(np.asarray(ring.coords),closed=True).contains_points(points)
    return mask.reshape(size,size)

def perturb_geometry(geom,rng,noise):
    minx,miny,maxx,maxy=geom.bounds; cx=(minx+maxx)/2; cy=(miny+maxy)/2
    out=translate(geom,xoff=-cx,yoff=-cy)
    factor=max(.65,rng.normal(1,noise*1.4))
    out=scale(out,xfact=factor,yfact=factor,origin=(0,0))
    out=rotate(out,float(rng.normal(0,noise*1.4)*180/np.pi),origin=(0,0))
    out=translate(out,xoff=cx+rng.normal(0,noise),yoff=cy+rng.normal(0,noise))
    delta=float(rng.normal(0,noise*.45))
    if abs(delta)>1e-8:
        try: out=out.buffer(delta,join_style=1)
        except Exception: pass
    return out

def run(seed=20261029,repetitions=30,grid_size=GRID):
    rng=np.random.default_rng(seed); _,points=make_grid(grid_size); rows=[]; examples={}
    for kind in ('ellipse','irregular','disconnected'):
      for noise in NOISE_LEVELS:
       for n in ANNOTATOR_COUNTS:
        for rep in range(repetitions):
         truth_geom=make_truth(kind,rng); truth=rasterize(truth_geom,points,grid_size)
         masks=np.stack([rasterize(perturb_geometry(truth_geom,rng,noise),points,grid_size) for _ in range(n)])
         freq=masks.mean(axis=0); strict=masks.all(axis=0)
         for threshold in CONSENSUS_THRESHOLDS:
          pred=freq>=threshold; p,r=precision_recall(pred,truth)
          rows.append(dict(shape=kind,noise_sd=noise,annotators=n,replicate=rep,method=f'frequency_threshold_{threshold:.1f}',threshold=threshold,
                           iou=iou(pred,truth),precision=p,recall=r,predicted_area_fraction=float(pred.mean()),truth_area_fraction=float(truth.mean())))
         p,r=precision_recall(strict,truth)
         rows.append(dict(shape=kind,noise_sd=noise,annotators=n,replicate=rep,method='strict_intersection',threshold=np.nan,
                          iou=iou(strict,truth),precision=p,recall=r,predicted_area_fraction=float(strict.mean()),truth_area_fraction=float(truth.mean())))
         if noise==.03 and n==5 and rep==0: examples[kind]=(truth,freq,strict)
    return pd.DataFrame(rows),examples

def main():
 p=argparse.ArgumentParser(); p.add_argument('--out',default='outputs'); p.add_argument('--seed',type=int,default=20261029); p.add_argument('--repetitions',type=int,default=30); a=p.parse_args()
 out=Path(a.out); out.mkdir(parents=True,exist_ok=True); raw,examples=run(a.seed,a.repetitions)
 raw.to_csv(out/'extended_shape_benchmark_raw.csv',index=False)
 summary=raw.groupby(['shape','noise_sd','annotators','method'],as_index=False).agg(iou_mean=('iou','mean'),iou_sd=('iou','std'),precision_mean=('precision','mean'),recall_mean=('recall','mean'),predicted_area_mean=('predicted_area_fraction','mean'))
 summary.to_csv(out/'extended_shape_benchmark_summary.csv',index=False)
 thresh=raw[raw.threshold.notna()].groupby(['shape','noise_sd','annotators','threshold'],as_index=False).agg(iou_mean=('iou','mean'),iou_sd=('iou','std'),precision_mean=('precision','mean'),recall_mean=('recall','mean'),predicted_area_mean=('predicted_area_fraction','mean'))
 thresh.to_csv(out/'extended_threshold_sensitivity_summary.csv',index=False)
 wide=raw.pivot(index=['shape','noise_sd','annotators','replicate'],columns='method',values='iou').reset_index()
 wide['consensus05_minus_strict_iou']=wide['frequency_threshold_0.5']-wide['strict_intersection']; wide.to_csv(out/'extended_paired_case_iou.csv',index=False)
 overall=wide.groupby('shape')['consensus05_minus_strict_iou'].apply(lambda x: bootstrap_mean_ci(x.to_numpy())).reset_index(name='paired_mean_ci')
 overall.to_csv(out/'extended_paired_iou_ci_by_shape.csv',index=False)
 fig,axes=plt.subplots(1,3,figsize=(12,3.6),sharey=True,constrained_layout=True)
 for ax,shape in zip(axes,('ellipse','irregular','disconnected')):
  part=thresh[(thresh.shape==shape)&(thresh.annotators==5)]
  for noise in NOISE_LEVELS:
   q=part[part.noise_sd==noise].groupby('threshold',as_index=False).iou_mean.mean()
   ax.plot(q.threshold,q.iou_mean,marker='o',label=f'noise={noise:g}')
  ax.set_title(shape); ax.set_xlabel('Frequency threshold'); ax.grid(True,alpha=.25)
 axes[0].set_ylabel('Mean IoU'); axes[-1].legend(fontsize=7)
 fig.savefig(out/'extended_threshold_sensitivity.png',dpi=180); plt.close(fig)
 fig,axes=plt.subplots(3,3,figsize=(8,8),constrained_layout=True)
 for i,shape in enumerate(('ellipse','irregular','disconnected')):
  for j,(label,maskidx) in enumerate((('Truth',0),('Frequency',1),('Strict',2))):
   axes[i,j].imshow(examples[shape][maskidx],origin='lower',vmin=0,vmax=1); axes[i,j].set_title(f'{shape}: {label}'); axes[i,j].set_xticks([]); axes[i,j].set_yticks([])
 fig.savefig(out/'extended_shape_examples.png',dpi=180); plt.close(fig)
 print('cases',len(wide),'rows',len(raw)); print(summary[(summary.noise_sd==.03)&(summary.annotators==5)&summary.method.isin(['frequency_threshold_0.5','strict_intersection'])].to_string(index=False)); print(thresh.groupby(['shape','threshold'])[['iou_mean','precision_mean','recall_mean']].mean().round(4).to_string())
if __name__=='__main__': main()
