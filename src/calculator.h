#pragma once

/**
 * @brief Simple Calculator class for CI/CD demo
 */
class Calculator {
public:
    double add(double a, double b);
    double subtract(double a, double b);
    double multiply(double a, double b);
    double divide(double a, double b);   // throws std::invalid_argument if b == 0
    bool   isPrime(int n);
    long   factorial(int n);             // throws std::invalid_argument if n < 0
};
