# import numpy as np
# import matplotlib.pyplot as plt
# # Given data points
# data_points = [3991.5, 3991.5, 3991.5, 3992.5, 3992.5, 3992.5, 3993.5, 3993.5, 3992.5, 3992.5, 3991.5, 3991.5, 3992.5, 3992.5, 3992.5]

# # Independent variable (x values)
# x = np.array(range(1, len(data_points) + 1))

# # Dependent variable (y values)
# y = np.array(data_points)

# # Perform linear regression
# m, b = np.polyfit(x, y, 1)

# print("Slope (m):", m)
# print("Y-intercept (b):", b)

# def lin_alg(x):
#     return m*x +b

# yy = lin_alg(x)
# plt.plot(x, yy)
# plt.ylim(3983, 3994)
# plt.show()


# s = "abcdeabsdbakjsdnfa"
# print(s.split("a"))

# import numpy as np
# x = np.array([10000, 10002, 10003, 10004, 10005, 10006])
# sd = np.std(np.array(x))

# print(sd)


# import packages
import numpy as np
import pandas as pd
import statsmodels.api as smf

# loading the csv file
# df = pd.read_csv('Ziheng/prices_round_2_day_-1.csv', delimiter=';')
# print(df.columns.to_list())

# # fitting the model
# # df.columns = ['ORCHIDS', 'TRANSPORT_FEES', 'EXPORT_TARIFF', 'IMPORT_TARIFF', 'SUNLIGHT', 'HUMIDITY']
# # x = df[['TRANSPORT_FEES', 'EXPORT_TARIFF', 'IMPORT_TARIFF', 'SUNLIGHT', 'HUMIDITY']]
# # y = df['ORCHIDS']
# # x = smf.add_constant(x)
# model = smf.ols(formula='ORCHIDS ~ TRANSPORT_FEES + EXPORT_TARIFF + IMPORT_TARIFF + SUNLIGHT + HUMIDITY', data=df).fit()
# # model = smf.OLS(y, x).fit()
# # model summary
# print(model.summary())


# x = np.array([1, 2, 3, 4 ,5])
# y = np.array([1, 2, 3, 4 ,5])

# z = smf.add_constant(x)

# model = smf.OLS(y, x).fit()

# print(model.tvalues)


lst = [1, 2, 3, 4, 5, 6]
print(lst[:-1])