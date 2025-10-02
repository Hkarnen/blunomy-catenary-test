from src.blunomy import io, clustering, visualize, fitting
import numpy as np

# Select a file to demo
#path = "data/lidar_cable_points_easy.parquet"
path = "data/lidar_cable_points_medium.parquet"
#path = "data/lidar_cable_points_hard.parquet"
#path = "data/lidar_cable_points_extrahard.parquet"

if __name__ == "__main__":
    df = io.load_parquet(path)
    # 0. Quick look at raw points
    # visualize.plot_points(df)

    points3d = df[['x', 'y', 'z']].to_numpy()

    # Cluster into wires (local 3D PCA + HDBSCAN)
    labels, coords_used, meta = clustering.cluster_hdbscan_local3d(
        points3d,
        min_cluster_size=100,
        min_samples=10
    )

    # Print summary
    clusters = clustering.unique_clusters(labels)
    print(f"HDBSCAN found {len(clusters)} clusters (wires)")

    unique, counts = np.unique(labels, return_counts=True)
    counts_map = dict(sorted((int(u), int(c)) for u, c in zip(unique, counts)))
    noise = counts_map.pop(-1, 0) if -1 in counts_map else 0
    if counts_map:
        print("Cluster sizes:", ", ".join(f"{cid}:{n}" for cid, n in counts_map.items()))
    print(f"Noise points: {noise}")

    # Fit catenary per cluster
    results = []
    curves_payload = []  # for 3D overlay

    for cid in clusters:
        cluster_points3d = points3d[labels == cid]

        # plane & 2D projection (x = along/span, y = elevation in plane)
        center, axes = fitting.fit_plane_pca(cluster_points3d)
        points2d = fitting.to_2d(cluster_points3d, center, axes)

        # fit catenary in plane
        params = fitting.fit_catenary_2d(points2d)
        xmin, xmax = float(points2d[:, 0].min()), float(points2d[:, 0].max())

        # sample curve in 2D and lift back to 3D
        curve2d = fitting.sample_catenary(params, xmin, xmax, num=200)
        curve3d = fitting.to_3d(curve2d, center, axes)

        # --- 2. See 2D fit overlay
        #visualize.plot_wire_fit_2d(points2d, curve2d, title=f"{path} | cluster {cid}")

        curves_payload.append({"cluster": int(cid), "curve3d": curve3d})
        results.append({
            "cluster": int(cid),
            "params": params,             # includes c, x0, y0, rmse
            "span_x": [xmin, xmax],
        })

    # --- 1. Plain clusters without fits
    #visualize.plot_clusters(df, labels)

    # --- 3. 3D scatter + fitted curves overlay
    visualize.plot_clusters_with_curves(df, labels, curves_payload)

    # Print per-wire params
    for r in results:
        p = r["params"]
        print(f" Wire {r['cluster']:2d}: c={p['c']:.3f}, "
              f"x0={p['x0']:.3f}, y0={p['y0']:.3f}, rmse={p['rmse']:.3f}")
