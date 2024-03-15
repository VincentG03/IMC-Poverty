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
    
  
def lin_reg(x, y):
  # number of observations/points
  n = np.size(x)
 
  # mean of x and y vector
  m_x = np.mean(x)
  m_y = np.mean(y)
 
  # calculating cross-deviation and deviation about x
  SS_xy = np.sum(y*x) - n*m_y*m_x
  SS_xx = np.sum(x*x) - n*m_x*m_x
 
  # calculating regression coefficients
  b_1 = SS_xy / SS_xx
  b_0 = m_y - b_1*m_x
 
  return (b_0, b_1)
    
    
    
x = np.array([1, 2, 3, 4, 5, 6])

y = np.array([1, 2, 3, 4, 5, 6])

print(lin_reg(x, y))