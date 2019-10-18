import argparse
import string
import sys

class Fact:
    def __init__(self, name, value=False):
        self.name = name
        self.value = value
    
    def __and__(self, o):
        if type(o) is Fact:
            return Fact(self.name, self.value & o.value)
        else:
            raise NotImplementedError(f"{self} + {o} is not implemented")
    
    def __or__(self, o):
        if type(o) is Fact:
            return Fact(self.name, self.value | o.value)
        else:
            raise NotImplementedError(f'{self} | {o} is not implemented')
    
    def __xor__(self, o):
        if type(o) is Fact:
            return Fact(self.name, self.value ^ o.value)
        else:
            raise NotImplementedError(f"{self} ^ {o} is not implemented")

    def imply(self, o):
        if type(o) is Fact:
            if self.value and not o.value:
                return Fact(self.name, False)
            else:
                return Fact(self.name, True)
        else:
            raise ValueError(f"{self} => {o} is not implemented")

    def equivalent(self, o):
        if type(o) is Fact:
            if (self.value and o.value) or (not self.value and not o.value):
                return Fact(self.name, True)
            else:
                return Fact(self.name, False)
        else:
            raise ValueError(f"{self} <=> {o} is not implemented")

    def __neg__(self):
        return Fact(self.name, not self.value)
    
    def __repr__(self):
        return f'{self.name}={self.value}'

class Operator:
    precedence_map = {'<=>': 1, '=>': 2, '^': 3, '|': 4, '+' : 5, '!': 6, '=': 0}
    # assoc_map = {'+': 'left', '-': 'left', '*': 'left', '/': 'left', '%': 'left',
                #  '^': 'right', '=': 'right', '**': 'left', '?': 'left'}

    def __init__(self, op):
        self.op = op
        self.n_operands = 2 if op != '!' else 1
        self.precedence = self.precedence_map[op]
    
    def eval(self, l, r=None, **kwargs):
        if self.op == '+':
            return l & r
        elif self.op == '!':
            return -l
        elif self.op == '|':
            return r | l
        elif self.op == '^':
            return r ^ l
        elif self.op == '=>':
            return r.imply(l)
        elif self.op == '<=>':
            return r.equivalent(l)
        
        elif self.op == '=':
            print("ASSIGN, env:", kwargs, "l=", l, 'r=', r)
            env = kwargs['env']
            found = False
            for t in env:
                if t.name == r.name:
                    r = t
                    found = True
                    break
            r.name = l.name
            r.value = l.value
            if not found:
                env.append(r)
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
                print("HERE")
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

def evaluate_rpn(rpn, env):
    eval_stack = []
    while rpn:
        val = rpn.pop(0)
        if type(val) is Fact:
            for t in env:
                if val.name == t.name:
                    val = t
                    break
        if type(val) is Fact:
            eval_stack.append(val)
        elif type(val) is Operator:
            n_op = val.n_operands
            if not eval_stack:
                raise ValueError(f"Not enough operands to perform calculation | Operator {val} ({type(val)})")
            op = eval_stack.pop()
            if n_op == 1:
                eval_stack.append(val.eval(op))
            else:
                if not eval_stack:
                    if val == '!':
                        print(f"Unary negation")
                        eval_stack.append(val.eval(op))
                    else:
                        raise ValueError(f"Not enough operands to perform calculation | Operator {val}, op1 {op}")
                else:
                    op2 = eval_stack.pop()
                    eval_stack.append(val.eval(op, op2, env=env))
        else:
            raise NotImplementedError(val, type(val))
    if len(eval_stack) != 1:
        raise ValueError("Expression doesn't evaluate to a single value")
    # print("EVAL STACK:", eval_stack)
    res = eval_stack[0]
    return res

def evaluate(inp, verbose=False):
    tokens = ''.join(c for c in inp.split(" ") if c)
    if verbose:
        print("TOKENS:", tokens)

    exp = expand_tokens(tokens)

    if verbose:
        print("EXPANDED:", exp)

    rpn = infix_to_rpn(exp)
    if verbose:
        print("RPN:", rpn)
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

def validate_file(lines):
    pass


def build_graph(rules):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--interactive', '-i', default=False, action='store_true', help='interactive mode')
    parser.add_argument('--file', '-f', default=None, help='File to read')
    parser.add_argument('--natural', '-n', default=True, action='store_true', help='more natural input')
    parser.add_argument('--verbose', '-v', default=False, action='store_true', help='more verbose evaluation')

    args = parser.parse_args()

    env = []
    if args.interactive:
        while True:
            inp = input("> ")
            if args.natural:
                inp = inp.upper()
            if inp.lower() == 'q' or inp.lower() == 'quit':
                break
            elif inp.lower() == 'env':
                print(env)
                continue
            try:
                res = evaluate(inp,args.verbose)
                print(res)
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
            print("PROP INPUT:", '\n'.join(proper_input))
            # 1. Rewrite into format that can be accepted into evaluate
            # 2. Feed this into evaluation line-by-line
        except ValueError as e:
            print(e)
            exit(1)
