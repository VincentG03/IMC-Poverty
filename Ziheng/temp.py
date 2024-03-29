# class yourmum:
    
#     def __init__(self) -> None:
#         pass
    
    
    
    
# mum = yourmum()
# mum.weight = 210

# print(yourmum.weight)




import numpy as np

# def lin_reg(x, y, theta):
#         alpha = 0.00001
#         iteration = 2000
#     #gradient descend algorithm
#         J_history = np.zeros([iteration, 1])
#         for iter in range(0,2000):
            
#             error = (x @ theta) -y
#             temp0 = theta[0] - ((alpha/m) * np.sum(error*x[:,0]))
#             temp1 = theta[1] - ((alpha/m) * np.sum(error*x[:,1]))
#             theta = np.array([temp0,temp1]).reshape(2,1)
#             J_history[iter] = (1 / (2*m) ) * (np.sum(((x @ theta)-y)**2))   #compute J value for each iteration 
#         return theta, J_history
    
  
# def lin_reg(x, y):
#   # number of observations/points
#   n = np.size(x)
 
#   # mean of x and y vector
#   m_x = np.mean(x)
#   m_y = np.mean(y)
 
#   # calculating cross-deviation and deviation about x
#   SS_xy = np.sum(y*x) - n*m_y*m_x
#   SS_xx = np.sum(x*x) - n*m_x*m_x
 
#   # calculating regression coefficients
#   b_1 = SS_xy / SS_xx
#   b_0 = m_y - b_1*m_x
 
#   return (b_0, b_1)
    
    
    
# x = np.array([1, 2, 3, 4, 5, 6])

# y = np.array([1, 2, 3, 4, 5, 6])

# print(lin_reg(x, y))

import matplotlib.pyplot as plt
import math



# import numpy as np
# import statsmodels.api as sm

# # Generate some example data
# np.random.seed(0)
# X = np.random.rand(100, 1)  # Independent variable
# y = 2 * X.squeeze() + np.random.normal(scale=0.5, size=100)  # Dependent variable

# # Add a constant to the independent variable matrix for the intercept term
# X = sm.add_constant(X)

# # Fit the linear regression model
# model = sm.OLS(y, X).fit()

# # Get the residuals
# residuals = model.resid

# # Calculate the standard deviation of residuals
# residuals_sd = np.std(residuals)

# print("Standard deviation of residuals:", residuals_sd)

# import numpy as np
# import statistics

# # Generate some example data
# np.random.seed(0)
# X = np.random.rand(100, 1)  # Independent variable
# y = 2 * X.squeeze() + np.random.normal(scale=0.5, size=100)  # Dependent variable

# # Calculate the coefficients manually
# X_mean = np.mean(X)
# y_mean = np.mean(y)
# n = len(X)

# # Calculate the slope (beta1) and intercept (beta0)
# beta1 = np.sum((X - X_mean) * (y - y_mean)) / np.sum((X - X_mean) ** 2)
# beta0 = y_mean - beta1 * X_mean

# # Calculate the predicted values
# y_pred = beta0 + beta1 * X

# # Calculate the residuals
# residuals = y - y_pred

# # Calculate the standard deviation of residuals
# residuals_sd = statistics.stdev(list(residuals))

# print("Standard deviation of residuals:", residuals_sd)

# x =[1,2,3,4]
# print(x[-4])


# [3991.5, 3991.5, 3991.5, 3992.5, 3992.5, 3992.5, 3993.5, 3993.5, 3992.5, 3992.5, 3991.5, 3991.5, 3992.5, 3992.5, 3992.5]


import numpy as np

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