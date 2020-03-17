# author: hzy
while True:
    N = int(input())
    if N == 0:
        break

    t1 = []
    t2 = []
    t1_score = 0
    t2_score = 0
    rounds = int(N / 2) + 1 if N & 1 else int(N / 2)
    for i in range(1, N + 1):
        s = input()
        sp = s.split(' ')
        ans = 0 if sp[len(sp) - 2] == 'no' else 1
        if s == 'no good':
            ans = 1
        if i % 2:
            # t1
            t1.append('O' if ans else 'X')
            t1_score += ans
        else:
            # t2
            t2.append('O' if ans else 'X')
            t2_score += ans

    print(' '.join(str(x) for x in list(range(1, rounds + 1))), 'Score')
    print(' '.join(t1), t1_score)
    if N & 1:
        print(' '.join(t2), '-', t2_score)
    else:
        print(' '.join(t2), t2_score)
