import ctypes
import sys
import operator

ops = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '%': operator.mod,
}

class c_int(ctypes.c_int32):
    # Reference: https://stackoverflow.com/questions/57186789/how-to-add-subtract-two-ctypes-c-double-in-python
    def __add__(self, other):
        # Reference: https://stackoverflow.com/questions/61208181/simulate-integer-overflow-in-python
        sum = self.value + other.value
        return c_int((int(sum) & (1 << 32-1)-1) - (int(sum) & (1 << 32-1)))

    def __sub__(self, other):
        return c_int(self.value - other.value)

    def __mul__(self, other):
        return c_int(self.value * other.value)

    def __truediv__(self, other):
        return c_int(self.value / other.value)

    def __mod__(self, other):
        # Reference: https://stackoverflow.com/questions/34291760/how-to-easily-implement-c-like-modulo-remainder-operation-in-python-2-7
        return c_int(abs(self.value) % abs(other.value)*(1-2*(self.value<0)))

def main():
    if sys.argv[1] is not None:
        f = open(sys.argv[1], "r")
        assign = {}
        count = 0
        for line in f:
            if not line or "return" in line:
                break
            elif "#include" in line or "main()" in line or "{" in line  or "}" in line:
                continue
            elif "int32_t" in line:
                # assign variables
                line = line[:-2]
                assign[line.split(" ")[1]] = 0
                continue
            elif "printf" in line:
                for key in assign:
                    if key in line:
                        print(int(assign[key]))
            elif "=" in line:
                line = line[:-2]
                equation = line.split(" ")
                for keys in assign:
                    if keys in line:
                        count += 1
                        if count == 1:
                            assign[equation[0]] = ops[equation[3]](c_int(int(equation[2])), c_int(int(equation[4]))).value
                        else:
                            try:
                                assign[equation[0]] = ops[equation[3]](c_int(int(assign[equation[2]])), c_int(int(equation[4]))).value
                            except KeyError:
                                assign[equation[0]] = ops[equation[3]](c_int(int(equation[2])), c_int(int(assign[equation[4]]))).value

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
