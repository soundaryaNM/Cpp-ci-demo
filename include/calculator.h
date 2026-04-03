#pragma once

namespace Calculator {

    // Basic arithmetic
    double add(double a, double b);
    double subtract(double a, double b);
    double multiply(double a, double b);
    double divide(double a, double b);   // throws std::invalid_argument on divide by zero

    // Advanced operations
    double power(double base, int exp);
    double factorial(int n);             // throws std::invalid_argument on negative input
    bool   isPrime(int n);

} // namespace Calculator
