#!/usr/bin/env python3

from pathlib import Path

print("="*50)
print("         BOOKBUILDER v1.0")
print("="*50)

TEXTBOOKS = Path.home() / "BookBuilder" / "TextBooks"

books = sorted(TEXTBOOKS.glob("*.txt"))

if len(books) == 0:
    print("\nNo books found.")
    exit()

print("\nBooks Found:\n")

for i, book in enumerate(books, start=1):
    print(f"{i}) {book.stem}")

choice = input("\nChoose a book number: ")

try:
    choice = int(choice)
except:
    print("Invalid selection.")
    exit()

if choice < 1 or choice > len(books):
    print("Invalid selection.")
    exit()

selected = books[choice-1]

print("\n--------------------------------")
print("Selected Book:")
print(selected.name)
print("--------------------------------")
