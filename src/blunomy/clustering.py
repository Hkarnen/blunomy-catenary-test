import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import hdbscan

def cluster_dbscan_scaled(points3d, eps=0.7, min_samples=20):
    """DBSCAN on 3D points with StandardScaler."""
    coords = StandardScaler().fit_transform(points3d)
    model = DBSCAN(eps=eps, min_samples=min_samples)
    labels = model.fit_predict(coords)
    return labels

def project_to_local3d(points3d):
    """
    Compute a global PCA basis for the points:
      axes[0] = along   (wire direction)
      axes[1] = across  (in-plane, separates side-by-side wires)
      axes[2] = normal  (out-of-plane, separates stacked layers)
    Returns:
      coords_3d : (N,3) columns = [along, across, normal]
      center    : (3,) centroid in XYZ
      axes      : (3,3) rows are unit vectors [along_3d, across_3d, normal_3d]
    """
    center = points3d.mean(axis=0)
    X = points3d - center
    pca = PCA(n_components=3).fit(X)
    axes = pca.components_                  # (3,3)
    along  = X @ axes[0]
    across = X @ axes[1]
    normal = X @ axes[2]
    coords_3d = np.column_stack([along, across, normal])
    return coords_3d, center, axes

def cluster_hdbscan_local3d(points3d,
                            min_cluster_size=200,
                            min_samples=10):
    """
    Cluster the point cloud into wires using HDBSCAN in PCA coords.

    Returns:
      labels      : (N,) cluster labels (-1 = noise)
      coords_used : (N,3) coords used for clustering
      meta        : dict with plane/basis + scaler stats
    """
    coords_3d, center, axes = project_to_local3d(points3d)

    scaler = StandardScaler()
    coords_used = scaler.fit_transform(coords_3d)
    scaler_mean, scaler_scale = scaler.mean_, scaler.scale_

    model = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric='euclidean'
    )
    labels = model.fit_predict(coords_used)

    meta = {
        "center": center,           # (3,)
        "axes": axes,               # (3,3): rows [along, across, normal]
        "scaler_mean": scaler_mean,
        "scaler_scale": scaler_scale,
    }
    return labels, coords_used, meta

def unique_clusters(labels):
    """Sorted cluster ids excluding noise (-1)."""
    return sorted(set(labels) - {-1})
