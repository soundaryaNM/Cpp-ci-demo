#include <iostream>
#include "calculator.h"

int main() {
    std::cout << "=== C++ Calculator Demo ===" << std::endl;
    std::cout << "add(3, 4)        = " << Calculator::add(3, 4)        << std::endl;
    std::cout << "subtract(10, 3)  = " << Calculator::subtract(10, 3)  << std::endl;
    std::cout << "multiply(6, 7)   = " << Calculator::multiply(6, 7)   << std::endl;
    std::cout << "divide(22, 7)    = " << Calculator::divide(22, 7)    << std::endl;
    std::cout << "power(2, 10)     = " << Calculator::power(2, 10)     << std::endl;
    std::cout << "factorial(5)     = " << Calculator::factorial(5)     << std::endl;
    std::cout << "isPrime(97)      = " << std::boolalpha << Calculator::isPrime(97) << std::endl;
    return 0;
}
