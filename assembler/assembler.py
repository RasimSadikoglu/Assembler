import sys, re
from instruction import Instruction

class Assembler:
    
    def __init__(self, filePath: str):
        fileContent = self.openFile(filePath)
        
        instructions = fileContent.split('\n')
        reObj = re.compile('^\\s*(\\w+)\\s+([Rr-]?[0-9a-fA-Fbox]+)(?:\\s*,\\s*([Rr-]?[0-9a-fA-Fbox]+))?(?:\\s*,\\s*([Rr-]?[0-9a-fA-Fbox]+))?\\s*$')

        self.hexCodes = []

        for ins, lineNumber in zip(instructions, range(1, len(instructions) + 1)):
            if (re.match('^\s*$', ins)):
                continue

            self.hexCodes.append(Instruction(ins, lineNumber, reObj).hexCode)
        
        self.writeFile(filePath.rsplit('.', maxsplit=1)[0] + '.hex')

    def openFile(self, filePath: str):
        try:
            with open(filePath, 'r') as input:
                return input.read()
        except FileNotFoundError:
            raise FileNotFoundError(f'File is not found! ({filePath})')

    def writeFile(self, filePath):
        try:
            with open(filePath, 'w') as output:
                for hexI in self.hexCodes:
                    hexString = hex(hexI)[2:].upper()
                    output.write(f':{"0" * (5 - len(hexString)) + hexString}\n')
        except FileNotFoundError:
            raise FileNotFoundError(f'Error while writing to the file! ({filePath})')

if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        print('Unexpected usage!\nUsage: py assembler.py <assembly_source>')
    else:
        Assembler(sys.argv[1])