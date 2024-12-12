# For analysing current games, see if change in odds affect it

import sys

arr_imp = []
for odd in sys.argv[1:]:
    implied = 1/float(odd)
    arr_imp.append(implied)

sum_implied = 0
for i in arr_imp:
    sum_implied += i

if sum_implied < 1:
    print(f"Go ahead! Implied sum is {sum_implied}")
else:
    print(f"Stop! Implied sum is {sum_implied}")

