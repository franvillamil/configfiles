#!/usr/bin/env python3

"""
Splits an input pdf file into several given a list of splitting
points (page numbers).
"""

__author__ = 'benhdj@cs.cmu.edu (Benjamin Han)'

import sys
import os
from pypdf import PdfReader, PdfWriter


def usage():
    print("""
Usage: splitPDF.py inputFN splitPageNum1 splitPageNum2 ...

  - inputFN: the path to the input pdf file.

  - splitPageNum1, ...: each one is a positive integer; the numbers
    must not exceed the number of pages of the input file, and the
    entire sequence must be strictly increasing.

Example: splitPDF.py input.pdf 3 5

This will split file input.pdf into 3 files (assuming input.pdf is 10
pages long):

  - input.part1.1_3.pdf contains page 1-3;

  - input.part2.4_5.pdf contains page 4-5;

  - input.part3.6_10.pdf contains page 6-10.
""".strip())


if len(sys.argv) < 3:
    usage()
    sys.exit(1)

inputFN = sys.argv[1]

if not os.path.isfile(inputFN):
    print(f"Error: file not found: {inputFN}")
    sys.exit(2)

try:
    reader = PdfReader(inputFN)
except Exception as e:
    print(f"Error reading PDF: {e}")
    sys.exit(3)

maxPages = len(reader.pages)
print(f"{inputFN} has {maxPages} pages")

try:
    splitPageNums = list(map(int, sys.argv[2:]))
except ValueError:
    print("Error: invalid split page number(s).")
    sys.exit(4)

for i, splitPageNum in enumerate(splitPageNums):
    if splitPageNum < 1 or splitPageNum > maxPages:
        print(f"Error: a split page number must be >= 1 and <= {maxPages}.")
        sys.exit(5)
    if i > 0 and splitPageNums[i - 1] >= splitPageNum:
        print("Error: split page numbers must be strictly increasing.")
        sys.exit(6)

# Ensure the final split reaches the end of the document
if splitPageNums[-1] < maxPages:
    splitPageNums.append(maxPages)

baseFN = os.path.splitext(os.path.basename(inputFN))[0]

startPageNum = 1

for i, splitPageNum in enumerate(splitPageNums):
    writer = PdfWriter()

    for page_index in range(startPageNum - 1, splitPageNum):
        writer.add_page(reader.pages[page_index])

    outputFN = f"{baseFN}.part{i + 1}.{startPageNum}_{splitPageNum}.pdf"

    with open(outputFN, "wb") as f:
        writer.write(f)

    print(f"Writing page {startPageNum}-{splitPageNum} to {outputFN}...")

    startPageNum = splitPageNum + 1

print(f"Done: {len(splitPageNums)} file(s) generated.")