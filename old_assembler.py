def argToHex(opCode: int, args) -> int:
    argCode = 0

    if opCode <= opCodes['XORI']:
        argCode += int(args[0][1:])
        argCode += int(args[1][1:]) << 4
        argCode += int(args[2][1:]) << 8 if args[2][0] == 'R' else (int(args[2]) & 0x3F) << 8
    elif opCode <= opCodes['ST']:
        argCode += int(args[0][1:])
        argCode += (int(args[1]) & 0x3FF) << 4
    elif opCode == opCodes['JUMP']:
        argCode += int(args[0]) & 0x7FFF
    else:
        argCode += int(args[0][1:])
        argCode += int(args[1][1:]) << 4
        argCode += (int(args[2]) & 0x3F) << 8

    return argCode

def intToHex(num: int, length: int) -> str:

    hexString = ''

    for i in range((length - 1) // 4 + 1):
        hexString = hexString + hex(num & 0xF)[2:].upper()
        num >>= 4

    return hexString[::-1]

opCodes = {
    'AND':  0b000_0_00_0000_0000_0000,
    'ANDI': 0b000_1_00_0000_0000_0000,
    'OR':   0b001_0_00_0000_0000_0000,
    'ORI':  0b001_1_00_0000_0000_0000,
    'ADD':  0b010_0_00_0000_0000_0000,
    'ADDI': 0b010_1_00_0000_0000_0000,
    'XOR':  0b011_0_00_0000_0000_0000,
    'XORI': 0b011_1_00_0000_0000_0000,
    'LD':   0b100_0_00_0000_0000_0000,
    'ST':   0b100_1_00_0000_0000_0000,
    'JUMP': 0b110_000000000000000,
    'BEQ':  0b111_010_000000000000,
    'BGT':  0b111_001_000000000000,
    'BLT':  0b111_100_000000000000,
    'BGE':  0b111_011_000000000000,
    'BLE':  0b111_110_000000000000
}

instructions = {
    'AND': {
        'opCode': 0b000_0_00_0000_0000_0000,
        'args': (
            ('R', )
        )
    }
}

fileContent = ''

with open('input.txt', 'r') as file:
    fileContent = file.read()

insts = fileContent.splitlines()

hexInsts = []

for inst in insts:
    opCode = inst.split(' ', maxsplit=1)
    hexInsts.append(0)
    hexInsts[-1] += opCodes[opCode[0]]

    args = opCode[1].split(',')
    hexInsts[-1] += argToHex(opCodes[opCode[0]], args)

with open('output.hex', 'w') as out:
    for hexI in hexInsts:
        out.write(f':{intToHex(hexI, 20)}\n')