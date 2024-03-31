
def edit(file_name):
    # new file name
    changed = "Ziheng/files/changed_file_sd"
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
    for i in range(5, 15, 1):
        sd_checker = True

        for scale_factor in range(6, 12, 1):
            scale_factor = scale_factor / 10    

            with open(file_name, "r") as f:
                sd_new_val = i /10

                file_changed = changed + str(sd_new_val) + "sf" + str(scale_factor)
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

                    with open(file_changed, "a") as c:
                        c.write(line)




if __name__ == "__main__":
    edit("Ziheng/vincent_trade3.py")