
def edit(file_name):
    # new file name
    changed = "Ziheng/files/changed_file"
    # var names:
    sd_multiplier = "sd_multiplier ="
    
    scale_factor_dict = "scale_factor_dict ="

    spread_hist = "spread_hist ="
    spread_val = 2  # temp vals - put inside for loop

    data_hist = "data_hist ="
    data_val = 2 

    midprice_hist = "midprice_hist ="
    midprice_val = 2

    product_limits = "product_limits ="
    product_val = 2

    avg_hist = "avg_hist = "
    avg_val = 2

    # ur gonna have to do some math to change it along side
    for sd in range(5, 15, 1):       
        sd_checker = True
        sd_new_val = sd /10

        for scale_factor in range(6, 12, 1):
            scale_factor = scale_factor / 10    

            for product_limit in range(20, 20, 2):

                with open(file_name, "r") as f:
                    
                    # writing the file name
                    file_changed = changed + "sd" + str(sd_new_val) + "sf" +\
                          str(scale_factor) + "pl" + str(product_limit)
                    

                    file_changed = file_changed.replace(".", "_")
                    file_changed = file_changed + ".py"
                    print(file_changed)

                    for line in f:

                        # checks
                        if sd_multiplier in line:
                            sd_checker = False
                            
                            with open(file_changed, "a") as c:
                                c.write(f"            {sd_multiplier} {sd_new_val}")
                            continue

                        if scale_factor_dict in line:
                            with open(file_changed, "a") as c:
                                c.write(f"        {scale_factor_dict} {{'AMETHYSTS': {scale_factor}, 'STARFRUIT': {scale_factor}}} \n")
                            continue

                        if product_limits in line:
                            with open(file_changed, "a") as c:
                                c.write(f"        {product_limits} {{'AMETHYSTS': {product_limit}, 'STARFRUIT': {product_limit}}} \n")
                            continue

                        with open(file_changed, "a") as c:
                            c.write(line)




if __name__ == "__main__":
    edit("Ziheng/vincent_trade3.py")