from lexer import TokenType, Token
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SyntaxError:
    line: int
    column: int
    message: str
    def __str__(self):
        return f"Erro sintático na linha {self.line}, coluna {self.column}: {self.message}"

@dataclass
class Instruction:
    type: str
    operands: List
    line: int

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.instructions = []
        self.errors = []
    def peek(self, offset=0) -> Token:
        pos = self.position + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[pos]
    def advance(self) -> Token:
        token = self.peek()
        if self.position < len(self.tokens) - 1:
            self.position += 1
        return token
    def expect(self, token_type: TokenType) -> bool:
        return self.peek().type == token_type
    def consume(self, token_type: TokenType) -> Optional[Token]:
        token = self.peek()
        if token.type != token_type:
            return None
        self.advance()
        return token
    def add_error(self, message: str, token: Optional[Token] = None):
        if token is None:
            token = self.peek()
        self.errors.append(SyntaxError(token.line, token.column, message))
    def parse_set_instruction(self) -> Optional[Instruction]:
        set_token = self.consume(TokenType.SET)
        if set_token is None:
            return None
        line = set_token.line
        if not self.expect(TokenType.IDENTIFIER):
            self.add_error("Esperado identificador após SET")
            return None
        identifier = self.advance().value
        if not self.expect(TokenType.NUMBER):
            self.add_error("Esperado número após identificador em SET")
            return None
        number = self.advance().value
        return Instruction('SET', [identifier, number], line)
    def parse_arithmetic_instruction(self, instruction_type: str) -> Optional[Instruction]:
        token_map = {'ADD': TokenType.ADD,'SUB': TokenType.SUB,'MUL': TokenType.MUL,'DIV': TokenType.DIV}
        op_token = self.consume(token_map[instruction_type])
        if op_token is None:
            return None
        line = op_token.line
        operands = []
        operand1 = self.parse_operand()
        if operand1 is None:
            self.add_error(f"Esperado operando válido após {instruction_type}")
            return None
        operands.append(operand1)
        operand2 = self.parse_operand()
        if operand2 is None:
            self.add_error(f"Esperado segundo operando após {instruction_type}")
            return None
        operands.append(operand2)
        return Instruction(instruction_type, operands, line)
    def parse_operand(self):
        if self.expect(TokenType.IDENTIFIER):
            return ('IDENTIFIER', self.advance().value)
        elif self.expect(TokenType.NUMBER):
            return ('NUMBER', self.advance().value)
        else:
            return None
    def parse_print_instruction(self) -> Optional[Instruction]:
        print_token = self.consume(TokenType.PRINT)
        if print_token is None:
            return None
        line = print_token.line
        if not self.expect(TokenType.IDENTIFIER):
            self.add_error("Esperado identificador após PRINT")
            return None
        identifier = self.advance().value
        return Instruction('PRINT', [identifier], line)
    def parse_instruction(self) -> Optional[Instruction]:
        current_token = self.peek()
        if current_token.type == TokenType.SET:
            return self.parse_set_instruction()
        elif current_token.type == TokenType.ADD:
            return self.parse_arithmetic_instruction('ADD')
        elif current_token.type == TokenType.SUB:
            return self.parse_arithmetic_instruction('SUB')
        elif current_token.type == TokenType.MUL:
            return self.parse_arithmetic_instruction('MUL')
        elif current_token.type == TokenType.DIV:
            return self.parse_arithmetic_instruction('DIV')
        elif current_token.type == TokenType.PRINT:
            return self.parse_print_instruction()
        elif current_token.type == TokenType.EOF:
            return None
        else:
            self.add_error(f"Instrução inválida: {current_token.value}")
            self.advance()
            return None
    def parse(self) -> tuple:
        self.instructions = []
        self.errors = []
        while self.peek().type != TokenType.EOF:
            instruction = self.parse_instruction()
            if instruction is not None:
                self.instructions.append(instruction)
        return self.instructions, self.errors

def analyze_syntax(tokens: List[Token]) -> tuple:
    parser = Parser(tokens)
    return parser.parse()
