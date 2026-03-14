#!/usr/bin/env python3
"""
Currency Converter
-------------------
Converts between currencies using real-time exchange rates.
Powered by Frankfurter API — no API key required.

Features:
  - Convert a single amount between any two currencies
  - View all exchange rates for a base currency
  - Conversion history saved to file
  - Favourite currency pairs

Install dependency:
    pip install requests

Run it:
    python currency_converter.py
"""

import requests
import json
import os
from datetime import datetime


# ─── Storage Files ────────────────────────────────────────────────────────────

HISTORY_FILE   = "conversion_history.json"   # Stores past conversions
FAVOURITES_FILE = "favourites.json"           # Stores favourite currency pairs

# ─── API Base URL ─────────────────────────────────────────────────────────────

BASE_URL = "https://api.frankfurter.app"


# ─── Supported Currencies ─────────────────────────────────────────────────────

# A handy reference dict so users can see currency names
COMMON_CURRENCIES = {
    "USD": "US Dollar",
    "EUR": "Euro",
    "GBP": "British Pound",
    "NGN": "Nigerian Naira",
    "JPY": "Japanese Yen",
    "CAD": "Canadian Dollar",
    "AUD": "Australian Dollar",
    "CHF": "Swiss Franc",
    "CNY": "Chinese Yuan",
    "INR": "Indian Rupee",
    "MXN": "Mexican Peso",
    "BRL": "Brazilian Real",
    "ZAR": "South African Rand",
    "GHS": "Ghanaian Cedi",
    "KES": "Kenyan Shilling",
    "EGP": "Egyptian Pound",
    "AED": "UAE Dirham",
    "SAR": "Saudi Riyal",
    "SGD": "Singapore Dollar",
    "NZD": "New Zealand Dollar",
}


# ─── File Helpers ─────────────────────────────────────────────────────────────

def load_json(filepath: str) -> list:
    """Load data from a JSON file. Returns empty list if file doesn't exist."""
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        return json.load(f)


def save_json(filepath: str, data):
    """Save data to a JSON file."""
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)


# ─── API Functions ────────────────────────────────────────────────────────────

def fetch_conversion(amount: float, from_cur: str, to_cur: str) -> dict:
    """
    Fetch real-time conversion from Frankfurter API.
    Returns a dict with the converted amount and rate.
    """
    url = f"{BASE_URL}/latest"
    params = {
        "amount": amount,
        "from":   from_cur.upper(),
        "to":     to_cur.upper(),
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    # Extract the converted amount from the response
    converted = data["rates"][to_cur.upper()]
    rate = converted / amount  # Rate per 1 unit

    return {
        "amount":    amount,
        "from":      from_cur.upper(),
        "to":        to_cur.upper(),
        "converted": converted,
        "rate":      rate,
        "date":      data["date"],  # Date of the exchange rate
    }


def fetch_all_rates(base_cur: str) -> dict:
    """
    Fetch all available exchange rates for a given base currency.
    Returns a dict of currency codes to rates.
    """
    url = f"{BASE_URL}/latest"
    params = {"from": base_cur.upper()}

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    return {
        "base":  base_cur.upper(),
        "date":  data["date"],
        "rates": data["rates"],
    }


def fetch_supported_currencies() -> dict:
    """Fetch the full list of currencies supported by Frankfurter API."""
    url = f"{BASE_URL}/currencies"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


# ─── History Functions ────────────────────────────────────────────────────────

def save_to_history(result: dict):
    """Append a conversion result to the history file."""
    history = load_json(HISTORY_FILE)
    history.append({
        "from":      result["from"],
        "to":        result["to"],
        "amount":    result["amount"],
        "converted": result["converted"],
        "rate":      result["rate"],
        "date":      result["date"],
        "saved_at":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    save_json(HISTORY_FILE, history)


def view_history():
    """Display all past conversions from the history file."""
    history = load_json(HISTORY_FILE)

    print("\n" + "=" * 55)
    print("  📜  CONVERSION HISTORY")
    print("=" * 55)

    if not history:
        print("  No conversions yet.\n")
        return

    # Show most recent first
    for i, entry in enumerate(reversed(history), start=1):
        print(f"\n  [{i}]  {entry['amount']} {entry['from']}  →  "
              f"{entry['converted']:.4f} {entry['to']}")
        print(f"       Rate: 1 {entry['from']} = {entry['rate']:.6f} {entry['to']}")
        print(f"       Date: {entry['date']}  |  Saved: {entry['saved_at']}")

    print("\n" + "=" * 55)
    print(f"  Total conversions: {len(history)}")
    print("=" * 55 + "\n")


def clear_history():
    """Clear all conversion history."""
    confirm = input("  Clear all history? (y/n): ").strip().lower()
    if confirm == "y":
        save_json(HISTORY_FILE, [])
        print("\n  🗑️   History cleared.\n")
    else:
        print("\n  Cancelled.\n")


# ─── Favourites Functions ─────────────────────────────────────────────────────

def load_favourites() -> list:
    """Load saved favourite currency pairs."""
    return load_json(FAVOURITES_FILE)


def save_favourite(from_cur: str, to_cur: str):
    """Save a currency pair to favourites if not already saved."""
    favourites = load_favourites()
    pair = {"from": from_cur.upper(), "to": to_cur.upper()}

    # Check if already saved
    if pair in favourites:
        print(f"\n  ℹ️   {from_cur.upper()} → {to_cur.upper()} is already in favourites.\n")
        return

    favourites.append(pair)
    save_json(FAVOURITES_FILE, favourites)
    print(f"\n  ⭐  Saved {from_cur.upper()} → {to_cur.upper()} to favourites.\n")


def view_favourites():
    """Display all saved favourite currency pairs."""
    favourites = load_favourites()

    print("\n" + "=" * 45)
    print("  ⭐  FAVOURITE CURRENCY PAIRS")
    print("=" * 45)

    if not favourites:
        print("  No favourites yet.\n")
        return

    for i, pair in enumerate(favourites, start=1):
        print(f"  [{i}]  {pair['from']}  →  {pair['to']}")

    print("=" * 45 + "\n")
    return favourites


def remove_favourite():
    """Remove a currency pair from favourites by index."""
    favourites = view_favourites()
    if not favourites:
        return

    try:
        idx = int(input("  Enter number to remove (0 to cancel): ").strip())
        if idx == 0:
            return
        if 1 <= idx <= len(favourites):
            removed = favourites.pop(idx - 1)
            save_json(FAVOURITES_FILE, favourites)
            print(f"\n  🗑️   Removed {removed['from']} → {removed['to']} from favourites.\n")
        else:
            print("\n  ⚠️  Invalid number.\n")
    except ValueError:
        print("\n  ⚠️  Invalid input.\n")


def quick_convert_favourites(amount: float):
    """Convert an amount for all saved favourite pairs at once."""
    favourites = load_favourites()

    if not favourites:
        print("\n  ℹ️   No favourites saved yet. Add some first!\n")
        return

    print(f"\n  Converting {amount} for all favourite pairs...\n")
    print("  " + "-" * 50)

    for pair in favourites:
        try:
            result = fetch_conversion(amount, pair["from"], pair["to"])
            print(f"  {amount} {result['from']:>4}  →  "
                  f"{result['converted']:>12.4f} {result['to']}"
                  f"   (rate: {result['rate']:.6f})")
        except Exception:
            print(f"  ⚠️  Could not fetch rate for {pair['from']} → {pair['to']}")

    print("  " + "-" * 50 + "\n")


# ─── Display Helpers ──────────────────────────────────────────────────────────

def display_result(result: dict):
    """Print a conversion result in a clean format."""
    print("\n" + "=" * 50)
    print("  💱  CONVERSION RESULT")
    print("=" * 50)
    print(f"  Amount:    {result['amount']} {result['from']}")
    print(f"  Converted: {result['converted']:.4f} {result['to']}")
    print(f"  Rate:      1 {result['from']} = {result['rate']:.6f} {result['to']}")
    print(f"  Date:      {result['date']}  (live rate)")
    print("=" * 50 + "\n")


def display_all_rates(data: dict):
    """Print all exchange rates for a base currency in a table."""
    print("\n" + "=" * 50)
    print(f"  📊  EXCHANGE RATES — Base: {data['base']}  ({data['date']})")
    print("=" * 50)

    for currency, rate in sorted(data["rates"].items()):
        # Show currency name if available
        name = COMMON_CURRENCIES.get(currency, "")
        name_col = f"  {name}" if name else ""
        print(f"  1 {data['base']}  =  {rate:>12.6f}  {currency}{name_col}")

    print("=" * 50 + "\n")


def show_common_currencies():
    """Print the list of common currencies for reference."""
    print("\n  Common Currencies:")
    print("  " + "-" * 38)
    for code, name in COMMON_CURRENCIES.items():
        print(f"  {code}  —  {name}")
    print("  " + "-" * 38 + "\n")


# ─── Input Helpers ────────────────────────────────────────────────────────────

def get_amount() -> float:
    """Prompt user for a valid positive amount."""
    while True:
        try:
            amount = float(input("  Enter amount: ").strip())
            if amount <= 0:
                print("  ⚠️  Amount must be greater than zero.\n")
            else:
                return amount
        except ValueError:
            print("  ⚠️  Invalid input. Enter a number.\n")


def get_currency(prompt: str) -> str:
    """Prompt user for a 3-letter currency code."""
    while True:
        code = input(prompt).strip().upper()
        if len(code) == 3 and code.isalpha():
            return code
        print("  ⚠️  Enter a valid 3-letter currency code (e.g. USD, EUR, NGN).\n")


# ─── Menu ─────────────────────────────────────────────────────────────────────

def show_menu():
    """Display the main menu."""
    print("\n  MENU")
    print("  1.  Convert a single amount")
    print("  2.  View all rates for a currency")
    print("  3.  Quick convert (favourite pairs)")
    print("  4.  Manage favourite pairs")
    print("  5.  View conversion history")
    print("  6.  Show supported currencies")
    print("  0.  Exit")


# ─── Main Loop ────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 50)
    print("      💱  CURRENCY CONVERTER")
    print("  Powered by Frankfurter API (real-time)")
    print("=" * 50)

    while True:
        show_menu()
        choice = input("\n  Choose an option (0-6): ").strip()

        # ── Exit ──
        if choice == "0":
            print("\n  👋  Goodbye!\n")
            break

        # ── Convert a single amount ──
        elif choice == "1":
            show_common_currencies()
            from_cur = get_currency("  From currency (e.g. USD): ")
            to_cur   = get_currency("  To currency   (e.g. NGN): ")
            amount   = get_amount()

            try:
                print("\n  ⏳  Fetching live rate...")
                result = fetch_conversion(amount, from_cur, to_cur)
                display_result(result)

                # Ask to save to history
                save_hist = input("  Save to history? (y/n): ").strip().lower()
                if save_hist == "y":
                    save_to_history(result)
                    print("  ✅  Saved to history.\n")

                # Ask to save pair to favourites
                save_fav = input("  Save pair to favourites? (y/n): ").strip().lower()
                if save_fav == "y":
                    save_favourite(from_cur, to_cur)

            except requests.exceptions.ConnectionError:
                print("\n  ❌  No internet connection. Please check your network.\n")
            except requests.exceptions.HTTPError as e:
                print(f"\n  ❌  API error: {e}. Check your currency codes.\n")
            except Exception as e:
                print(f"\n  ❌  Unexpected error: {e}\n")

        # ── View all rates ──
        elif choice == "2":
            show_common_currencies()
            base = get_currency("  Enter base currency (e.g. USD): ")

            try:
                print("\n  ⏳  Fetching rates...")
                data = fetch_all_rates(base)
                display_all_rates(data)
            except requests.exceptions.HTTPError:
                print(f"\n  ❌  Currency '{base}' not supported or API error.\n")
            except requests.exceptions.ConnectionError:
                print("\n  ❌  No internet connection.\n")

        # ── Quick convert favourites ──
        elif choice == "3":
            amount = get_amount()
            try:
                quick_convert_favourites(amount)
            except requests.exceptions.ConnectionError:
                print("\n  ❌  No internet connection.\n")

        # ── Manage favourites ──
        elif choice == "4":
            print("\n  FAVOURITES")
            print("  a.  View favourites")
            print("  b.  Add a favourite pair")
            print("  c.  Remove a favourite pair")
            sub = input("\n  Choose (a/b/c): ").strip().lower()

            if sub == "a":
                view_favourites()
            elif sub == "b":
                show_common_currencies()
                from_cur = get_currency("  From currency: ")
                to_cur   = get_currency("  To currency:   ")
                save_favourite(from_cur, to_cur)
            elif sub == "c":
                remove_favourite()

        # ── View history ──
        elif choice == "5":
            view_history()
            if load_json(HISTORY_FILE):
                clear = input("  Clear history? (y/n): ").strip().lower()
                if clear == "y":
                    clear_history()

        # ── Show supported currencies ──
        elif choice == "6":
            try:
                print("\n  ⏳  Fetching supported currencies...")
                currencies = fetch_supported_currencies()
                print("\n" + "=" * 45)
                print("  🌍  SUPPORTED CURRENCIES")
                print("=" * 45)
                for code, name in sorted(currencies.items()):
                    print(f"  {code}  —  {name}")
                print("=" * 45 + "\n")
            except Exception as e:
                print(f"\n  ❌  Could not fetch currencies: {e}\n")

        else:
            print("\n  ⚠️  Invalid choice. Enter a number between 0 and 6.\n")


if __name__ == "__main__":
    main()