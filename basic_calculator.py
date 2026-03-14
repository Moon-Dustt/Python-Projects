#!/usr/bin/env python3
"""
Basic Calculator
----------------
Takes user input and performs:
  addition, subtraction, multiplication, division

Run it:
    python basic_calculator.py
"""


# ─── Operations ───────────────────────────────────────────────────────────────

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    # Prevent division by zero
    if b == 0:
        return "Error: Cannot divide by zero"
    return a / b


# ─── Get a valid number from the user ─────────────────────────────────────────

def get_number(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("  Invalid input. Please enter a number.\n")


# ─── Main Program ─────────────────────────────────────────────────────────────

def main():
    print("==========================")
    print("      Basic Calculator    ")
    print("==========================")

    while True:
        # Show operation choices
        print("\nOperations:")
        print("  1. Addition       (+)")
        print("  2. Subtraction    (-)")
        print("  3. Multiplication (×)")
        print("  4. Division       (÷)")
        print("  0. Exit")

        # Get user choice
        choice = input("\nChoose an operation (0-4): ").strip()

        # Exit
        if choice == "0":
            print("\nGoodbye!\n")
            break

        # Validate choice
        if choice not in ("1", "2", "3", "4"):
            print("  Invalid choice. Please enter 1, 2, 3, or 4.")
            continue

        # Get the two numbers
        a = get_number("Enter first number:  ")
        b = get_number("Enter second number: ")

        # Perform the selected operation
        if choice == "1":
            result = add(a, b)
            symbol = "+"
        elif choice == "2":
            result = subtract(a, b)
            symbol = "-"
        elif choice == "3":
            result = multiply(a, b)
            symbol = "×"
        elif choice == "4":
            result = divide(a, b)
            symbol = "÷"

        # Display result
        print(f"\n  {a} {symbol} {b} = {result}")

        # Ask if they want to calculate again
        again = input("\nCalculate again? (y/n): ").strip().lower()
        if again != "y":
            print("\nGoodbye!\n")
            break


if __name__ == "__main__":
    main()