import sys, re
from instruction import Instruction

class Assembler:
    
    def __init__(self, filePath: str):
        fileContent = self.openFile(filePath)
        
        instructions = filter(None, fileContent.split('\n'))
        reObj = re.compile('^\\s*(\\w+)\\s+([Rr-]?[0-9box]+)(?:\\s*,\\s*([Rr-]?[0-9box]+))?(?:\\s*,\\s*([Rr-]?[0-9box]+))?\\s*$')

        self.hexCodes = []

        for ins in instructions:
            self.hexCodes.append(Instruction(ins, reObj).hexCode)
        
        self.writeFile(filePath.rsplit('.', maxsplit=1)[0] + '.hex')

    def openFile(self, filePath: str):
        try:
            with open(filePath, 'r') as input:
                return input.read()
        except:
            print(f'File does not found! ({filePath})')
            exit(1)

    def writeFile(self, filePath):
        try:
            with open(filePath, 'w') as output:
                for hexI in self.hexCodes:
                    output.write(f':{hex(hexI)[2:].upper()}\n')
        except:
            print(f'Error while writing to the file! ({filePath})')
            exit(1)

if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        print('Unexpected usage!\nUsage: py assembler.py <assembly_source>')
    else:
        Assembler(sys.argv[1])