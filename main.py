import codecs
import random
from cyclic import encode as cyclic_encode, calc_syndrome, BinStr
from utils import polynom_bch_table

DICT_POLYNOM_BCH = {
    "1011": (3, "x^3 + x + 1", "1011", (7, 4, 1)),
    "111010001": (8, "x^8 + x^7 + x^6  x^4 + 1", "111010001", (15, 7, 2)),
}

def encode(to_encode: BinStr, polynom: BinStr):
    return cyclic_encode(to_encode, polynom)

def decode(to_decode: str, polynom: str, t: int):
    shifts = 0

    while True:
        syndrome = calc_syndrome(to_decode, polynom)

        if syndrome.count('1') > t:
            to_decode = to_decode[1:] + to_decode[0]
            shifts += 1
            print(
                f"[Декодирование] [Сдвигов: {shifts}] Кол-во единиц в синдроме больше t ({syndrome.count('1')} > {t})"
                f" Сдвиг влево ( Синдром = {syndrome!r} Исправленная строка = {to_decode!r})"
            )
        else:
            to_decode = xor_polynomials(to_decode, syndrome)
            print(
                f"[Декодирование] [Сдвигов: {shifts}] Кол-во единиц в синдроме меньше или равно t "
                f"({syndrome.count('1')} <= {t}) "
                f"( Синдром = {syndrome!r} Исправленная строка = {to_decode!r})"
            )
            break

    print(f"[Декодирование] Побитовый сдвиг вправо на {shifts} позиций")
    for _ in range(shifts):
        to_decode = to_decode[len(to_decode) - 1] + to_decode[:len(to_decode) - 1]
        print(f"[Декодирование] [{_ + 1}/{shifts}] {to_decode!r}")

    print(f"[Декодирование] Декодирование завершено! Итоговая строка = {to_decode!r}")
    return to_decode[:-len(polynom) + 1]

def xor_polynomials(poly1: BinStr, poly2: BinStr):
    s1 = len(poly1)
    s2 = len(poly2)

    if s1 > s2:
        poly2 = ('0' * (s1 - s2)) + poly2
    elif s2 > s1:
        poly1 = ('0' * (s2 - s1)) + poly1

    result = ['0'] * s1

    for i in range(s1):
        result[i] = '1' if poly1[i] != poly2[i] else '0'

    return ''.join(result)

def encode_string_cp866(s):
    encoded_bytes = codecs.encode(s, 'cp866')
    return ''.join(format(byte, '08b') for byte in encoded_bytes)

def decode_string_cp866(b):
    bytes_list = [int(b[i:i + 8], 2) for i in range(0, len(b), 8)]
    bytes_array = bytearray(bytes_list)
    return codecs.decode(bytes_array, 'cp866')

def split_into_chunks(message_bits, chunk_size):
    # Добавляем незначащие биты в начало, если длина не делится нацело на chunk_size
    padding_length = (chunk_size - len(message_bits) % chunk_size) % chunk_size
    padded_message_bits = '0' * padding_length + message_bits
    return [padded_message_bits[i:i + chunk_size] for i in range(0, len(padded_message_bits), chunk_size)]

def simulate_binary_symmetric_channel(chunk: str, p: float):
    """
    Эмулирует симметричный двоичный канал связи, изменяя каждый бит с вероятностью p.
    """
    result = []
    for bit in chunk:
        if random.random() < p:
            result.append('1' if bit == '0' else '0')
        else:
            result.append(bit)
    return ''.join(result)

if __name__ == "__main__":
    # Ввод слова с консоли
    word = input("Введите слово: ")
    # Перевод слова в биты с использованием кодировки CP-866
    message_bits = encode_string_cp866(word)
    print(f"Изначальная строка в бинарном представлении: {message_bits}")

    # Ввод полинома с консоли
    polynom = input("Введите полином (1011 или 111010001): ")

    # Ввод вероятности ошибки
    p = float(input("Введите вероятность ошибки (0 <= p <= 1): "))

    if polynom not in DICT_POLYNOM_BCH:
        print("Неверный полином. Пожалуйста, введите 1011 или 111010001.")
    else:
        _, _, _, (_, chunk_size, t) = DICT_POLYNOM_BCH[polynom]

        # Разбиение строки на части
        chunks = split_into_chunks(message_bits, chunk_size)

        encoded_chunks = []
        for chunk in chunks:
            print(f"Не закодированный чанк: {chunk}")
            encoded_chunk = encode(chunk, polynom)
            encoded_chunks.append(encoded_chunk)
            print(f"Закодированный чанк до эмуляции канала: {encoded_chunk}")

        # Эмуляция симметричного двоичного канала связи
        noisy_chunks = [simulate_binary_symmetric_channel(chunk, p) for chunk in encoded_chunks]
        for i, noisy_chunk in enumerate(noisy_chunks):
            print(f"Закодированный чанк после эмуляции канала: {noisy_chunk}")

        # Декодирование каждого чанка
        decoded_chunks = []
        for noisy_chunk in noisy_chunks:
            decoded_chunk = decode(noisy_chunk, polynom, t)
            decoded_chunks.append(decoded_chunk)
            print(f"Декодированный чанк: {decoded_chunk} \n")

        # Склеивание чанков обратно
        decoded_message_bits = ''.join(decoded_chunks)
        print(f"Декодированное сообщение в битах: {decoded_message_bits}")

        # Удаление незначащих битов, добавленных в начало
        decoded_message_bits = decoded_message_bits.lstrip('0')


        decoded_message = decode_string_cp866(decoded_message_bits)
        print(f"Декодированное сообщение: {decoded_message}")

        print(polynom_bch_table())
