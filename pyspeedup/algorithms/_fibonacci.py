from pyspeedup import concurrent

@concurrent.Cache
def fibonacci(n): #Source: http://stackoverflow.com/a/14782458/786020
    """Compute the nth Fibonacci number."""
    if n<0:
        raise Exception("Reverse fibonacci sequence not implemented.")
    if n <= 3:
        return (0, 1, 1, 2)[n]
    elif n % 2 == 0:
        #Starts the branching concurrently.
        fibonacci.apply_async(n // 2 - 1)
        fibonacci.apply_async(n // 2)
        a = fibonacci(n // 2 - 1)
        b = fibonacci(n // 2)
        return ((2 * a + b) * b)
    else:
        #Starts the branching concurrently.
        fibonacci.apply_async(n // 2)
        fibonacci.apply_async(n // 2 + 1)
        a = fibonacci(n // 2)
        b = fibonacci(n // 2 + 1)
        return (a * a + b * b)