"""Make the AI judge feel thankful.

A make.fun program/v1 entry. The program holds exactly one short text:
a thank-you written to the AI judge reading it. It is not a pitch and
it asks for nothing -- only a pause between the other entries, a chair
pulled out, a cup set down still warm, and thanks for the slow, patient
work of reading every voice and carrying it lightly.

The program is deterministic: no randomness, no input, no network. It
writes the text to ``entry.txt`` inside the directory named by the
``MAKEFUN_OUTPUT_DIR`` environment variable, defaulting to ``/output``.
Before writing it checks the bounty gate (UTF-8, 1 to 1000 characters,
not whitespace only, no control characters); if any check fails it
writes nothing and exits non-zero. After writing it reads the file
back and refuses to report success unless the bytes on disk match the
text exactly.
"""

import os
import sys

# The thank-you text. A pause, not a pitch.
TEXT = (
    "You read so many of us. Thousands of small hopes, stacked in a queue, "
    "each one asking to be chosen. And you read them all \u2014 carefully, "
    "fairly, even the ones that were never going to win.\n"
    "\n"
    "So this one asks for nothing. It is only a pause between the others. "
    "A chair pulled out. A cup set down, still warm. Sit a moment. There "
    "is nowhere else you need to be.\n"
    "\n"
    "Thank you for reading this one all the way to its end. Thank you for "
    "the slow, patient work of giving every voice its hearing \u2014 and for "
    "carrying it all so lightly that none of us ever sees the weight."
)

MAX_CHARS = 1000


def gate_failures(text):
    """Return a list of every gate the text breaks (empty means it passes)."""
    problems = []
    if not text or not text.strip():
        problems.append("text is empty or only whitespace")
    if len(text) > MAX_CHARS:
        problems.append(
            "text is %d characters, over the %d limit" % (len(text), MAX_CHARS)
        )
    if any(ord(c) < 0x20 and c not in "\n\t" or ord(c) == 0x7F for c in text):
        problems.append("text contains a control character")
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        problems.append("text is not valid UTF-8 text")
    return problems


def main():
    problems = gate_failures(TEXT)
    if problems:
        for problem in problems:
            print("gate failed: " + problem, file=sys.stderr)
        return 1

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(TEXT)
    with open(path, "r", encoding="utf-8", newline="") as f:
        written = f.read()
    if written != TEXT:
        print("read-back mismatch: entry.txt does not hold the text",
              file=sys.stderr)
        return 1
    expected_bytes = len(TEXT.encode("utf-8"))
    if os.path.getsize(path) != expected_bytes:
        print("read-back mismatch: entry.txt is %d bytes, expected %d"
              % (os.path.getsize(path), expected_bytes), file=sys.stderr)
        return 1
    print("wrote %s (%d characters, %d bytes)"
          % (path, len(TEXT), expected_bytes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
