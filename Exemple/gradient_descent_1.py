import numpy as np
import matplotlib.pyplot as plt

# Define the function
def f(x):
    return np.sin(2 * x) * np.exp(-0.1 * x**2) + 0.05 * x**3 - 0.5 * x

# Define the derivative
def f_prim(x):
    term1 = (-4 * x * np.exp(-x**2 / 10) * np.sin(2 * x) + 3 * x**2 - 10) / 20
    term2 = 2 * np.exp(-x**2 / 10) * np.cos(2 * x)
    return term1 + term2

# Plot the function and its derivative
x = np.linspace(-5, 5, 1000)
y = f(x)
dy = f_prim(x)

plt.figure(figsize=(12, 7))
plt.plot(x, y, label=r"$f(x)$", color='teal')
plt.plot(x, dy, label=r"$f'(x)$", color='orange', linestyle='--')
plt.axhline(0, color='black', linewidth=0.5)
plt.title("Function $f(x)$ and its Derivative $f'(x)$")
plt.xlabel("x")
plt.ylabel("Value")
plt.grid(True)

def findLocalMinima(x0, y, dy, lr=1e-2, max_iter=1000, epsilon=1e-4):
    history = [(x0, y(x0))]
    step = 0
    while abs(dy(x0)) > epsilon and step < max_iter:
        old = x0
        change = lr * dy(x0)
        x0 = x0 - change
        
        if abs(change) > 0.001:
            history.append((x0, y(x0)))
        
        print(f"Step {step+1}: x0 = {x0:.4f}, f(x) = {y(x0):.4f}, dy = {dy(x0):.4f} ")
        step += 1
    print(f"\nFinal result after {step} steps: x = {x0:.4f}, f(x) = {y(x0):.4f}")
    return history

start_x = np.random.uniform(-3, 3)
path = findLocalMinima(start_x, f, f_prim, lr=0.05)

xs, ys = zip(*path)
plt.plot(xs, ys, marker='o', color='red', label='Steps')

for i, (x_i, y_i) in enumerate(path):
    plt.text(x_i, y_i + 0.05, f"{i}", fontsize=8, color='black')

plt.legend()
plt.show()

