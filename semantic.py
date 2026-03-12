from dataclasses import dataclass
from typing import Dict, Optional, List
from parser import Instruction

@dataclass
class Symbol:
    name: str
    value: Optional[int] = None
    declared_at_line: int = 0
    is_declared: bool = False
    def __repr__(self):
        return f"Symbol({self.name}, value={self.value}, declared={self.is_declared})"

@dataclass
class SemanticError:
    line: int
    message: str
    def __str__(self):
        return f"Erro semântico na linha {self.line}: {self.message}"

class SymbolTable:
    def __init__(self):
        self.symbols: Dict[str, Symbol] = {}
    def declare_variable(self, name: str, value: int, line: int) -> bool:
        if name in self.symbols:
            return False
        symbol = Symbol(name=name, value=value, declared_at_line=line, is_declared=True)
        self.symbols[name] = symbol
        return True
    def get_variable(self, name: str) -> Optional[Symbol]:
        return self.symbols.get(name)
    def is_declared(self, name: str) -> bool:
        return name in self.symbols and self.symbols[name].is_declared
    def update_variable(self, name: str, value: int) -> bool:
        if name not in self.symbols:
            return False
        self.symbols[name].value = value
        return True
    def get_all_variables(self) -> Dict[str, Symbol]:
        return {name: sym for name, sym in self.symbols.items() if sym.is_declared}
    def __repr__(self):
        return f"SymbolTable({self.symbols})"

class SemanticAnalyzer:
    RESERVED_WORDS = {'SET', 'ADD', 'SUB', 'MUL', 'DIV', 'PRINT'}
    def __init__(self, instructions: List[Instruction]):
        self.instructions = instructions
        self.symbol_table = SymbolTable()
        self.errors = []
        self.valid_instructions = []
    def add_error(self, message: str, line: int):
        self.errors.append(SemanticError(line, message))
    def get_operand_value(self, operand, instruction_line: int) -> Optional[int]:
        operand_type, operand_value = operand
        if operand_type == 'NUMBER':
            return int(operand_value)
        elif operand_type == 'IDENTIFIER':
            if not self.symbol_table.is_declared(operand_value):
                self.add_error(f"Variável '{operand_value}' não declarada", instruction_line)
                return None
            symbol = self.symbol_table.get_variable(operand_value)
            if symbol is not None:
                return symbol.value
            return None
        return None
    def analyze_set(self, instruction: Instruction) -> bool:
        identifier, number = instruction.operands
        if identifier in self.RESERVED_WORDS:
            self.add_error(f"'{identifier}' é uma palavra reservada", instruction.line)
            return False
        if self.symbol_table.is_declared(identifier):
            self.add_error(f"Variável '{identifier}' já foi declarada", instruction.line)
            return False
        try:
            value = int(number)
        except ValueError:
            self.add_error(f"Número inválido: {number}", instruction.line)
            return False
        self.symbol_table.declare_variable(identifier, value, instruction.line)
        self.valid_instructions.append(instruction)
        return True
    def analyze_arithmetic(self, instruction: Instruction) -> bool:
        operand1, operand2 = instruction.operands
        if operand1[0] == 'IDENTIFIER' and not self.symbol_table.is_declared(operand1[1]):
            self.add_error(f"Variável '{operand1[1]}' não declarada", instruction.line)
            return False
        if operand2[0] == 'IDENTIFIER' and not self.symbol_table.is_declared(operand2[1]):
            self.add_error(f"Variável '{operand2[1]}' não declarada", instruction.line)
            return False
        value1 = self.get_operand_value(operand1, instruction.line)
        value2 = self.get_operand_value(operand2, instruction.line)
        if value1 is None or value2 is None:
            return False
        if instruction.type == 'ADD':
            result = value1 + value2
        elif instruction.type == 'SUB':
            result = value1 - value2
        elif instruction.type == 'MUL':
            result = value1 * value2
        elif instruction.type == 'DIV':
            if value2 == 0:
                self.add_error("Divisão por zero", instruction.line)
                return False
            result = value1 // value2
        self.valid_instructions.append(instruction)
        return True
    def analyze_print(self, instruction: Instruction) -> bool:
        identifier = instruction.operands[0]
        if not self.symbol_table.is_declared(identifier):
            self.add_error(f"Variável '{identifier}' não declarada", instruction.line)
            return False
        self.valid_instructions.append(instruction)
        return True
    def analyze(self) -> tuple:
        self.valid_instructions = []
        self.errors = []
        for instruction in self.instructions:
            if instruction.type == 'SET':
                self.analyze_set(instruction)
            elif instruction.type in ['ADD', 'SUB', 'MUL', 'DIV']:
                self.analyze_arithmetic(instruction)
            elif instruction.type == 'PRINT':
                self.analyze_print(instruction)
        return self.valid_instructions, self.symbol_table, self.errors

def analyze_semantic(instructions: List[Instruction]) -> tuple:
    analyzer = SemanticAnalyzer(instructions)
    return analyzer.analyze()
