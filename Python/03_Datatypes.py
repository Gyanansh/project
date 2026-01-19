n = 10
m = 99

for i in range(n, m + 1):
    temp = i
    rev = 0
    while i > 0:
        r = i % 10
        rev = rev * 10 + r
        i = i // 10
    if rev == temp:
        print(temp)