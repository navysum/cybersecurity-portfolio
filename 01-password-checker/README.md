# Password Strength Checker (CLI)

A simple cybersecurity starter project that evaluates password strength and explains what to improve.

## What it checks
- Length (weighted heavily)
- Character variety: lowercase, uppercase, digits, symbols
- Common password list match (local)
- Common patterns (e.g., `word123`)
- Sequences (e.g., `1234`, `abcd`, `qwer`)
- Repeated characters (e.g., `aaaa`, `1111`)
- Rough entropy estimate (character-set based)

## Requirements
- Python 3.10+ recommended (works on most modern Python 3 versions)

## Run it

### Option A: Prompt (recommended)
```bash
python password_checker.py
