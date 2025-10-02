import numpy as np
from scipy.optimize import least_squares

GRAVITY_Z = np.array([0, 0, 1])

def fit_plane_pca(points3d):
    """
    PCA plane for a wire cluster.
    """

    center = points3d.mean(axis=0)
    X = points3d - center
    # SVD (equivalent to PCA directions)
    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    a = Vt[0] / np.linalg.norm(Vt[0])   # First principal component
    b = Vt[1] / np.linalg.norm(Vt[1])   # Second principal component

    # Choose in-plane axis most aligned with +Z as y; the other as x
    if abs(np.dot(a, GRAVITY_Z)) >= abs(np.dot(b, GRAVITY_Z)):
        y_axis, x_axis = a, b
    else:
        y_axis, x_axis = b, a

    # Ensure y points "up"
    if np.dot(y_axis, GRAVITY_Z) < 0:
        y_axis = -y_axis

    axes = np.vstack([x_axis, y_axis])
    return center, axes

def to_2d(points3d, center, axes):
    """
    Project 3D points to 2D in-plane coords [along, across].
    """
    X = points3d - center
    along  = X @ axes[0]
    across = X @ axes[1]
    points2d = np.column_stack([along, across])
    return points2d

def to_3d(points2d, center, axes):
    """
    Reconstruct 3D points from 2D in-plane coords [along, across].
    """
    points3d = center + points2d @ axes
    return points3d

def _catenary(x, param):
    """
    y(x) = y0 + c * cosh((x - x0)/c)
    param = [c, x0, y0] with c > 0 (curvature), trough at (x0, y0)
    """

    c, x0, y0 = param
    return y0 + c * np.cosh((x - x0) / c)

def _residuals(param, x, y):
    """
    Residuals for least_squares fitting of catenary curve.
    """

    c = param[0]
    return _catenary(x, param) - y

def fit_catenary_2d(points2d):
    """
    Fit catenary curve y(x) to 2D points [along, across] in the plane.
    """

    x = points2d[:, 0]
    y = points2d[:, 1]  

    # Initial guesses
    i_min = np.argmin(y)
    xo_init = x[i_min]
    yo_init = y[i_min]
    span_x = x.max() - x.min()
    c_init = max(span_x / np.pi, 1e-3)  # avoid zero

    p0 = [c_init, xo_init, yo_init]
    result = least_squares(_residuals, p0, args=(x, y))
    c, x0, y0 = result.x
    rmse = np.sqrt(np.mean(result.fun ** 2))

    return {"c": c, "x0": x0, "y0": y0, "rmse": rmse}

def sample_catenary(params, xmin, xmax, num=200):
    """
    Sample (x, y) points along the fitted catenary curve.
    """

    c = params["c"]
    x0 = params["x0"]
    y0 = params["y0"]

    x_samples = np.linspace(xmin, xmax, num)
    y_samples = _catenary(x_samples, [c, x0, y0])
    points2d = np.column_stack([x_samples, y_samples])
    return points2d



    