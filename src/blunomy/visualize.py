import matplotlib.pyplot as plt
import numpy as np

def plot_points(df):
    """Quick 3D scatter of LiDAR points from a DataFrame with x,y,z."""
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(df['x'], df['y'], df['z'], s=2, alpha=0.6)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("3D Scatter Plot of LiDAR Points")
    plt.show()

def plot_clusters(df, labels):
    """3D scatter plot colored by cluster labels (-1 = noise)."""
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    # convert labels to a color per cluster id
    unique_labels = sorted(set(labels))
    for label in unique_labels:
        mask = labels == label
        if label == -1:
            ax.scatter(df.loc[mask, 'x'], df.loc[mask, 'y'], df.loc[mask, 'z'],
                       s=2, alpha=0.25, label="noise")
        else:
            ax.scatter(df.loc[mask, 'x'], df.loc[mask, 'y'], df.loc[mask, 'z'],
                       s=3, alpha=0.85, label=f"cluster {label}")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("3D Scatter Plot of Clusters")
    ax.legend(loc="upper left", frameon=False)
    plt.show()

def plot_wire_fit_2d(points2d, curve2d, title="Wire fit in plane (x,y)"):
    """
    Scatter the wire’s 2D points (x,y) and overlay the fitted catenary curve.
    """
    x, y = points2d[:, 0], points2d[:, 1]
    cx, cy = curve2d[:, 0], curve2d[:, 1]

    plt.figure(figsize=(6, 4))
    plt.scatter(x, y, s=6, alpha=0.6, label="points")
    plt.plot(cx, cy, linewidth=2, label="fitted catenary")
    plt.xlabel("x (along in plane)")
    plt.ylabel("y (elevation in plane)")
    plt.title(title)
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.show()

def plot_clusters_with_curves(df, labels, curves3d):
    """
    3D scatter of all LiDAR points coloured by cluster, with fitted 3D curves overlaid.
    """
    # set up 3D axes
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    # --- scatter points by cluster ---
    unique_labels = sorted(set(labels))
    for lab in unique_labels:
        mask = (labels == lab)
        xs = df.loc[mask, 'x'].to_numpy()
        ys = df.loc[mask, 'y'].to_numpy()
        zs = df.loc[mask, 'z'].to_numpy()

        if lab == -1:
            ax.scatter(xs, ys, zs, s=2, alpha=0.15, label="noise")
        else:
            ax.scatter(xs, ys, zs, s=3, alpha=0.6, label=f"cluster {lab}")

    # --- overlay fitted curves ---
    for item in curves3d:
        cid = item["cluster"]
        C = item["curve3d"]  # (M,3)
        ax.plot(C[:, 0], C[:, 1], C[:, 2], linewidth=2.0, label=f"fit {cid}")

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Clusters + fitted catenaries")
    # deduplicate legend entries (cluster + fit may share labels)
    handles, labels_txt = ax.get_legend_handles_labels()
    seen = {}
    new_h, new_l = [], []
    for h, l in zip(handles, labels_txt):
        if l not in seen:
            seen[l] = True
            new_h.append(h)
            new_l.append(l)
    ax.legend(new_h, new_l, loc="upper left", frameon=False)
    plt.tight_layout()
    plt.show()