#!/usr/local/bin/python

import sys
import fileinput
import argparse
import logging


def main(input_line, **kwargs):
    print(kwargs)
    print(input_line)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args, unknown_args = parser.parse_known_args()
    return args, unknown_args


if __name__ == "__main__":
    args, unknown_args = parse_args()
    sys.argv = sys.argv[:1]
    logging.basicConfig(level=logging.INFO if not args.debug else logging.DEBUG)
    if not args.debug:
        sys.tracebacklimit = -1

    for line in fileinput.input():
        try:
            line = line.strip()
            main(input_line=line, **vars(args))
        except Exception as e:
            print(f"{type(e).__name__}: {e.args[0]}")
