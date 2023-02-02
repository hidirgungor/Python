
def fib(x):
    a, b = 0, 1
    while a < x:
        print(a, end=' ')
        a, b = b, a+b
    print()
x = int(input(f"Type the maximum number for Fibonacci series up to x: "))
fib (x)