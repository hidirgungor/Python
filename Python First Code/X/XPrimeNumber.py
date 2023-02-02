# coding=utf-8

print (60*"-")
print (22*" ","Prime Number X")
print (60*"-")

num = int(input("Type the maximum number for Prime Number series up to x : "))
prime = []

for i in range(2, num):
    for j in range(2, i):
        if i % j == 0:
            break
    else:
        prime.append(i)

print("\n", prime)
print("\n0 - {} total of {} there's a prime number.".format(num, len(prime)))
