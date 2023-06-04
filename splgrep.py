#!/usr/bin/env python

import argparse
import splre

parser = argparse.ArgumentParser(prog="SPLgrep",
                    description="Structural (Python/Perl)-Like Regular Expression grep-like program (phew!)",
                    epilog="For SPLRE grammar look at regexspec.md, README.md and grammar.parg")
parser.add_argument("expr", help="SPLRE expression to use")
parser.add_argument("file", help="File to read from if not stdin", type=argparse.FileType("r"), nargs="?", default="-")
parser.add_argument("-v", "--verbose", action="store_true", help="Show grammar/parse tree")
args = parser.parse_args()

regex = splre.create_splre(args.expr, print_grammar=args.verbose, print_parse_tree=args.verbose)
input_str = args.file.read()
args.file.close()

results = splre.run_splre(input_str, regex)
for output in results:
    print(output, end='')
print("")