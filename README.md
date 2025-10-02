# Blunomy Case Study — LiDAR Powerline Catenary Fitting

This project clusters LiDAR point clouds of overhead power lines into individual wires and fits a **catenary** curve to each wire.


## Approach

1. **Clustering**
   - Compute a PCA basis → represent points as `[along, across, normal]`.  
   - Standardize axes.  
   - Cluster with **HDBSCAN** to separate wires (robust to gaps and noise).  

2. **Per-wire fitting**
   - For each cluster, fit a local PCA plane.  
   - Choose the in-plane axis most aligned with global +Z as **y (elevation)**; the orthogonal axis is **x (span)**.  
   - Fit a 2D catenary curve using nonlinear least squares.  
   - Sample the fitted curve in 2D and lift it back into 3D.  

3. **Visualisation**
   - 3D scatter of clusters (coloured) with fitted catenary curves overlaid.  
   - Optional: 2D plots per wire for checking the fit.  


## Repo structure

```
.
├─ data/
├─ src/
│  └─ blunomy/
│     ├─ __init__.py
│     ├─ io.py
│     ├─ clustering.py
│     ├─ fitting.py
│     └─ visualize.py
├─ main.py
├─ requirements.txt
└─ README.md
```

---

## How to run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Place the `.parquet` files in `data/`.  
3. In `main.py`, set the `path` variable to the dataset you want to test.  
4. Run:
   ```bash
   python main.py
   ```
5. The script prints clustering + fitting results and shows 3D plots with wires and fitted curves.

---

## Notes

- The main adjustable parameter is `min_cluster_size` for HDBSCAN (smaller values for sparser datasets).  
- The pipeline is modular: clustering and fitting are independent, so methods can be swapped or extended easily.  
- Outputs include fitted catenary parameters (`c`, `x0`, `y0`) and RMSE error per wire.  
