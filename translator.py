from typing import List
from parser import Instruction
from semantic import SymbolTable

class CodeGenerator:
    def __init__(self, valid_instructions: List[Instruction], symbol_table: SymbolTable):
        self.instructions = valid_instructions
        self.symbol_table = symbol_table
        self.generated_code = []
        self.variable_operations = {}
    def generate_set(self, instruction: Instruction) -> str:
        identifier, number = instruction.operands
        code = f"{identifier} = {number}"
        self.variable_operations[identifier] = 'assignment'
        return code
    def generate_arithmetic(self, instruction: Instruction) -> str:
        operand1, operand2 = instruction.operands
        op_type = instruction.type
        operator_map = {'ADD': '+','SUB': '-','MUL': '*','DIV': '//' }
        operator = operator_map[op_type]
        value1 = operand1[1] if operand1[0] == 'IDENTIFIER' else operand1[1]
        value2 = operand2[1] if operand2[0] == 'IDENTIFIER' else operand2[1]
        code = f"{value1} {operator} {value2}"
        return code
    def generate_print(self, instruction: Instruction) -> str:
        identifier = instruction.operands[0]
        code = f"print({identifier})"
        return code
    def generate(self) -> List[str]:
        self.generated_code = []
        for instruction in self.instructions:
            if instruction.type == 'SET':
                code = self.generate_set(instruction)
            elif instruction.type in ['ADD','SUB','MUL','DIV']:
                code = self.generate_arithmetic(instruction)
            elif instruction.type == 'PRINT':
                code = self.generate_print(instruction)
            else:
                continue
            self.generated_code.append(code)
        return self.generated_code
    def get_code_string(self) -> str:
        return '\n'.join(self.generated_code)

def generate_code(valid_instructions: List[Instruction], symbol_table: SymbolTable) -> str:
    generator = CodeGenerator(valid_instructions, symbol_table)
    generator.generate()
    return generator.get_code_string()
