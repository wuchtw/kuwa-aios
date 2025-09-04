#!/usr/local/bin/python

import sys
import fileinput
import argparse
import logging


def main(**kwargs):
    print(kwargs)
    for line in fileinput.input():
        try:
            line = line.strip()
            print(line)
        except Exception as e:
            print(f"{type(e).__name__}: {e.args[0]}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    args, unknown_args = parser.parse_known_args()
    return args, unknown_args


if __name__ == "__main__":
    args, unknown_args = parse_args()
    sys.argv = sys.argv[:1]
    logging.basicConfig(level=logging.INFO if not args.debug else logging.DEBUG)
    if args.debug:
        sys.tracebacklimit = -1
    main(**vars(args))
