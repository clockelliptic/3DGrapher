list1 = [1,2,3,4]
x = 0

for i, val in enumerate(list1):
    if val == list1[-1]:
        break

    x+=val
    y = 0

    for j in list1[i:]:
        y+=j

    print('(x, y):', (x,y))

print("\n-----------------\n")

list1 = [1,8,6,4]
x = 0

for i, val in enumerate(list1):
    if val == list1[-1]:
        break

    x+=val
    y = 0

    for j in list1[i:]:
        y+=j

    print('(x, y):', (x,y))