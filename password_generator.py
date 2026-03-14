#!/usr/bin/env python3
"""
Password Generator
-------------------
Generates strong random passwords using letters,
digits, and special characters.

Uses only built-in Python modules:
    - random  : for secure random selection
    - string  : for character sets
    - pyperclip (optional) : to copy password to clipboard

Run it:
    python password_generator.py
"""

import random
import string
import os
import json
from datetime import datetime


# ─── Character Sets (from the string module) ──────────────────────────────────

UPPERCASE   = string.ascii_uppercase   # A-Z
LOWERCASE   = string.ascii_lowercase   # a-z
DIGITS      = string.digits            # 0-9
SPECIAL     = string.punctuation       # !@#$%^&*()_+ etc.


# ─── Storage File ─────────────────────────────────────────────────────────────

# Saved passwords are stored here
STORAGE_FILE = "saved_passwords.json"


def load_saved() -> list:
    """Load previously saved passwords from file."""
    if not os.path.exists(STORAGE_FILE):
        return []
    with open(STORAGE_FILE, "r") as f:
        return json.load(f)


def save_to_file(entry: dict):
    """Append a new password entry to the storage file."""
    saved = load_saved()
    saved.append(entry)
    with open(STORAGE_FILE, "w") as f:
        json.dump(saved, f, indent=4)
    print(f"\n  💾  Password saved to {STORAGE_FILE}\n")


# ─── Password Generator ───────────────────────────────────────────────────────

def generate_password(
    length: int      = 16,
    use_upper: bool  = True,
    use_lower: bool  = True,
    use_digits: bool = True,
    use_special: bool= True,
) -> str:
    """
    Generate a strong random password.

    Parameters:
        length      — total number of characters in the password
        use_upper   — include uppercase letters (A-Z)
        use_lower   — include lowercase letters (a-z)
        use_digits  — include digits (0-9)
        use_special — include special characters (!@#$ etc.)

    Returns:
        A randomly generated password string.
    """

    # Build the pool of characters based on user preferences
    pool = ""
    guaranteed = []  # At least one character from each selected set

    if use_upper:
        pool += UPPERCASE
        guaranteed.append(random.choice(UPPERCASE))  # Guarantee at least one

    if use_lower:
        pool += LOWERCASE
        guaranteed.append(random.choice(LOWERCASE))  # Guarantee at least one

    if use_digits:
        pool += DIGITS
        guaranteed.append(random.choice(DIGITS))     # Guarantee at least one

    if use_special:
        pool += SPECIAL
        guaranteed.append(random.choice(SPECIAL))    # Guarantee at least one

    # Edge case — if no character set was selected
    if not pool:
        raise ValueError("At least one character type must be selected.")

    # Fill the remaining characters randomly from the full pool
    remaining_length = length - len(guaranteed)
    remaining = random.choices(pool, k=remaining_length)

    # Combine guaranteed + remaining, then shuffle to avoid predictable patterns
    password_list = guaranteed + remaining
    random.shuffle(password_list)

    # Join list into a single string
    return "".join(password_list)


# ─── Password Strength Checker ────────────────────────────────────────────────

def check_strength(password: str) -> tuple:
    """
    Evaluate the strength of a password.

    Returns:
        (score, label) — score from 0-4, label is Weak/Fair/Good/Strong
    """
    score = 0

    # Check for each character type
    if any(c in UPPERCASE  for c in password): score += 1
    if any(c in LOWERCASE  for c in password): score += 1
    if any(c in DIGITS     for c in password): score += 1
    if any(c in SPECIAL    for c in password): score += 1

    # Bonus for length
    if len(password) >= 12: score += 1
    if len(password) >= 20: score += 1

    # Map score to label
    if score <= 2:
        return score, "Weak   ❌"
    elif score == 3:
        return score, "Fair   ⚠️"
    elif score == 4:
        return score, "Good   ✅"
    else:
        return score, "Strong 💪"


# ─── Display Helpers ──────────────────────────────────────────────────────────

def display_password(password: str):
    """Print the generated password with its strength rating."""
    score, label = check_strength(password)

    print("\n" + "=" * 50)
    print(f"  🔑  Generated Password:")
    print(f"\n      {password}\n")
    print(f"  📏  Length:   {len(password)} characters")
    print(f"  💪  Strength: {label}")
    print("=" * 50)


def display_saved():
    """Display all saved passwords from the storage file."""
    saved = load_saved()

    print("\n" + "=" * 50)
    print("  💾  SAVED PASSWORDS")
    print("=" * 50)

    if not saved:
        print("  No saved passwords yet.\n")
        return

    for i, entry in enumerate(saved, start=1):
        print(f"\n  [{i}]  Label:    {entry['label']}")
        print(f"       Password: {entry['password']}")
        print(f"       Saved:    {entry['date']}")

    print("\n" + "=" * 50 + "\n")


# ─── Input Helpers ────────────────────────────────────────────────────────────

def get_length() -> int:
    """Ask the user for a password length between 6 and 128."""
    while True:
        try:
            length = int(input("  Password length (6-128) [default: 16]: ").strip() or "16")
            if 6 <= length <= 128:
                return length
            print("  ⚠️  Please enter a number between 6 and 128.\n")
        except ValueError:
            print("  ⚠️  Invalid input. Enter a number.\n")


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    """Ask a yes/no question. Returns True for yes, False for no."""
    hint = "[Y/n]" if default else "[y/N]"
    answer = input(f"  {prompt} {hint}: ").strip().lower()
    if answer == "":
        return default
    return answer in ("y", "yes")


def get_preferences() -> dict:
    """Ask the user which character types to include."""
    print("\n  -- Character Options (press Enter to keep default: Yes) --\n")
    return {
        "use_upper":   ask_yes_no("Include uppercase letters (A-Z)?",  True),
        "use_lower":   ask_yes_no("Include lowercase letters (a-z)?",  True),
        "use_digits":  ask_yes_no("Include digits (0-9)?",             True),
        "use_special": ask_yes_no("Include special characters (!@#)?", True),
    }


# ─── Menu ─────────────────────────────────────────────────────────────────────

def show_menu():
    """Display the main menu."""
    print("\n  MENU")
    print("  1.  Generate password (default settings)")
    print("  2.  Generate password (custom settings)")
    print("  3.  Generate multiple passwords")
    print("  4.  View saved passwords")
    print("  0.  Exit")


# ─── Main Loop ────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 50)
    print("      🔐  PASSWORD GENERATOR")
    print("=" * 50)

    while True:
        show_menu()
        choice = input("\n  Choose an option (0-4): ").strip()

        # ── Exit ──
        if choice == "0":
            print("\n  👋  Goodbye! Stay secure.\n")
            break

        # ── Quick generate with defaults ──
        elif choice == "1":
            length = get_length()
            password = generate_password(length=length)
            display_password(password)

            # Ask if they want to save it
            if ask_yes_no("\n  Save this password?", default=False):
                label = input("  Enter a label (e.g. Gmail, GitHub): ").strip() or "Untitled"
                save_to_file({
                    "label":    label,
                    "password": password,
                    "date":     datetime.now().strftime("%Y-%m-%d %H:%M"),
                })

        # ── Custom generate ──
        elif choice == "2":
            length = get_length()
            prefs  = get_preferences()

            try:
                password = generate_password(length=length, **prefs)
                display_password(password)

                if ask_yes_no("\n  Save this password?", default=False):
                    label = input("  Enter a label: ").strip() or "Untitled"
                    save_to_file({
                        "label":    label,
                        "password": password,
                        "date":     datetime.now().strftime("%Y-%m-%d %H:%M"),
                    })

            except ValueError as e:
                print(f"\n  ❌  {e}\n")

        # ── Generate multiple ──
        elif choice == "3":
            length = get_length()

            while True:
                try:
                    count = int(input("  How many passwords to generate? (1-20): ").strip())
                    if 1 <= count <= 20:
                        break
                    print("  ⚠️  Enter a number between 1 and 20.\n")
                except ValueError:
                    print("  ⚠️  Invalid input.\n")

            print(f"\n  🔑  {count} Generated Passwords:\n")
            print("  " + "-" * 46)
            for i in range(1, count + 1):
                pw = generate_password(length=length)
                _, strength = check_strength(pw)
                print(f"  {i:>2}.  {pw}  ({strength})")
            print("  " + "-" * 46 + "\n")

        # ── View saved ──
        elif choice == "4":
            display_saved()

        else:
            print("\n  ⚠️  Invalid choice. Enter 0, 1, 2, 3, or 4.\n")


if __name__ == "__main__":
    main()