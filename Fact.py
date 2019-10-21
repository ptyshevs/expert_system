class Fact:
    state_map = {False: -1, None: 0, True: 1}

    def __init__(self, name, value=None):
        self.name = name
        self.atomic = True
        # Value can be -1, 0, 1 representing False, None, True
        # if type(value) is bool or value is None:
            # self.value = self.state_map[value]
        # else:
            # if value not in [-1, 0, 1]:
                # raise ValueError(f"Fact can only have three values [-1, 0, 1], not {value}")
        self.value = value
    
    def __and__(self, o):
        if type(o) is Fact:
            return Fact(f'{self.name} & {o.name}', min(self.value, o.value))
        else:
            raise NotImplementedError(f"{self} + {o} is not implemented")
    
    def __or__(self, o):
        if type(o) is Fact:
            return Fact(f'{self.name} | {o.name}', max(self.value, o.value))
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
        return Fact(f'!{self.name}', not self.value)
    
    def __repr__(self):
        r = self.value
        at = 'T' if self.atomic else 'F'
        return f'{self.name}: {r} [{at}]'

if __name__ == '__main__':
    a = Fact('A', True)
    b = Fact('B', None)
    print(a & b)