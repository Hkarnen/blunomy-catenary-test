# Clustering Lidar Cable Points – Notes

### Initial Approach: DBSCAN (3D)
Method: Applied DBSCAN directly on (x, y, z) point cloud.

Problem: Very sensitive to eps value.
Too small → everything marked as noise.
Too large → all wires merged into one cluster.
Tiny changes in eps caused unstable results.

Conclusion: Not reliable for gappy, skinny structures like wires.

### Attempt 2: DBSCAN (with StandardScaler)

Idea: Normalize axis ranges so z (vertical separation) isn’t dominated by long spans in x,y.

Result: Slightly more stable, but still merged wires when gaps appeared.

Conclusion: Scaling helped, but eps tuning was still brittle.

### Attempt 3: HDBSCAN (2D Projection)
Method: Used PCA to project (x,y,z) → (along, across) plane. Clustered with HDBSCAN in 2D.

Result: Worked for easy dataset (3 wires clean).
Failed for medium dataset: collapsed stacked layers (top vs bottom) into one cluster because vertical separation (normal axis) was discarded.

Conclusion: Projection to 2D was too aggressive—lost important vertical information.

### Attempt 4: HDBSCAN (3D with weights, Scaled)
Method: Kept PCA 3D local frame (along, across, normal).
Applied weights:
Down-weight along (to avoid splitting gaps).
Up-weight across and normal (to separate adjacent/stacked wires).

Result:
Correctly split stacked layers in medium dataset.
Allowed finer control, but required tuning of weights and parameters.

Conclusion: Effective, but more knobs than necessary.

### Final Approach: HDBSCAN (3D Unweighted, Scaled)
Method:
PCA → local 3D coords [along, across, normal].
StandardScaler to equalize axis contributions.
HDBSCAN clustering, no extra weights.

Results:
Easy: 3 clusters (3 wires).
Medium: 7 clusters (top + bottom sets of wires).
Hard: Needed smaller min_cluster_size (100 instead of 200) to account for bigger gaps; worked fine.
Extra-hard: Also worked with smaller min_cluster_size.

Conclusion:
Robust across all datasets.
Only parameter to adjust is min_cluster_size (based on dataset density).
No weighting needed.

# Fitting Catenary Curves – Notes

### Initial Step: Plane Fitting with PCA

For each wire cluster, fit a 2D plane using PCA.
Goal: get a local coordinate system:
x = along the wire (span).
y = elevation (axis most aligned with global +Z).

Problem: If we didn’t align y to +Z, the catenary fit sometimes flattened into a horizontal line.

Fix: Always pick the in-plane axis most aligned with +Z as y.

### Attempt 1: Direct 3D Fit

Idea: Fit catenary directly in 3D.

Problem: Formula is inherently 2D (y(x)), so 3D fitting is ill-posed. Needed extra parameters.

Conclusion: Too complex for the assessment scope. Dropped.

### Attempt 2: 2D Fit (Wrong Axis Alignment)

Projected cluster into 2D PCA plane. Fit catenary curve with least-squares.

Problem: PCA axes don’t guarantee y ≈ vertical → fitted curves sometimes turned into near-flat lines (at y=0).

Conclusion: Needed to align the “y” axis to elevation.

### Final Approach: 2D Fit with Vertical-Aligned Axis

PCA → choose axis most aligned with global +Z as “y” (elevation). Other axis = “x” (along-wire).

Fit catenary in this (x,y) plane: Parameters: c (curvature), x0 (horizontal shift, trough), y0 (vertical shift).

Initial guess: trough = lowest point in cluster; c ≈ span/π.

Used SciPy least_squares for robust fitting.

Worked consistently across easy, medium, hard, extra-hard.

**Visualization**

3D plots: all clusters colored

2D plots (per wire cluster): raw points + fitted catenary.

3D plots: all clusters colored + fitted curves overlaid.

**Results Across Datasets**

Easy: 3 wires, all fitted well.

Medium: 7 wires (two stacked sets), separated and fitted correctly.

Hard: Larger gaps required lowering min_cluster_size; fits worked fine.

Extra-hard: Similar to hard; stable with same parameters.

**Overall Conclusion (Post-Clustering)**

Pipeline is stable:

Cluster with HDBSCAN in PCA 3D space.

Per-cluster PCA plane aligned with vertical.

Fit 2D catenary via least-squares.

Lift curve back to 3D for visualization.

Minimal parameter tuning (mainly min_cluster_size).

Produces robust cluster separation and accurate fitted catenary curves across all datasets.