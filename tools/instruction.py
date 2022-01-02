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
            (OperandType.REGISTER, 0xF, 4, (0, 15)),
            (OperandType.REGISTER, 0xF, 8, (0, 15)),
            (OperandType.IMMEDIATE, 0xF, 0, (-8, 7))
        ],
        'RRI6': [
            (OperandType.REGISTER, 0xF, 0, (0, 15)),
            (OperandType.REGISTER, 0xF, 4, (0, 15)),
            (OperandType.IMMEDIATE, 0x3F, 8, (-0x20, 0x1F))
        ],
        'RI11': [
            (OperandType.REGISTER, 0xF, 0, (0, 15)),
            (OperandType.IMMEDIATE, 0x7FF, 4, (0, 0x7FF))
        ],
        'I12': [
            (OperandType.IMMEDIATE, 0xFFF, 0, (-0x800, 0x7FF))
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
            'opCode': (OperandType.OPCODE, 0x4, 15),
            'args': arguments['RI11']
        },
        'ST': {
            'opCode': (OperandType.OPCODE, 0x5, 15),
            'args': arguments['RI11']
        },
        'JUMP': {
            'opCode': (OperandType.OPCODE, 0x3F, 12),
            'args': arguments['I12']
        },
        'BEQ': {
            'opCode': (OperandType.OPCODE, 0x3A, 12),
            'args': arguments['I4RR']
        },
        'BGT': {
            'opCode': (OperandType.OPCODE, 0x39, 12),
            'args': arguments['I4RR']
        },
        'BLT': {
            'opCode': (OperandType.OPCODE, 0x3C, 12),
            'args': arguments['I4RR']
        },
        'BGE': {
            'opCode': (OperandType.OPCODE, 0x3B, 12),
            'args': arguments['I4RR']
        },
        'BLE': {
            'opCode': (OperandType.OPCODE, 0x3E, 12),
            'args': arguments['I4RR']
        }
    }

    def __init__(self, line: str, lineNumber: int, reObj: Pattern[str]):
        self.line = line
        self.lineNumber = lineNumber
        self.hexCode = 0
        self.reObj = reObj

        parsedLine = re.findall(self.reObj, self.line)

        # If regex result is empty throw error.
        if len(parsedLine) != 1:
            raise SyntaxError(f'Instruction format is wrong!\nLine {self.lineNumber}: "{line}"')

        # Remove empty matches.
        parsedLine = tuple(filter(None, parsedLine[0]))

        opCode = ()
        args = []

        try:
            inst = self.instructions[parsedLine[0].upper()]
            opCode = inst['opCode']
            args = inst['args']
        except KeyError:
            raise SyntaxError(f'Instruction is not found!\nLine {self.lineNumber}: "{line}" ({parsedLine[0]})')

        self.hexCode = opCode[1] << opCode[2]
        self.argParser(parsedLine[1:], args)
    
    def argParser(self, input: str, args: tuple):

        # Check parameter count.
        if len(input) != len(args):
            raise SyntaxError(f'Arguments length does not match!\nLine {self.lineNumber}: ({self.line})')
        
        # Loop over parameters.
        for inp, arg in zip(input, args):

            number = self.parseNumber(inp, arg)

            self.hexCode += (number & arg[1]) << arg[2]

    def parseNumber(self, num: str, arg: tuple) -> int:
        number = ''

        # Check if parameter is wanted type.
        if arg[0] == OperandType.REGISTER and num[0] != 'R':
            raise SyntaxError(f'Expected register, got immediate instead!\nLine {self.lineNumber}: "{self.line}" ({num})')

        if arg[0] == OperandType.IMMEDIATE and num[0] == 'R':
            raise SyntaxError(f'Expected immediate, got register instead!\nLine {self.lineNumber}: "{self.line}" ({num})')

        # Remove R from registers.
        number = num[1:] if arg[0] == OperandType.REGISTER else num

        number = self.strParse(number)

        lowerLimit, upperLimit = arg[3]

        # Check for overflow if there is, throw
        if number < lowerLimit or number > upperLimit:
            raise OverflowError(f'Overflow error!\nLine {self.lineNumber}: "{self.line}" ("{num}" = {number}) [{lowerLimit}, {upperLimit}]')

        return number

    def strParse(self, number: str) -> int:
        
        try:
            if (re.match('-?0b[01]+', number) != None):
                return int(number, 2)
            elif (re.match('-?0o[0-7]+', number) != None):
                return int(number, 8)
            elif (re.match('-?0x[0-9a-fA-F]+', number) != None):
                return int(number, 16)
            else:
                return int(number)
        except ValueError:
            raise ValueError(f'Illegal number format!\nLine {self.lineNumber}: "{self.line}" ({number})')