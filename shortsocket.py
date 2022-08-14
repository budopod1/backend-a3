import struct


class Array:
    def __init__(self, iterable, dtype="array"):
        self.iterable = iterable
        self.dtype = dtype

    def __str__(self):
        return str(self.iterable)

    def __repr__(self):
        return f"Array({str(self)}, dtype={self.dtype})"

    def __iter__(self):
        return (value for value in self.iterable)


dtypes = [
    "array",
    "bool8",
    "int8",
    "int32",
    "float32",
    "snip"
]


def int_to_binary(data, bits):
    binary = []
    for i in list(range(bits))[::-1]:
        value = 2 ** i
        if data - value >= 0:
            data -= value
            binary.append(True)
        else:
            binary.append(False)
    return binary[::-1]
    # return [bit == "1" for bit in (bin(data)[2:].rjust(bits, "0"))[:bits]]


def binary_to_bytes(data):
    byte_data = []
    for i in range(8):
        byte_data.append(data[i::8])
    result = b""
    for byte in zip(*byte_data):
        result += bytes([sum([
            2 ** i if bit else 0
            for i, bit in enumerate(byte)
        ])])
    return result


def bytes_to_binary(data):
    binary = []
    for byte in data:
        binary.extend(int_to_binary(int(byte), 8))
    return binary

        
def binary_to_int(data):
    total = 0
    for i, bit in enumerate(data):
        if bit:
            total += 2 ** i
    return total


def decode_int8(data):
    data = bytes_to_binary(data)
    sign = data[7]
    num = binary_to_int(data[:7])
    if not sign:
        num *= -1
    return num


def encode_int8(data):
    sign = data >= 0
    # return binary_to_bytes(
    #     int_to_binary(abs(data), 7) + [sign]
    # )
    # print("---")
    # print(data)
    # data_decoded = decode_int8(((abs(data) + int(sign) * 128).to_bytes(1, "little")))
    # if data_decoded != data:
    #     print("!", data_decoded, data)
    return (abs(data) + int(sign) * 128).to_bytes(1, "little")


def encode_bool8(data):
    return encode_int8(int(data))


def decode_bool8(data):
    return bool(decode_int8(data))


def encode_int32(data):
    # actully int31, so figure out how to improve efficentcy
    sign = data >= 0
    # value = binary_to_bytes(
    #     [True, sign] + int_to_binary(abs(data), 30)
    # )
    # print(data, decode_int32(value))
    # return binary_to_bytes(
    #     [True, sign] + int_to_binary(abs(data), 30)
    # )
    # print(data)
    return ((abs(data) << 2) + (int(sign) << 1) + 1).to_bytes(4, "little")


def decode_int32(data):
    """
    data = bytes_to_binary(data)
    sign = data[0] ^ data[1]
    num = binary_to_int(data[1:])
    if not sign:
        num *= -1
    return num
    """
    data = binary_to_int(bytes_to_binary(data))
    data = data >> 1
    return (data >> 1) * (-1 if data % 2 == 0 else 1) # (data % 2 == 0 ? -1 : 1);


# SMALLEST_EXPONENT = 10


def encode_float32(data): # IEEE-754
    if data == 0:
        return b"\xff\xff\xff\xff"
    return struct.pack("f", data)[::-1]
    """
    sign = [data >= 0]
    data = abs(data)
    if round(data, 6) == 0:
        exponent = [False] * 8
        mantissa = [False] * 23
    elif data == float("inf"):
        pass
    else:
        rexponent = floor(log(data) / log(2))
        rmantissa = (data / 2**rexponent) - 1
        exponent = int_to_binary(rexponent + SMALLEST_EXPONENT, 8)
        mantissa = int_to_binary(
            round(rmantissa * 2**23),
            23
        )
    return binary_to_bytes(sign + exponent + mantissa)
    """


def decode_float32(data):
    if data == b"\xff\xff\xff\xff":
        return 0
    return struct.unpack("f", data[::-1])[0]
    """
    data = bytes_to_binary(data)
    sign = data[0]
    exponent = binary_to_int(data[1:8]) - SMALLEST_EXPONENT
    mantissa = binary_to_int(data[9:32])
    if exponent == -SMALLEST_EXPONENT and mantissa == 0:
        return 0
    num = 2 ** exponent * (1 + (mantissa / 2**23))
    if not sign:
        num *= -1
    return num
    """


def encode_snip(data):
    return data


def decode_snip(data):
    return data


def encode_array(data):
    result = encode_int8(dtypes.index(data.dtype))
    for element in data:
        value = {
            "array": encode_array,
            "int8": encode_int8,
            "bool8": encode_bool8,
            "int32": encode_int32,
            "float32": encode_float32,
            "snip": encode_snip
        }[data.dtype](element)
        assert value[0] != 0, f"{value=} {element=} {data.dtype=}"
        result += value
    result += b"\x00"
    return result


def encode(data):
    if not isinstance(data, Array):
        raise TypeError("Value to encode must be an Array")
    return encode_array(data)


def _add_at_level(data, level, item):
    for i in range(level):
        data = data[-1]
    data.append(item)

    
def _get_step(dtype):
    return {
        "int8": 1,
        "bool8": 1,
        "snip": 1,
        "int32": 4,
        "float32": 4,
        "array": 1
    }[dtype]
    
    
def _get_dtype(byte):
    if decode_int8(byte)< 0:
        pass
    return dtypes[decode_int8(byte)]
    
    
def at(data, index):
    return bytes([data[index]])
    

def decode(data):
    i = 0
    dtype = "array"
    step = _get_step(dtype)
    decoded = []
    level = 0
    while True:
        is_array = False
        
        if i >= len(data) - 1:
            break
        if at(data, i) == b"\x00":
            level -= 1
            dtype = "array"
            step = _get_step(dtype)
        elif dtype == "int8":
            _add_at_level(decoded, level, decode_int8(at(data, i)))
        elif dtype == "bool8":
            _add_at_level(decoded, level, decode_bool8(at(data, i)))
        elif dtype == "snip":
            _add_at_level(decoded, level, at(data, i))
        elif dtype == "int32":
            _add_at_level(decoded, level, decode_int32(data[i:i+step]))
        elif dtype == "float32":
            _add_at_level(decoded, level, decode_float32(data[i:i+step]))
        elif dtype == "array":
            _add_at_level(decoded, level, [])
            level += 1
            dtype = _get_dtype(at(data, i))
            step = _get_step(dtype)
            i += 1
            is_array = True
        if not is_array:
            i += step
    return decoded
