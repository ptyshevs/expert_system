import argparse
import string

class Fact:
    def __init__(self, name):
        self.name = name
        self.value = False
    
    def __add__(self, o):
        if type(o) is Fact:
            return self.value & o.value
        else:
            raise NotImplementedError(f"{self} + {o} is not implemented")
    
    def __repr__(self):
        return f'{self.name}={self.value}'

class Operator:
    def __init__(self, op):
        self.op = op
        self.n_operands = 2 if op != '!' else 1
    
    def eval(self, l, r=None):
        if self.op == '+':
            return l + r
    
    def __repr__(self):
        return self.op

def expand_tokens(tokens):
    exp = []
    n = len(tokens)
    for i in range(n):
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
                raise ValueError(f'Invalid token: {tk}')
        elif tk in string.ascii_uppercase:
            exp.append(Fact(tk))
        else:
            raise ValueError(f'Invalid token: {tk}')
    return exp

        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--interactive', '-', default=True, action='store_true', help='interactive mode')

    args = parser.parse_args()

    env = []
    if args.interactive:
        while True:
            inp = input("> ")
            if inp == 'q' or inp == 'quit':
                break
            
            tokens = ''.join(c for c in inp.split(" ") if c)
            print("TOKENS:", tokens)

            try:
                exp = expand_tokens(tokens)
            except ValueError as e:
                print(e)
                continue
            print("EXPANDED:", exp)