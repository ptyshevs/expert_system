class Fact:
    state_map = {False: 0, None: 1, True: 2}

    def __init__(self, name, value=None):
        self.name = name
        # Value can be 0, 1, 2 representing False, None, True
        if value in [None, False, True]:
            self.value = self.state_map[value]
        else:
            if value not in [0, 1, 2]:
                raise ValueError(f"Fact can only have three values [0, 1, 2], not {value}")
            self.value = value
    
    def __and__(self, o):
        if type(o) is Fact:
            r = None
            sv = self.value
            ov = o.value
            if sv == 0:
                r = False
            elif sv == 1:
                if ov == 0:
                    r = False
                else:
                    r = None
            else:
                if ov == 0:
                    r = False
                elif ov == 1:
                    r = None
                else:
                    r = True
            return Fact(f'{self.name} & {o.name}', r)
        else:
            raise NotImplementedError(f"{self} + {o} is not implemented")
    
    def __or__(self, o):
        if type(o) is Fact:
            r = None
            sv = self.value
            ov = o.value
            if sv == 2:
                r = True
            elif sv == 1:
                if ov == 2:
                    r = True
                else:
                    r = None
            else:
                if ov == 0:
                    r = False
                elif ov == 1:
                    r = None
                else:
                    r = True
            return Fact(f'{self.name} | {o.name}', r)
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
        sv = self.value
        r = None
        if sv == 0:
            r = True
        elif sv == 1:
            r = None
        else:
            r = False
        return Fact(f'!{self.name}', r)
    
    def __repr__(self):
        r = None
        if self.value == 0:
            r = False
        elif self.value == 1:
            r = None
        else:
            r = True
        return f'{self.name}: {r}'

if __name__ == '__main__':
    a = Fact('A', True)
    b = Fact('B', None)
    print(a & b)