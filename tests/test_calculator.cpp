#include <gtest/gtest.h>
#include "calculator.h"
#include <stdexcept>

// Basic Arithmetic
TEST(AddTest, PositiveNumbers)    { EXPECT_DOUBLE_EQ(Calculator::add(2, 3), 5); }
TEST(AddTest, NegativeNumbers)    { EXPECT_DOUBLE_EQ(Calculator::add(-2, -3), -5); }
TEST(AddTest, Floats)             { EXPECT_NEAR(Calculator::add(1.1, 2.2), 3.3, 1e-9); }

TEST(SubtractTest, Basic)         { EXPECT_DOUBLE_EQ(Calculator::subtract(10, 4), 6); }
TEST(SubtractTest, NegativeResult){ EXPECT_DOUBLE_EQ(Calculator::subtract(3, 7), -4); }

TEST(MultiplyTest, Basic)         { EXPECT_DOUBLE_EQ(Calculator::multiply(3, 4), 12); }
TEST(MultiplyTest, ByZero)        { EXPECT_DOUBLE_EQ(Calculator::multiply(99, 0), 0); }

TEST(DivideTest, Basic)           { EXPECT_DOUBLE_EQ(Calculator::divide(10, 2), 5); }
TEST(DivideTest, DivideByZero)    { EXPECT_THROW(Calculator::divide(5, 0), std::invalid_argument); }

TEST(PowerTest, Positive)         { EXPECT_DOUBLE_EQ(Calculator::power(2, 10), 1024); }
TEST(PowerTest, ZeroExponent)     { EXPECT_DOUBLE_EQ(Calculator::power(5, 0), 1); }

TEST(FactorialTest, Zero)         { EXPECT_DOUBLE_EQ(Calculator::factorial(0), 1); }
TEST(FactorialTest, Five)         { EXPECT_DOUBLE_EQ(Calculator::factorial(5), 120); }
TEST(FactorialTest, Negative)     { EXPECT_THROW(Calculator::factorial(-1), std::invalid_argument); }

TEST(PrimeTest, SmallPrimes)      { EXPECT_TRUE(Calculator::isPrime(2)); EXPECT_TRUE(Calculator::isPrime(97)); }
TEST(PrimeTest, NonPrimes)        { EXPECT_FALSE(Calculator::isPrime(0)); EXPECT_FALSE(Calculator::isPrime(4)); }

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
