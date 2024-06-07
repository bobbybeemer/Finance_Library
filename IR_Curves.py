
# calculates the zero rates given par rates
def bootstrap_zeros(par_rates):
    # first par rate equals the zero rate since it is only one payment
    zero_rates = [par_rates[0]]
    # for every other zero rate
    for i in range(1, len(par_rates)):
        # get the par rate (coupon) for that tenor and create a sum that is originally 0
        coupon = par_rates[i]
        discounted_sum = 0
        # for all the zero rates before the one we are trying to calculate
        for j in range(0, i):
            # discount the coupon by the right zero rate and add it to the sum
            discounted_sum += coupon / (1+zero_rates[j])**(j+1)
        # once all the discounted coupons (other than final payment) have been added, calculate the final payment = 1+coupon
        final_payment = 1 + coupon
        # rearrange the following formula:
        # 1 = C/(1+ZR1)^1 + C/(1+ZR2)^2 + C/(1+ZR3)^3 + ... + (1+C)/(1+ZRn)^n to solve for ZRn
        zero_rates.append((final_payment / (1-discounted_sum))**(1/(i+1)) - 1)
    return zero_rates


# calculates implied forward rates from zero rates - output includes the current 1-year zero rate
def forward_rates(zero_rates):
    # rate for the first year is just the one-year spot rate
    forward_rates = [zero_rates[0]]

    # loop through the rest of the rates to calculate implied one-year rates
    for i in range(1, len(zero_rates)):
        forward_rates.append(((1+zero_rates[i])**(i+1) / (1+zero_rates[i-1])**i) -1)
    return forward_rates


# calculate par rates from the zero rates
def par_rates(zero_rates):
    # first par rate equals the zero rate since it is only one payment
    pars = [zero_rates[0]]
    
    # keep a sum of all the discount factors
    # starting value is just the first discount factor
    sum_discount_factors = 1 / (1+zero_rates[0])**1
    
    # for all the other zero rates, calculate the discount factor, add it to sum, and calculate par rate for that tenor (calculation needs the sum of the discount factors and the last discount factor)
    for i in range(1, len(zero_rates)):
        last_discount_factor = 1 / (1+zero_rates[i])**(i+1)
        sum_discount_factors += last_discount_factor
        # rearrange 1 = C/(1+ZR1)^1 + C/(1+ZR2)^2 + C/(1+ZR3)^3 + ... + (1+C)/(1+ZRn)^n to solve for C
        pars.append((1 - last_discount_factor) / sum_discount_factors)
    return pars
