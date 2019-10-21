import argparse
import string
import sys
from Fact import Fact


class Operator:
    precedence_map = {'<=>': 1, '=>': 2, '^': 3, '|': 4, '+' : 5, '!': 6, '=': 0}
    # assoc_map = {'+': 'left', '-': 'left', '*': 'left', '/': 'left', '%': 'left',
                #  '^': 'right', '=': 'right', '**': 'left', '?': 'left'}

    def __init__(self, op):
        self.op = op
        self.name = op
        self.n_operands = 2 if op != '!' else 1
        self.precedence = self.precedence_map[op]
    
    def eval(self, l, r=None, **kwargs):
        if type(l) is Fact:
            l = l.value
        if type(r) is Fact:
            r = r.value
        if self.op == '+':
            return l & r
        elif self.op == '!':
            return not l
        elif self.op == '|':
            return r | l
        elif self.op == '^':
            return r ^ l
        return r
    
    def __repr__(self):
        return self.op

def expand_tokens(tokens):
    exp = []
    n = len(tokens)
    i = 0
    while i < n:
        tk = tokens[i]
        if tk in '()':
            exp.append(tk)
        elif tk in '!+|^':
            exp.append(Operator(tk))
        elif tk == '<':
            if i < n - 2 and tokens[i+1] == '=' and tokens[i+2] == '>':
                exp.append(Operator('<=>'))
                i += 2
            else:
                raise ValueError(f"Invalid token: {tk}")
        elif tk == '=':
            if i < n - 1 and tokens[i+1] == '>':
                exp.append(Operator('=>'))
                i += 1
            else:
                exp.append(Operator('='))
        elif tk in string.ascii_uppercase:
            exp.append(Fact(tk))
        else:
            raise ValueError(f'Invalid token: {tk}')
        
        i += 1
    return exp

def infix_to_rpn(expr):
    operators = []  # Stack
    output = []  # Queue
    # print("INFIX TO RPN")
    while expr:
        tk = expr.pop(0)
        # print(f'tk={tk}, type={type(tk)}')
        if type(tk) is Fact:
            output.append(tk)
        elif type(tk) is Operator:
            while True:
                if len(operators) == 0:
                    break
                head = operators[-1]
                if head == '(':
                    break
                elif type(head) is Operator and head.precedence >= tk.precedence:
                    output.append(operators.pop())
                else:
                    break
            operators.append(tk)
        elif tk == '(':
            operators.append(tk)
        elif tk == ')':
            found_bracket = False
            while True:
                if len(operators) == 0:
                    break
                head = operators[-1]
                if head == '(':
                    found_bracket = True
                    break
                output.append(operators.pop())
            if not found_bracket:
                raise ValueError("Mismatched parentheses")
            assert operators[-1] == '('
            operators.pop()
    while operators:
        op = operators.pop()
        if op in ['(', ')']:
            raise ValueError("Mismatched parentheses")
        output.append(op)
    return output     

def evaluate_rpn(rpn, facts, rules, verbose=False):
    eval_stack = []
    while rpn:
        val = rpn.pop(0)
        if type(val) is Fact:
            res = resolve_query(rules, facts, val, verbose=verbose)
            
            if res is None:
                val.value = False
            else:
                val = res
            eval_stack.append(val)
        elif type(val) is Operator:
            n_op = val.n_operands
            if not eval_stack:
                raise ValueError(f"Not enough operands to perform calculation | Operator {val} ({type(val)})")
            op = eval_stack.pop()
            # op = resolve_query(rules, facts, op, verbose=True)
            if n_op == 1:
                r = val.eval(op)
                eval_stack.append(r)
            else:
                if not eval_stack:
                    raise ValueError(f"Not enough operands to perform calculation | Operator {val}, op1 {op}")
                else:
                    op2 = eval_stack.pop()
                    # op2 = resolve_query(rules, facts, op2, verbose=True)
                    eval_stack.append(val.eval(op, op2))
        else:
            raise NotImplementedError(val, type(val))
    if len(eval_stack) != 1:
        raise ValueError("Expression doesn't evaluate to a single value")
    # print("EVAL STACK:", eval_stack)
    res = eval_stack[0]
    if type(res) is bool:
        return res
    elif type(res) is Fact:
        return res.value
    return res

def evaluate(inp, verbose=False, return_rpn=False):
    tokens = ''.join(c for c in inp.split(" ") if c)
    if verbose:
        print("TOKENS:", tokens)

    exp = expand_tokens(tokens)

    if verbose:
        print("EXPANDED:", exp)

    rpn = infix_to_rpn(exp)
    if verbose:
        print("RPN:", rpn)
    if return_rpn:
        return rpn
    res = evaluate_rpn(rpn, env)
    if verbose:
        print("EVAL RESULT:", res)
    return res

def parse_file(f):
    lines = []
    for line in f:
        if line.endswith("\n"):
            line = line[:-1]
        if line.startswith("#"):
            continue
        elif not line:
            continue
        tokens = [c for c in line.split(" ") if c]
        if len(tokens) == 0:
            continue
        full = True
        for i in range(len(tokens)):
            if tokens[i].startswith("#"):
                full = False
                r = " ".join(tokens[:i])
                if r:
                    lines.append(r)
                break
        if full:
            lines.append(" ".join(tokens))
    return lines

def parse_rule(rule):
    tokens = ''.join(c for c in rule.split(" ") if c)
    exp = expand_tokens(tokens)
    lhs, consequence, rhs = [], None, []

    is_lhs = True
    for t in exp:
        if type(t) is Fact:
            if t.name in facts:
                t = facts[t.name]
            else:
                facts[t.name] = t
            if not is_lhs:
                t.atomic = False
        if type(t) is str and t in ['=>', '<=>']:
            consequence = t
            is_lhs = False
        elif type(t) is not str and t.name in ['=>', '<=>']:
            consequence = t
            is_lhs = False
        elif is_lhs:
            lhs.append(t)
        else:
            rhs.append(t)
    if len(lhs) == 0:
        raise ValueError(f"{rule}: Empty LHS")
    elif len(rhs) == 0:
        raise ValueError(f"{rule}: Empty RHS")
    elif consequence is None:
        raise ValueError(f"{rule}: Consequence is not understood")
    return lhs, consequence, rhs

def validate_input(lines):
    if len(lines) < 2:
        raise ValueError("Input is insufficient for proper working")
    rules, init_facts, query = lines[:-2], lines[-2], lines[-1]
    if not query.startswith("?") or not all(c in string.ascii_uppercase for c in query[1:]):
        raise ValueError("Invalid query:", query)
    else:
        query = query[1:]
    if not init_facts.startswith("=") or not all(c in string.ascii_uppercase for c in init_facts[1:]):
        raise ValueError("Invalid initial facts:", init_facts)
    else:
        init_facts = init_facts[1:]

    facts = dict()  # List of all known facts, either atomic or complex

    rules_parsed = []
    for rule in rules:
        rules_parsed.append(parse_rule(rule))
    return rules_parsed, init_facts, facts, query

def initialize_facts(init_facts, facts):
    for f in init_facts:
        if f not in facts:
            print(f"Initial fact {f} doesn't exist in graph")
            continue
        else:
            fact = facts[f]
            if not fact.atomic:
                fact.atomic = True
            fact.value = True
    for f in facts.values():
        if f.atomic and f.value is None:
            f.value = False

def solve_rhs(facts, rhs, res, query, verbose=False):
    if verbose:
        print("RHS:", rhs, "as:", res)
    if res is None:
        return res
    elif len(rhs) == 1:
        t = rhs[0]
        if type(t) is Fact:
            return res
    elif len(rhs) == 2:
        op, val = rhs
        if op.name == '!':
            return not res
        else:
            raise ValueError("Invalid RHS:", rhs)
    elif len(rhs) == 3:
        a, op, b = rhs
        second = b if f == a else b
        if op.name == '+':
            if res is True:
                return True
            else:
                if second is False:
                    return True
                else:
                    return None
    else:
        raise ValueError("Invalid RHS:", rhs)


def resolve_query(rules, facts, f, verbose=False, stack=[]):
    if f in stack:
        return None
    else:
        stack.append(f)
    result = None
    if verbose:
        print("Resolving query:", f)
    if type(f) is bool:
        return f
    if f.atomic:
        result = f.value
    else:
        # Resolving among complex
        rules_with_rhs = [r for r in rules if f in r[2]]
        if verbose:
            print("RULES WITH RHS:", rules_with_rhs)
        for r in rules_with_rhs:

            lhs, cons, rhs = r[0][:], r[1], r[2][:]
            
            if f in lhs:
                print("Recursion attempted")
                continue

            rpn = infix_to_rpn(lhs)
            if verbose:
                print("RPN:", rpn)
            evaluated_lhs = evaluate_rpn(rpn, facts, rules)
            if verbose:
                print("LHS EVAL:", evaluated_lhs, "is None:", evaluated_lhs is None)
            if evaluated_lhs is None:
                if verbose:
                    print("Continued")
                continue
            elif cons.name == '=>':
                if verbose:
                    print("Resolving implication")
                if evaluated_lhs is True:
                    result = solve_rhs(facts, rhs, True, f, verbose=verbose)
                else:
                    if verbose:
                        print("Proposition is False, moving on")
                    continue
            elif cons.name == '<=>':
                if verbose:
                    print("Resolving equivalence")
                result = solve_rhs(facts, rhs, evaluated_lhs, f, verbose=verbose)
            else:
                raise ValueError("Invalid consequence operator", cons)
    stack.pop()
    return result

def resolve_queries(rules, facts, queries, verbose=False):
    for q in queries:
        if q not in facts:
            print(f"Query is not understood: {q}")
            continue
        f = facts[q]
        res = resolve_query(rules, facts, f, verbose)
        print(f"Q[{q}]: {res}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--interactive', '-i', default=False, action='store_true', help='interactive mode')
    parser.add_argument('--file', '-f', default=None, help='File to read')
    parser.add_argument('--natural', '-n', default=True, action='store_true', help='more natural input')
    parser.add_argument('--verbose', '-v', default=False, action='store_true', help='more verbose evaluation')

    args = parser.parse_args()

    env = []
    if args.interactive:
        rules, init_facts, facts, queries = [], "", dict(), ""

        while True:
            inp = input("> ")
            if args.natural:
                inp = inp.upper()
            if inp.lower() == 'q' or inp.lower() == 'quit':
                break
            elif inp.lower() == 'facts':
                print(facts)
                continue
            elif inp.lower() == 'rules':
                print(rules)
                continue
            elif inp.lower() == 'exec':
                if args.verbose:
                    print(f"QUERIES NOW: |{queries}| | RULES: {rules}")

                initialize_facts(init_facts, facts)
                resolve_queries(rules, facts, queries, args.verbose)
            else:
                try:
                    if not inp:
                        continue
                    if inp.startswith("="):
                        init_facts = inp[1:]
                    elif inp.startswith("?"):
                        queries = inp[1:].strip()
                    else:
                        rules.append(parse_rule(inp))
                except ValueError as e:
                    print(e)
    else:
        if args.file is not None:
            try:
                f = open(args.file)
            except ValueError:
                print("No such file. Nice try")
                exit(1)
        else:
            f = sys.stdin
        try:
            proper_input = parse_file(f)
            # print("PROP INPUT:")
            rules, init_facts, facts, queries = validate_input(proper_input)
            
            initialize_facts(init_facts, facts)
            
            if args.verbose:
                print("RULES", rules)
                print("INIT FACTS:", init_facts)
                print("FACTS:", facts)
                print("QUERIES:", queries)

            resolve_queries(rules, facts, queries, args.verbose)
            
        except ValueError as e:
            print(e)
            exit(1)
