import enum, re
from typing import Pattern

class OperandType(enum.Enum):
    REGISTER = 0
    IMMEDIATE = 1
    OPCODE = 2

class Instruction:

    arguments = {
        'RRR': [
            (OperandType.REGISTER, 0xF, 0, (0, 15)),
            (OperandType.REGISTER, 0xF, 4, (0, 15)),
            (OperandType.REGISTER, 0xF, 8, (0, 15))
        ],
        'RRI4': [
            (OperandType.REGISTER, 0xF, 0, (0, 15)),
            (OperandType.REGISTER, 0xF, 4, (0, 15)),
            (OperandType.IMMEDIATE, 0xF, 8, -8, 7)
        ],
        'RRI6': [
            (OperandType.REGISTER, 0xF, 0, (0, 15)),
            (OperandType.REGISTER, 0xF, 4, (0, 15)),
            (OperandType.IMMEDIATE, 0x3F, 8, (-0x20, 0x1F))
        ],
        'RI10': [
            (OperandType.REGISTER, 0xF, 0, (0, 15)),
            (OperandType.IMMEDIATE, 0x3FF, 4, (-0x200, 0x1FF))
        ],
        'I15': [
            (OperandType.IMMEDIATE, 0x7FFF, 0, (-0x4000, 0x3FFF))
        ]
    }

    instructions = {
        'AND': {
            'opCode': (OperandType.OPCODE, 0x0, 14),
            'args': arguments['RRR']
        },
        'ANDI': {
            'opCode': (OperandType.OPCODE, 0x1, 14),
            'args': arguments['RRI6']
        },
        'OR': {
            'opCode': (OperandType.OPCODE, 0x2, 14),
            'args': arguments['RRR']
        },
        'ORI': {
            'opCode': (OperandType.OPCODE, 0x3, 14),
            'args': arguments['RRI6']
        },
        'ADD': {
            'opCode': (OperandType.OPCODE, 0x4, 14),
            'args': arguments['RRR']
        },
        'ADDI': {
            'opCode': (OperandType.OPCODE, 0x5, 14),
            'args': arguments['RRI6']
        },
        'XOR': {
            'opCode': (OperandType.OPCODE, 0x6, 14),
            'args': arguments['RRR']
        },
        'XORI': {
            'opCode': (OperandType.OPCODE, 0x7, 14),
            'args': arguments['RRI6']
        },
        'LD': {
            'opCode': (OperandType.OPCODE, 0x8, 14),
            'args': arguments['RI10']
        },
        'ST': {
            'opCode': (OperandType.OPCODE, 0x9, 14),
            'args': arguments['RI10']
        },
        'JUMP': {
            'opCode': (OperandType.OPCODE, 0x6, 15),
            'args': arguments['I15']
        },
        'BEQ': {
            'opCode': (OperandType.OPCODE, 0x3A, 12),
            'args': arguments['RRI4']
        },
        'BGT': {
            'opCode': (OperandType.OPCODE, 0x39, 12),
            'args': arguments['RRI4']
        },
        'BLT': {
            'opCode': (OperandType.OPCODE, 0x3C, 12),
            'args': arguments['RRI4']
        },
        'BGE': {
            'opCode': (OperandType.OPCODE, 0x3B, 12),
            'args': arguments['RRI4']
        },
        'BLE': {
            'opCode': (OperandType.OPCODE, 0x3E, 12),
            'args': arguments['RRI4']
        }
    }

    def __init__(self, line: str, reObj: Pattern[str]):
        self.line = line
        self.hexCode = 0
        self.reObj = reObj

        parsedLine = re.findall(self.reObj, self.line)

        if len(parsedLine) != 1:
            raise SyntaxError(f'Instruction format is wrong! ({line})')

        parsedLine = tuple(filter(None, parsedLine[0]))

        opCode = ()
        args = []

        try:
            inst = self.instructions[parsedLine[0].upper()]
            opCode = inst['opCode']
            args = inst['args']
        except KeyError:
            raise KeyError(f'Instruction is not found!\nLine: "{line}" ({parsedLine[0]})')

        self.hexCode = opCode[1] << opCode[2]
        self.argParser(parsedLine[1:], args)
    
    def argParser(self, input: str, args: tuple):

        if len(input) != len(args):
            raise SyntaxError(f'Arguments length does not match! ({self.line})')
        
        for inp, arg in zip(input, args):

            number = self.parseNumber(inp, arg)

            self.hexCode += (number & arg[1]) << arg[2]

    def parseNumber(self, num: str, arg: tuple) -> int:
        number = -1

        if arg[0] == OperandType.REGISTER and num[0] != 'R':
            raise SyntaxError(f'Expected register, got immediate instead!\nLine: "{self.line}" ({num})')

        if arg[0] == OperandType.IMMEDIATE and num[0] == 'R':
            raise SyntaxError(f'Expected immediate, got register instead!\nLine: "{self.line}" ({num})')

        num = num[1:] if arg[0] == OperandType.REGISTER else num

        number = self.strParse(num)

        lowerLimit, upperLimit = arg[3]

        if number < lowerLimit or number > upperLimit:
            raise OverflowError(f'Overflow error!\nLine: "{self.line}" [{lowerLimit}, {upperLimit}]')

        return number

    def strParse(self, num: str) -> int:
        
        try:
            if (re.match('-?0b\d+', num)):
                return int(num, 2)
            elif (re.match('-?0o\d+', num)):
                return int(num, 8)
            elif (re.match('-?0x\d+', num)):
                return int(num, 16)
            else:
                return int(num)
        except ValueError:
            raise ValueError(f'Illegal number format!\nLine: "{self.line}" ({num})')

    def getHex(self) -> int:
        return self.hexCode