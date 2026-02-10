#!/usr/bin/env python3
"""
Password Strength Checker (CLI)

Checks:
- length
- upper/lowercase
- digits
- symbols
- repeated characters
- common patterns
- common password list (local file: common_passwords.txt)

Usage:
  python password_checker.py
  python password_checker.py --password "MyPass123!"
  python password_checker.py --password "MyPass123!" --show
  python password_checker.py --common-list common_passwords.txt
"""

from __future__ import annotations

import argparse
import math
import os
import re
import sys
from dataclasses import dataclass
from typing import List, Tuple, Optional


DEFAULT_COMMON_PASSWORDS = {
    # Keep this small in-code; use common_passwords.txt for a bigger list.
    "password", "123456", "123456789", "qwerty", "letmein",
    "admin", "welcome", "iloveyou", "monkey", "football"
}

KEYBOARD_SEQS = ["qwertyuiop", "asdfghjkl", "zxcvbnm", "1234567890"]
COMMON_SUBSTITUTIONS = {
    "@": "a",
    "0": "o",
    "1": "l",
    "!": "i",
    "$": "s",
    "3": "e",
    "5": "s",
    "7": "t",
}


@dataclass
class CheckResult:
    score: int  # 0..100
    rating: str
    entropy_bits: float
    issues: List[str]
    suggestions: List[str]


def load_common_passwords(path: Optional[str]) -> set[str]:
    if not path:
        return set(DEFAULT_COMMON_PASSWORDS)

    if not os.path.exists(path):
        return set(DEFAULT_COMMON_PASSWORDS)

    out: set[str] = set(DEFAULT_COMMON_PASSWORDS)
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip()
                if p and not p.startswith("#"):
                    out.add(p.lower())
    except OSError:
        # fall back silently
        return set(DEFAULT_COMMON_PASSWORDS)
    return out


def normalize_for_common_checks(pw: str) -> str:
    s = pw.strip().lower()
    for sym, repl in COMMON_SUBSTITUTIONS.items():
        s = s.replace(sym, repl)
    return s


def has_keyboard_sequence(pw_lower: str, min_len: int = 4) -> bool:
    # Detect sequential substrings like "qwer", "asdf", "1234" and reverse
    for row in KEYBOARD_SEQS:
        for i in range(0, len(row) - min_len + 1):
            chunk = row[i:i + min_len]
            if chunk in pw_lower or chunk[::-1] in pw_lower:
                return True
    return False


def has_simple_sequence(pw: str, min_len: int = 4) -> bool:
    # Detect increasing/decreasing ASCII sequences like "abcd", "fedc", "6789"
    if len(pw) < min_len:
        return False

    def is_seq(a: str, b: str) -> int:
        return ord(b) - ord(a)

    pw2 = pw
    for i in range(len(pw2) - min_len + 1):
        window = pw2[i:i + min_len]
        diffs = [is_seq(window[j], window[j + 1]) for j in range(min_len - 1)]
        if all(d == 1 for d in diffs) or all(d == -1 for d in diffs):
            return True
    return False


def repeated_characters(pw: str) -> Tuple[bool, int]:
    # Long repeats like "aaaa" or "1111"
    m = re.search(r"(.)\1{3,}", pw)
    return (m is not None, len(m.group(0)) if m else 0)


def estimate_entropy_bits(pw: str) -> float:
    # Rough entropy estimate based on character sets used (not perfect, but useful)
    if not pw:
        return 0.0

    pools = 0
    if re.search(r"[a-z]", pw):
        pools += 26
    if re.search(r"[A-Z]", pw):
        pools += 26
    if re.search(r"[0-9]", pw):
        pools += 10
    if re.search(r"[^a-zA-Z0-9]", pw):
        # approximate common symbol set size
        pools += 33

    if pools == 0:
        return 0.0

    return len(pw) * math.log2(pools)


def rate_from_score(score: int) -> str:
    if score >= 85:
        return "Very Strong"
    if score >= 70:
        return "Strong"
    if score >= 50:
        return "Moderate"
    if score >= 30:
        return "Weak"
    return "Very Weak"


def evaluate_password(pw: str, common_passwords: set[str]) -> CheckResult:
    issues: List[str] = []
    suggestions: List[str] = []

    if not pw:
        return CheckResult(
            score=0,
            rating="Very Weak",
            entropy_bits=0.0,
            issues=["Password is empty."],
            suggestions=["Enter a password with at least 12–16 characters."]
        )

    length = len(pw)
    has_lower = bool(re.search(r"[a-z]", pw))
    has_upper = bool(re.search(r"[A-Z]", pw))
    has_digit = bool(re.search(r"[0-9]", pw))
    has_symbol = bool(re.search(r"[^a-zA-Z0-9]", pw))

    # Base scoring
    score = 0

    # Length scoring (heavier weight)
    if length >= 16:
        score += 40
    elif length >= 12:
        score += 30
    elif length >= 10:
        score += 20
    elif length >= 8:
        score += 10
    else:
        issues.append("Too short (aim for at least 12 characters).")
        suggestions.append("Use 12–16+ characters (a passphrase works well).")

    # Character variety
    variety = sum([has_lower, has_upper, has_digit, has_symbol])
    score += variety * 10
    if not has_lower:
        issues.append("No lowercase letters.")
        suggestions.append("Add lowercase letters (a–z).")
    if not has_upper:
        issues.append("No uppercase letters.")
        suggestions.append("Add uppercase letters (A–Z).")
    if not has_digit:
        issues.append("No digits.")
        suggestions.append("Add digits (0–9).")
    if not has_symbol:
        issues.append("No symbols.")
        suggestions.append("Add symbols (e.g., !@#$%).")

    # Penalties: common passwords / patterns
    normalized = normalize_for_common_checks(pw)

    if normalized in common_passwords:
        issues.append("Appears in common password lists.")
        suggestions.append("Avoid common passwords; use a unique passphrase.")
        score -= 40

    # Contains a common password as a substring (e.g., password123!)
    for common in list(common_passwords)[:5000]:  # prevent huge slowdown if list is massive
        if len(common) >= 6 and common in normalized:
            issues.append("Contains a common password word/pattern.")
            suggestions.append("Remove common words (e.g., 'password', 'admin') and use a unique phrase.")
            score -= 20
            break

    # Sequences
    lower_pw = pw.lower()
    if has_keyboard_sequence(lower_pw, min_len=4) or has_simple_sequence(lower_pw, min_len=4):
        issues.append("Contains an easy sequence (keyboard or ordered characters).")
        suggestions.append("Avoid sequences like 1234, abcd, qwer.")
        score -= 15

    # Repeats
    has_rep, rep_len = repeated_characters(pw)
    if has_rep:
        issues.append(f"Contains repeated characters (e.g., '{'*' * min(rep_len, 6)}').")
        suggestions.append("Avoid long repeats like aaaa or 1111.")
        score -= 10

    # Simple “word + digits” pattern
    if re.fullmatch(r"[A-Za-z]+[0-9]{1,4}[!@#$%]?", pw):
        issues.append("Looks like a common pattern (word + digits).")
        suggestions.append("Use a passphrase or mix words in a less predictable way.")
        score -= 10

    # Entropy adjustment
    entropy = estimate_entropy_bits(pw)
    if entropy >= 80:
        score += 10
    elif entropy < 50:
        score -= 10
        suggestions.append("Increase complexity and length to raise entropy.")

    # Clamp score
    score = max(0, min(100, score))
    rating = rate_from_score(score)

    # De-duplicate suggestions while preserving order
    seen = set()
    suggestions_unique = []
    for s in suggestions:
        if s not in seen:
            suggestions_unique.append(s)
            seen.add(s)

    return CheckResult(
        score=score,
        rating=rating,
        entropy_bits=round(entropy, 2),
        issues=issues,
        suggestions=suggestions_unique
    )


def format_report(pw: str, result: CheckResult, show_password: bool) -> str:
    pw_display = pw if show_password else "*" * len(pw)
    lines = []
    lines.append("Password Strength Report")
    lines.append("-" * 26)
    lines.append(f"Password: {pw_display}")
    lines.append(f"Score:    {result.score}/100")
    lines.append(f"Rating:   {result.rating}")
    lines.append(f"Entropy:  ~{result.entropy_bits} bits (rough estimate)")
    lines.append("")

    if result.issues:
        lines.append("Issues found:")
        for i in result.issues:
            lines.append(f" - {i}")
        lines.append("")
    else:
        lines.append("Issues found: none")
        lines.append("")

    if result.suggestions:
        lines.append("Suggestions:")
        for s in result.suggestions:
            lines.append(f" - {s}")
        lines.append("")
    return "\n".join(lines)


def prompt_password() -> str:
    try:
        import getpass
        return getpass.getpass("Enter a password to check: ")
    except Exception:
        return input("Enter a password to check: ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Password Strength Checker (CLI)")
    parser.add_argument("--password", "-p", type=str, default=None, help="Password string (avoid using this on shared machines)")
    parser.add_argument("--show", action="store_true", help="Show the password in output (default hides it)")
    parser.add_argument("--common-list", type=str, default=None, help="Path to common_passwords.txt")
    args = parser.parse_args()

    common_passwords = load_common_passwords(args.common_list)

    pw = args.password if args.password is not None else prompt_password()
    result = evaluate_password(pw, common_passwords)
    print(format_report(pw, result, show_password=args.show))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
