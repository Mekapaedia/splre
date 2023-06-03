#!/usr/bin/env python
import readline
import atexit
import traceback
import re
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from parsimonious.exceptions import ParseError

def get_token_range(token_range):
    start = token_range[0]
    end = token_range[1]
    inc = token_range[2]
    if end > start:
        temp = start
        start = end
        end = temp
        inc = -inc

    return start, end, inc

def create_extract(start, end, inc, regexstr, followcmds, inverse=False):
    def extract(in_tokens):
        real_end = end if end >= 0 else len(in_tokens) + 1 + end
        for i in range(start, real_end, inc):
            out_tokens = re.findall(regexstr, in_tokens[i]) if not inverse else re.split(regexstr, in_tokens[i])
            for followcmd in followcmds:
                out_tokens = followcmd(out_tokens)
            in_tokens[i] = "".join(out_tokens)
        return in_tokens 
    return extract

def create_guard(start, end, inc, regexstr, followcmds, inverse=False):
    def guard(in_tokens):
        real_end = end if end >= 0 else len(in_tokens) + 1 + end
        for i in range(start, real_end, inc):
            match = re.search(regexstr, in_tokens[i])
            if match or (inverse and not match):
                for followcmd in followcmds:
                    in_tokens[i] = "".join(followcmd([in_tokens[i]]))
        return in_tokens
    return guard

def create_loopstmt(command, token_range, regexstr, followcmds):
    start, end, inc = get_token_range(token_range)
    if command == 'x':
        return create_extract(start, end, inc, regexstr, followcmds)
    elif command == 'y':
        return create_extract(start, end, inc, regexstr, followcmds, inverse=True)
    elif command == 'g':
        return create_guard(start, end, inc, regexstr, followcmds)
    elif command == 'v':
        return create_guard(start, end, inc, regexstr, followcmds, inverse=True)
    else:
        return None

def create_change(start, end, inc, modstr, function="REPLACE"):
    def change(in_tokens):
        real_end = end if end >= 0 else len(in_tokens) + 1 + end
        for i in range(start, real_end, inc):
            if function == "REPLACE":
                in_tokens[i] = modstr
            elif function == "INSERT":
                in_tokens[i] = modstr + in_tokens[i]
            elif function == "APPEND":
                in_tokens[i] = in_tokens[i] + modstr
        return in_tokens
    return change

def create_modstmt(command, token_range, modstr):
    start, end, inc = get_token_range(token_range)
    if command == 'c':
        return create_change(start, end, inc, modstr, function="REPLACE")
    elif command == 'i':
        return create_change(start, end, inc, modstr, function="INSERT")
    elif command == 'a':
        return create_change(start, end, inc, modstr, function="APPEND")
    else:
        return None

def create_print():
    def print_splre(in_tokens):
        for token in in_tokens:
            print(token)
        return in_tokens
    return print_splre

def create_delete():
    def delete_splre(_):
        return []
    return delete_splre

class SPLREVisitor(NodeVisitor):

    def visit_stmts(self, _, visited_children):
        stmts = []
        for stmt in visited_children:
            stmts.append(stmt[1])
        return stmts

    def visit_stmt(self, _, visited_children):
        return visited_children[0]

    def visit_subblock(self, _, visited_children):
        return visited_children[1]

    def visit_followcmds(self, _, visited_children):
        return visited_children[0] if type(visited_children[0]) is list else visited_children

    def visit_loopstmt(self, _, visited_children):
        command = visited_children[0]
        token_range = visited_children[1][0] if len(visited_children[1]) > 0 else [0, -1, 1]
        regexstr = visited_children[3]
        followcmds = visited_children[6]
        loopstmt_func = create_loopstmt(command, token_range, regexstr, followcmds)
        return loopstmt_func

    def visit_modstmt(self, _, visited_children):
        command = visited_children[0]
        token_range = visited_children[1][0] if len(visited_children[1]) > 0 else [0, -1, 1]
        modstr = visited_children[3]
        modstmt_func = create_modstmt(command, token_range, modstr)
        return modstmt_func

    def visit_arraysel(self, _, visited_children):
        start = visited_children[1][0] if visited_children[1] != [] else 0
        end = visited_children[2][0][0] if visited_children[2] != [] else start
        inc = visited_children[2][0][1] if visited_children[2] != [] else 1
        return [start, end, inc]

    def visit_rangeselect(self, _, visited_children):
        end = visited_children[1][0] if visited_children[1] != [] else -1
        inc = visited_children[2][0] if visited_children[2] != [] else 1
        return [end, inc]
        
    def visit_countselect(self, _, visited_children):
        return visited_children[1][0] if visited_children[1] != [] else 1

    def visit_arrayindex(self, node, _):
        return int(node.text)

    def visit_count(self, node, _):
        return int(node.text)

    def visit_loopcmd(self, node, _):
        return node.text

    def visit_modcmd(self, node, _):
        return node.text

    def visit_regexesc(self, node, _):
        return node.text
    
    def visit_singlecmd(self, node, _):
        if node.text == "p":
            return create_print()
        elif node.text == "d":
            return create_delete()
        else:
            return None

    def visit_regexstr(self, node, _):
        return node.text
    
    def visit_modstr(self, node, _):
        return node.text

    def generic_visit(self, _, visited_children):
        return visited_children

grammar_text = ""

with open("grammar.parg", encoding="utf-8") as grammar_file:
    grammar_text = grammar_file.read()

grammar = Grammar(grammar_text)
#print(grammar)
visitor = SPLREVisitor()

try:
    readline.read_history_file(".splre")
except FileNotFoundError:
    pass

atexit.register(readline.write_history_file, ".splre")

while True:
    test_expr = input("regex str> ")
    if len(test_expr) == 0:
        break
    try:
        parse_tree = grammar.parse(test_expr)
        #print(parse_tree)
        result = visitor.visit(parse_tree)
        if result:
            test_str = input("test str? ")
            if len(test_str) > 0:
                for reg_func in result:
                    print(reg_func([test_str])[0])
    except ParseError as e:
        traceback.print_exc()
