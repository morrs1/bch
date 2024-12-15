

BinStr = str


def encode(to_encode: BinStr, polynom: BinStr) -> BinStr:
    source = to_encode
    to_encode = to_encode + "0" * (len(polynom) - 1)
    check_bits = calc_syndrome(to_encode, polynom)
    return source + check_bits



def calc_syndrome(value: BinStr, polynom: BinStr) -> BinStr:
    value = list(map(int, value))
    polynom = list(map(int, polynom))
    for i in range(len(value) - len(polynom) + 1):
        if value[i] == 1:
            for j in range(len(polynom)):
                value[i + j] = (value[i + j] + polynom[j]) % 2

    return "".join(map(str, value[-len(polynom) + 1:]))

