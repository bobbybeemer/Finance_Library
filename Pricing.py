import math
from scipy.stats import norm
from IR_Curves import get_forward_rates

# works for annual interest rate swap where one party pays the one year rate and the other pays fixed
def swap_rate(zero_rates, num_years):
    zero_rates = zero_rates[:num_years]
    forward_rates = get_forward_rates(zero_rates)
    # FR1/ZR1^1 + FR2/ZR2^2 + FR3/ZR3^3 + ...  =  R/ZR1^1 + R/ZR2^2 + R/ZR3^3 + ...  =  R(1/ZR1^1 + 1/ZR2^2 + 1/ZR3^3 + ...)
    left_side = 0
    for i in range(0, len(forward_rates)):
        left_side += forward_rates[i]/((1+zero_rates[i])**(i+1))
    
    # 1/ZR1^1 + 1/ZR2^2 + 1/ZR3^3 + ...
    # this is all multiplied by R on the right side of the equation where is the swap rate
    right_side = 0
    for i in range(0, len(zero_rates)):
        right_side += 1/((1+zero_rates[i])**(i+1))
    return left_side/right_side



# calculated using no-arbitrage pricing -> FV of the current prices/rates
def forward_price(spot_price, num_years, zero_rates):
    return spot_price*(1+zero_rates[num_years-1])**num_years

def forward_fx(spot_price, num_years, zero_rates_1, zero_rates_2):
    return spot_price*((1+zero_rates_1[num_years-1])**num_years / (1+zero_rates_2[num_years-1])**num_years)



# call and put prices are calculated using Black-Scholes
def call_price(spot_price, strike_price, compound_rate, time_to_maturity, stdev):
    d1 = (math.log(spot_price/strike_price) + time_to_maturity*(compound_rate + stdev**2/2)) / (stdev * math.sqrt(time_to_maturity))
    d2 = d1 - (stdev * math.sqrt(time_to_maturity))
    return norm().cdf(d1)*spot_price - norm().cdf(d2)*(strike_price/math.exp(compound_rate*time_to_maturity))


def put_price(spot_price, strike_price, compound_rate, time_to_maturity, stdev):
    d1 = (math.log(spot_price/strike_price) + time_to_maturity*(compound_rate + stdev**2/2)) / (stdev * math.sqrt(time_to_maturity))
    d2 = d1 - (stdev * math.sqrt(time_to_maturity))
    return norm().cdf(-d2)*(strike_price/math.exp(compound_rate*time_to_maturity)) - norm().cdf(-d1)*spot_price


# assumes all rates move together
def dollar_value_bp(par, coupon_rate, term, zero_rates):
    # get payments associated with the bond
    payments = [par*coupon_rate]*(term-1) + [par*coupon_rate+par]
    # create running totals of the $dur and $conv
    doll_dur = 0
    doll_conv = 0
    DELTA_BP = 0.01
    # for every payment, calculate that payments $dur and $conv and add it to the total
    for i in range(0, len(payments)):
        doll_dur += dollar_duration(payments[i], zero_rates[i], i+1)
        doll_conv += dollar_convexity(payments[i], zero_rates[i], i+1)
    
    # taylor series approximation for change in value of bond
    return (doll_dur * DELTA_BP) + (1/2 * doll_conv * DELTA_BP**2)


# helper functions
# first derivative of pricing function with respect to r
def dollar_duration(payment, rate, term):
    return (payment * -term) / (1+rate)**(term+1)

# second derivative of pricing function with respect to r
def dollar_convexity(payment, rate, term):
    return (payment * (term**2 + term)) / (1+rate)**(term+2)
