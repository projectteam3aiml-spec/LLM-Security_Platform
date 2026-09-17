import copy

a = [[1, 2], [3, 4]]

b = copy.copy(a)
c = copy.deepcopy(a)
print("Original:", a)
print("Shallow Copy:", b)
print("Deep Copy:", c)
