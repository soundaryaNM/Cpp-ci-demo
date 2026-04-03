#include "calculator.h"
#include <stdexcept>
#include <cmath>

namespace Calculator {

double add(double a, double b) { return a + b; }
double subtract(double a, double b) { return a - b; }
double multiply(double a, double b) { return a * b; }

double divide(double a, double b) {
    if (b == 0.0)
        throw std::invalid_argument("Division by zero is undefined.");
    return a / b;
}

double power(double base, int exp) { return std::pow(base, exp); }

double factorial(int n) {
    if (n < 0)
        throw std::invalid_argument("Factorial is not defined for negative numbers.");
    if (n == 0 || n == 1) return 1.0;
    double result = 1.0;
    for (int i = 2; i <= n; ++i) result *= i;
    return result;
}

bool isPrime(int n) {
    if (n < 2) return false;
    if (n == 2) return true;
    if (n % 2 == 0) return false;
    for (int i = 3; i * i <= n; i += 2)
        if (n % i == 0) return false;
    return true;
}

} // namespace Calculator
