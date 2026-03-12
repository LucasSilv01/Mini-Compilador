from enum import Enum, auto
from dataclasses import dataclass

class TokenType(Enum):
    SET = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    PRINT = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    EOF = auto()
    ERROR = auto()

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int
    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, linha={self.line}, col={self.column})"

class Lexer:
    RESERVED_WORDS = {'SET': TokenType.SET,'ADD': TokenType.ADD,'SUB': TokenType.SUB,'MUL': TokenType.MUL,'DIV': TokenType.DIV,'PRINT': TokenType.PRINT}
    def __init__(self, source_code: str):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
    def error(self, message: str) -> Token:
        return Token(TokenType.ERROR, message, self.line, self.column)
    def peek(self) -> str:
        if self.position >= len(self.source):
            return '\0'
        return self.source[self.position]
    def advance(self) -> str:
        if self.position >= len(self.source):
            return '\0'
        char = self.source[self.position]; self.position += 1
        if char == '\n':
            self.line += 1; self.column = 1
        else:
            self.column += 1
        return char
    def skip_whitespace(self):
        while self.peek() in ' \t':
            self.advance()
    def skip_line(self):
        while self.peek() != '\n' and self.peek() != '\0':
            self.advance()
    def read_identifier(self) -> str:
        identifier = ''
        while self.peek().isalpha() or self.peek().isdigit() or self.peek() == '_':
            identifier += self.advance()
        return identifier
    def read_number(self) -> str:
        number = ''
        while self.peek().isdigit():
            number += self.advance()
        return number
    def tokenize(self) -> list:
        self.tokens = []
        while self.position < len(self.source):
            self.skip_whitespace()
            if self.peek() == '\0':
                break
            if self.peek() == '\n':
                self.advance(); continue
            if self.peek() == '#':
                self.skip_line(); continue
            char = self.peek(); line = self.line; column = self.column
            if char.isalpha():
                identifier = self.read_identifier()
                if identifier in self.RESERVED_WORDS:
                    token_type = self.RESERVED_WORDS[identifier]
                    self.tokens.append(Token(token_type, identifier, line, column))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, identifier, line, column))
            elif char.isdigit():
                number = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, number, line, column))
            else:
                self.tokens.append(self.error(f"Caractere inválido: '{char}'"))
                self.advance()
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens

def analyze_lexical(source_code: str) -> tuple:
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    errors = [token for token in tokens if token.type == TokenType.ERROR]
    return tokens, errors
