n = 2
mat = []
for i in range(n) :
    line = []
    for j in range(n):
        line.append((i,j))
    mat.append(line)

print(mat)

mat[(1,1)]