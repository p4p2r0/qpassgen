#!/usr/bin/env python3

import argparse
import math
import secrets
import string
import sys
import time

AMBIGUOUS = set("Il1O0|`'\".,;:")


def build_charset(no_lower, no_upper, no_digits, no_symbols, exclude_ambiguous):
    charset = ""
    if not no_lower:
        charset += string.ascii_lowercase
    if not no_upper:
        charset += string.ascii_uppercase
    if not no_digits:
        charset += string.digits
    if not no_symbols:
        charset += string.punctuation
    if exclude_ambiguous:
        charset = "".join(c for c in charset if c not in AMBIGUOUS)
    if not charset:
        sys.exit("error: charset is empty, enable at least one character class")
    return charset


def required_length(target_bits, charset_size):
    bits_per_char = math.log2(charset_size)
    return math.ceil(target_bits / bits_per_char)


def generate_password(charset, length):
    return "".join(secrets.choice(charset) for _ in range(length))


def copy_to_clipboard(password, clear_after):
    try:
        import pyperclip
    except ImportError:
        sys.exit("error: --clipboard requires pyperclip (pip install pyperclip)")

    try:
        pyperclip.copy(password)
    except pyperclip.PyperclipException:
        sys.exit(
            "error: no clipboard mechanism found (Linux needs xclip or xsel installed)"
        )

    print("Copied to clipboard!")

    if clear_after:
        print(f"Clipboard will clear in {clear_after}s. Press Ctrl+C to skip.")
        try:
            time.sleep(clear_after)
        except KeyboardInterrupt:
            print()
        if pyperclip.paste() == password:
            pyperclip.copy("")
            print("Clipboard cleared.")


def main():
    parser = argparse.ArgumentParser(description="Password Generator")
    parser.add_argument(
        "-l", "--length", type=int, help="explicit length, overrides --entropy"
    )
    parser.add_argument(
        "-e",
        "--entropy",
        type=int,
        default=256,
        help="target entropy in bits (default: 256)",
    )
    parser.add_argument(
        "-n", "--count", type=int, default=1, help="number of passwords to generate"
    )
    parser.add_argument("--no-lower", action="store_true")
    parser.add_argument("--no-upper", action="store_true")
    parser.add_argument("--no-digits", action="store_true")
    parser.add_argument("--no-symbols", action="store_true")
    parser.add_argument(
        "--exclude-ambiguous", action="store_true", help="drop chars like I, l, 1, O, 0"
    )
    parser.add_argument(
        "--quiet", action="store_true", help="print only the password(s)"
    )
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="copy to clipboard instead of printing it",
    )
    parser.add_argument(
        "--clear-after",
        type=int,
        metavar="SECONDS",
        help="auto-clear clipboard after N seconds",
    )
    args = parser.parse_args()

    if args.clipboard and args.count > 1:
        sys.exit("error: --clipboard only supports a single password, use -n 1")
    if args.clear_after and not args.clipboard:
        sys.exit("error: --clear-after requires --clipboard")

    charset = build_charset(
        args.no_lower,
        args.no_upper,
        args.no_digits,
        args.no_symbols,
        args.exclude_ambiguous,
    )
    bits_per_char = math.log2(len(charset))
    length = args.length if args.length else required_length(args.entropy, len(charset))

    classical_bits = length * bits_per_char
    pq_bits = classical_bits / 2

    if not args.quiet:
        print(f"Charset size        : {len(charset)}")
        print(f"Bits per character  : {bits_per_char:.3f}")
        print(f"Password length     : {length}")
        print(f"Classical entropy   : {classical_bits:.1f} bits")
        print(
            f"Post-quantum margin : {pq_bits:.1f} bits (Grover's algorithm halves effective security)"
        )
        print()

    if args.clipboard:
        password = generate_password(charset, length)
        copy_to_clipboard(password, args.clear_after)
        return

    for _ in range(args.count):
        print(generate_password(charset, length))


if __name__ == "__main__":
    main()
