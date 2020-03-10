# author: hzy
i = input().split(' ')
L, M = int(i[0]), int(i[1])
order = list(range(L + 1))
for ii in range(M):
    i2 = input().split(' ')
    left, right = int(i2[0]), int(i2[1])
    if left > right:
        tmp = left
        left = right
        right = tmp

    # remove form order
    for iii in range(left, right+1):
        if iii in order:
            order.remove(iii)

print(len(order))
