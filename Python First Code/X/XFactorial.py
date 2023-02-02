# coding=utf-8

print (60*"-")
print (22*" ", "Factorial X")
print (60*"-")


def fact(num):
    if num <= 1:
        return 1
    else:
        return num * fact(num - 1)


if __name__ == '__main__':
    num = int(input("Enter the number you want to take the factorof: "))

    print(fact(num))
