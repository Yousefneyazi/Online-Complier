import re
from typing import List, Dict, Any

class TokenType:
    # Keywords
    IF = 'IF'
    ELIF = 'ELIF'
    ELSE = 'ELSE'
    WHILE = 'WHILE'
    FOR = 'FOR'
    IN = 'IN'
    RANGE = 'RANGE'
    PRINT = 'PRINT'
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'
    
    # Identifiers and Literals
    IDENTIFIER = 'IDENTIFIER'
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    
    # Operators
    ASSIGN = 'ASSIGN'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MUL = 'MUL'
    DIV = 'DIV'
    MOD = 'MOD'
    POW = 'POW'
    FLOORDIV = 'FLOORDIV'
    EQ = 'EQ'
    NEQ = 'NEQ'
    LT = 'LT'
    GT = 'GT'
    LE = 'LE'
    GE = 'GE'
    
    # Punctuation
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    COLON = 'COLON'
    COMMA = 'COMMA'
    
    # Structural
    NEWLINE = 'NEWLINE'
    INDENT = 'INDENT'
    DEDENT = 'DEDENT'
    EOF = 'EOF'
    ILLEGAL = 'ILLEGAL'

class Token:
    def __init__(self, type_: str, value: str, line: int):
        self.type = type_
        self.value = value
        self.line = line

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy JSON serialization (FastAPI)."""
        return {"type": self.type, "value": self.value, "line": self.line}

    def __repr__(self):
        return f"Token({self.type}, '{self.value}')"

class Lexer:
    def __init__(self, source_code: str):
        self.source_code = source_code + "\n"  # Guarantee a trailing newline
        self.tokens: List[Token] = []
        
        # Regular expressions for different token types
        # Note: Order matters! E.g., '==' must come before '=', '<=' before '<'
        self.token_specs = [
            ('NUMBER',     r'\d+(\.\d*)?'),      # Integer or decimal number
            ('STRING',     r'["\']([^"\']*)["\']'),  # String literal (single or double quotes)
            ('IF',         r'\bif\b'),           # 'if' keyword
            ('ELIF',       r'\belif\b'),         # 'elif' keyword
            ('ELSE',       r'\belse\b'),         # 'else' keyword
            ('WHILE',      r'\bwhile\b'),        # 'while' keyword
            ('FOR',        r'\bfor\b'),          # 'for' keyword
            ('IN',         r'\bin\b'),           # 'in' keyword
            ('RANGE',      r'\brange\b'),        # 'range' keyword
            ('PRINT',      r'\bprint\b'),        # 'print' keyword
            ('AND',        r'\band\b'),          # 'and' keyword
            ('OR',         r'\bor\b'),           # 'or' keyword
            ('NOT',        r'\bnot\b'),          # 'not' keyword
            ('IDENTIFIER', r'[A-Za-z_]\w*'),     # Identifiers/Variables
            ('EQ',         r'=='),               # Equal operator
            ('NEQ',        r'!='),               # Not equal operator
            ('LE',         r'<='),               # Less than or equal (must be before LT)
            ('GE',         r'>='),               # Greater than or equal (must be before GT)
            ('ASSIGN',     r'='),                # Assignment operator
            ('LT',         r'<'),                # Less than
            ('GT',         r'>'),                # Greater than
            ('PLUS',       r'\+'),               # Addition
            ('MINUS',      r'-'),                # Subtraction
            ('POW',        r'\*\*'),             # Exponentiation (Must be before MUL)
            ('MUL',        r'\*'),               # Multiplication
            ('FLOORDIV',   r'//'),               # Floor division (Must be before DIV)
            ('DIV',        r'/'),                # Division
            ('MOD',        r'%'),                # Modulus
            ('LPAREN',     r'\('),               # Left Parenthesis
            ('RPAREN',     r'\)'),               # Right Parenthesis
            ('COLON',      r':'),                # Colon
            ('COMMA',      r','),                # Comma
            ('NEWLINE',    r'\n[ \t]*'),         # Match newline and any leading whitespace for indentation
            ('SKIP',       r'[ \t]+'),           # Skip over spaces and tabs
            ('MISMATCH',   r'.'),                # Any other illegal character
        ]
        # Combine all regexes into one master regex with named groups
        self.regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in self.token_specs)
        
    def tokenize(self) -> List[Token]:
        line_num = 1
        indent_stack = [0]
        
        for match in re.finditer(self.regex, self.source_code):
            kind = match.lastgroup
            value = match.group(kind)
            
            if kind == 'STRING':
                # Extract just the string content without the surrounding quotes
                value = match.group(2) if match.group(2) is not None else value[1:-1]
            elif kind == 'NEWLINE':
                line_num += 1
                indent_level = len(value.replace('\n', ''))
                
                # Treat empty lines as skip, unless it's EOF
                if match.end() < len(self.source_code) and self.source_code[match.end()] == '\n':
                    continue
                
                self.tokens.append(Token('NEWLINE', '\\n', line_num))
                
                if indent_level > indent_stack[-1]:
                    indent_stack.append(indent_level)
                    self.tokens.append(Token('INDENT', ' ' * indent_level, line_num))
                elif indent_level < indent_stack[-1]:
                    while len(indent_stack) > 1 and indent_level < indent_stack[-1]:
                        indent_stack.pop()
                        self.tokens.append(Token('DEDENT', '', line_num))
                continue
            elif kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                hint = self._get_error_hint(value, line_num)
                raise SyntaxError(f"Syntax Error at line {line_num}: Illegal character '{value}'. {hint}")
            
            self.tokens.append(Token(kind, value, line_num))
            
        # Clean up any remaining indents at EOF
        while len(indent_stack) > 1:
            indent_stack.pop()
            self.tokens.append(Token('DEDENT', '', line_num))
            
        # Append EOF marker
        self.tokens.append(Token(TokenType.EOF, "", line_num))
        
        # Filter out multiple consecutive newlines safely
        filtered_tokens = []
        for i, t in enumerate(self.tokens):
            if t.type == 'NEWLINE' and i > 0 and self.tokens[i-1].type == 'NEWLINE':
                continue
            filtered_tokens.append(t)
            
        self.tokens = filtered_tokens
        return self.tokens

    def _get_error_hint(self, char: str, line: int) -> str:
        """Provide a helpful hint for common illegal characters."""
        hints = {
            '{': "Hint: Use ':' and indentation instead of curly braces (Python-style blocks).",
            '}': "Hint: Use ':' and indentation instead of curly braces (Python-style blocks).",
            ';': "Hint: Semicolons are not needed. Use a new line to end statements.",
            '&': "Hint: Use 'and' for logical AND.",
            '|': "Hint: Use 'or' for logical OR.",
            '[': "Hint: Lists/arrays are not supported in this language.",
            ']': "Hint: Lists/arrays are not supported in this language.",
            '#': "Hint: Comments are not supported. Remove the '#' and the text after it.",
            '@': "Hint: Decorators are not supported in this language.",
            '\\': "Hint: Backslash is not a valid operator.",
            '~': "Hint: Bitwise NOT is not supported.",
            '^': "Hint: Use '**' for exponentiation instead of '^'.",
            '!': "Hint: Use 'not' for logical negation, or '!=' for not-equal.",
        }
        return hints.get(char, "Hint: This character is not part of the language syntax.")

# Quick script test if executed directly
if __name__ == "__main__":
    test_code = """
x = 5
if x > 0 and x < 10:
    print('yes')
for i in range(3):
    print(i)
"""
    lexer = Lexer(test_code)
    for token in lexer.tokenize():
        print(token)
