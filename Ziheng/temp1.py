import numpy as np
import matplotlib.pyplot as plt
# Given data points
data_points = [3991.5, 3991.5, 3991.5, 3992.5, 3992.5, 3992.5, 3993.5, 3993.5, 3992.5, 3992.5, 3991.5, 3991.5, 3992.5, 3992.5, 3992.5]

# Independent variable (x values)
x = np.array(range(1, len(data_points) + 1))

# Dependent variable (y values)
y = np.array(data_points)

# Perform linear regression
m, b = np.polyfit(x, y, 1)

print("Slope (m):", m)
print("Y-intercept (b):", b)

def lin_alg(x):
    return m*x +b

yy = lin_alg(x)
plt.plot(x, yy)
plt.ylim(3983, 3994)
plt.show()
