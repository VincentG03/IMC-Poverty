import json
from pprint import pprint

def clean_backtester(file_name):
# Original JSON-like string
    with open(file_name, "r") as f:
        # stuff = f.read()
        for line in f:

            original_string = str(line).split(',"orders"')
            # original_string = '''0 {"logs":"","orders":{"AMETHYSTS":[{"price":9998,"quantity":20,"symbol":"AMETHYSTS"},{"price":10004,"quantity":-20,"symbol":"AMETHYSTS"}],"STARFRUIT":[{"price":5037,"quantity":20,"symbol":"STARFRUIT"},{"price":5042,"quantity":-20,"symbol":"STARFRUIT"}]},"state":{"listings":{"AMETHYSTS":{"denomination":"1","product":"AMETHYSTS","symbol":"AMETHYSTS"},"STARFRUIT":{"denomination":"1","product":"STARFRUIT","symbol":"STARFRUIT"}},"market_trades":{"AMETHYSTS":[],"STARFRUIT":[]},"observations":{},"order_depths":{"AMETHYSTS":{"buy_orders":{"9995.0":30,"9998":1},"sell_orders":{"10005":-30}},"STARFRUIT":{"buy_orders":{"5036":30},"sell_orders":{"5043":-30}}},"own_trades":{"AMETHYSTS":[],"STARFRUIT":[]},"position":{"AMETHYSTS":0,"STARFRUIT":0},"timestamp":0,"traderData":""}}'''
            # pprint(original_string)
    # Extracting JSON part from the string
    # json_string = original_string.split(' ', 1)[1]
            with open("Ziheng/CLEAN_backtester.log", "a") as k:
                x = original_string[0]
                print(original_string[0])
                k.write(f"{original_string[0].replace('\\n', '\n')} \n")
    # # Converting JSON string to dictionary
    # data = json.loads(json_string)

    # # Removing unnecessary keys
    # keys_to_remove = ['logs', 'traderData']
    # for key in keys_to_remove:
    #     data.pop(key, None)

    # # Converting dictionary back to JSON string
    # cleaned_json_string = json.dumps(data, indent=4)
    # return original_string
    return "Done"
print(clean_backtester("logs/new_this.log"))
