import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def fn(x, y):
    return np.sin(x) * np.cos(y) + 0.1 * (x**2 + y**2)

def dx(x, y):
    return np.cos(x) * np.cos(y) + 0.2 * x

def dy(x, y):
    return -np.sin(x) * np.sin(y) + 0.2 * y


def findLocalMinima(x0, y0, fn, dx, dy, max_iter=10000, lr=0.01, epsilon=1e-5):
    old_cost = np.inf
    new_cost = fn(x0, y0)
    step = 0
    path = [(x0, y0, fn(x0, y0))]

    while abs(new_cost - old_cost) > epsilon and step < max_iter:
        x0 = x0 - lr * dx(x0, y0)
        y0 = y0 - lr * dy(x0, y0)
        z0 = fn(x0, y0)
        path.append((x0, y0, z0))
        old_cost = new_cost
        new_cost = fn(x0, y0)
        step += 1

    print(f"Number of steps: {step}")
    return x0, y0, fn(x0, y0), fn(x0, y0), path

x0 = np.random.uniform(-5,5)
y0 = np.random.uniform(-5,5)

x_min, y_min, z_min, grad_norm, path = findLocalMinima(x0, y0, fn, dx, dy)

print(f"Local minimum at ({x_min:.4f}, {y_min:.4f}) with value {z_min:.4f} and gradient norm {grad_norm:.4e}")

X = np.linspace(-5, 5, 200)
Y = np.linspace(-5, 5, 200)
X, Y = np.meshgrid(X, Y)
Z = fn(X, Y)

path = np.array(path)
Xp, Yp, Zp = path[:,0], path[:,1], path[:,2]

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
ax.plot(Xp, Yp, Zp, 'r.-', label='Gradient Descent Path', linewidth=2, markersize=4)
ax.scatter(x_min, y_min, z_min, color='black', s=50, label='Local Minimum')

ax.set_title("3D Gradient Descent Path on f(x, y) = sin(x)cos(y) + 0.1(x² + y²)")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("f(x, y)")
ax.legend()

plt.show()

X, Y = np.meshgrid(np.linspace(-5, 5, 100), np.linspace(-5, 5, 100))
Z = fn(X, Y)
plt.contour(X, Y, Z, levels=50, cmap='viridis')
path = np.array(path)
plt.plot(path[:,0], path[:,1], 'r.-')  # descent path
plt.title("Gradient Descent Path")
plt.xlabel("x")
plt.ylabel("y")
plt.show()