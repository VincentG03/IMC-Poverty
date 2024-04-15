import itertools
import numpy as np

def generate_combinations(multiplier_array, num_cells):
    indices = [(i, j) for i in range(len(multiplier_array)) for j in range(len(multiplier_array[0]))]
    cell_combinations = list(itertools.combinations(indices, num_cells))
    return cell_combinations

def generate_all_combinations(multiplier_array, max_length):
    all_combinations = []
    for length in range(1, max_length + 1):
        combinations = generate_combinations(multiplier_array, length)
        all_combinations.extend(combinations)
    return all_combinations



def calculate_profit(scenario, multiplier_array, user_array, hunter_array):
    if user_array == [
        [2, 7, 4, 2, 4],
        [5.5, 6, 7, 6, 2],
        [8, 8, 2.5, 2, 0.5],
        [4, 7, 7, 5.5, 4],
        [0.5, 1, 3, 0.5, 1]
    ]:
        print("yes")
    
    total_profit = 0
    profit = 0 
    island_value = 7500
    for island in scenario:
        row, col = island
        multiplier = multiplier_array[row][col]
        user_value = user_array[row][col]
        hunter_value = hunter_array[row][col]
        total_value = user_value + hunter_value

        profit =  island_value * (multiplier / total_value)
        total_profit += profit
    return total_profit

def expedition_cost(scenario):
    if len(scenario) == 1:
        cost = 0
    elif len(scenario) == 2:
        cost = 25000
    else: 
        cost = 25000+75000
    
    return cost 

# Change this to IMC array.
multiplier_array = [
    [24, 70, 41, 21, 60 ],
    [47, 82, 87, 80, 35],
    [73, 89, 100, 90, 17],
    [77, 83, 85, 79, 55],
    [12, 27, 52, 15, 30]
]

hunter_array = [
    [2, 4, 3, 2, 4 ],
    [3, 5, 5, 5, 3],
    [4, 5, 8, 7, 2],
    [5, 5, 5, 5, 4],
    [2, 3, 4, 2, 3]
]

# New user arrays
user_arrays = [
    ("all_4%", [
        [4, 4, 4, 4, 4],
        [4, 4, 4, 4, 4],
        [4, 4, 4, 4, 4],
        [4, 4, 4, 4, 4],
        [4, 4, 4, 4, 4]
    ]),
    ("jono_skew", [
        [2, 7, 4, 2, 4],
        [5.5, 6, 7, 6, 2],
        [8, 8, 2.5, 2, 0.5],
        [4, 7, 7, 5.5, 4],
        [0.5, 1, 3, 0.5, 1]
    ]), 
    ("jono_high_skew", [
        [2, 7,4, 2, 4],
        [5.5, 6, 7, 6, 2],
        [8, 8, 2.5, 2, 0.5],
        [4, 7, 7, 5.5, 4],
        [0.5, 1, 3, 0.5, 1]
    ])
]

# Example usage
max_length = 3
all_combinations = generate_all_combinations(multiplier_array, max_length)

results = []
for user_array_name, user_array in user_arrays:
    for scenario in all_combinations:
        total_rev = calculate_profit(scenario, multiplier_array, user_array, hunter_array)
        total_cost = expedition_cost(scenario)
        total_profit = total_rev - total_cost
        results.append((user_array_name, scenario, total_profit))
        x = 10 #just for debugger

# Sort the results from best to worst
sorted_results = sorted(results, key=lambda x: x[2], reverse = False)


# Continuously ask for user input
while True:
    # Ask for user input
    user_input = input("Enter array name or 'ALL' to show all scenarios (type 'stop' to quit): ")

    # Check if user wants to exit
    if user_input.lower() == 'stop':
        print("Fuck you...")
        break

    # Filter and print results based on user input
    if user_input.lower() == "all":
        for user_array_name, scenario, total_profit in sorted_results:
            print("User Array: {:<15} Scenario: {:<25} Total Profit: {:<10}".format(user_array_name, str(scenario), str(round(total_profit,2))))
    else:
        for user_array_name, scenario, total_profit in sorted_results:
            if user_input.lower() == user_array_name.lower():
                print("User Array: {:<15} Scenario: {:<25} Total Profit: {:<10}".format(user_array_name, str(scenario), str(round(total_profit,2))))
                
                