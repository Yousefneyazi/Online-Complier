from typing import List, Dict, Any, Optional
from lexer import Token

class ASTNode:
    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError()

class Program(ASTNode):
    def __init__(self, statements: List[ASTNode]):
        self.statements = statements

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Program",
            "statements": [stmt.to_dict() for stmt in self.statements]
        }

class Assignment(ASTNode):
    def __init__(self, identifier: str, value: ASTNode):
        self.identifier = identifier
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Assignment",
            "identifier": self.identifier,
            "value": self.value.to_dict()
        }

class PrintStatement(ASTNode):
    def __init__(self, value: ASTNode):
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "PrintStatement",
            "value": self.value.to_dict()
        }

class IfStatement(ASTNode):
    def __init__(self, condition: ASTNode, then_block: List[ASTNode], elif_chains: Optional[List[tuple]], else_block: Optional[List[ASTNode]]):
        self.condition = condition
        self.then_block = then_block
        self.elif_chains = elif_chains or []   # List of (condition, block) tuples
        self.else_block = else_block

    def to_dict(self) -> Dict[str, Any]:
        res = {
            "type": "IfStatement",
            "condition": self.condition.to_dict(),
            "then_block": [stmt.to_dict() for stmt in self.then_block],
        }
        if self.elif_chains:
            res["elif_chains"] = [
                {
                    "condition": cond.to_dict(),
                    "block": [stmt.to_dict() for stmt in block]
                }
                for cond, block in self.elif_chains
            ]
        if self.else_block is not None:
            res["else_block"] = [stmt.to_dict() for stmt in self.else_block]
        return res

class WhileStatement(ASTNode):
    def __init__(self, condition: ASTNode, body: List[ASTNode]):
        self.condition = condition
        self.body = body

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "WhileStatement",
            "condition": self.condition.to_dict(),
            "body": [stmt.to_dict() for stmt in self.body]
        }

class ForStatement(ASTNode):
    """for <var> in range(<start>, <end>, <step>):"""
    def __init__(self, var_name: str, start: ASTNode, end: ASTNode, step: Optional[ASTNode], body: List[ASTNode]):
        self.var_name = var_name
        self.start = start
        self.end = end
        self.step = step
        self.body = body

    def to_dict(self) -> Dict[str, Any]:
        res = {
            "type": "ForStatement",
            "variable": self.var_name,
            "start": self.start.to_dict(),
            "end": self.end.to_dict(),
            "body": [stmt.to_dict() for stmt in self.body]
        }
        if self.step:
            res["step"] = self.step.to_dict()
        return res

class BinaryOp(ASTNode):
    def __init__(self, left: ASTNode, operator: str, right: ASTNode):
        self.left = left
        self.operator = operator
        self.right = right

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "BinaryOp",
            "operator": self.operator,
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }

class UnaryOp(ASTNode):
    def __init__(self, operator: str, operand: ASTNode):
        self.operator = operator
        self.operand = operand

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "UnaryOp",
            "operator": self.operator,
            "operand": self.operand.to_dict()
        }

class Identifier(ASTNode):
    def __init__(self, name: str):
        self.name = name

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "Identifier", "name": self.name}

class NumberLiteral(ASTNode):
    def __init__(self, value: float):
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "NumberLiteral", "value": self.value}

class StringLiteral(ASTNode):
    def __init__(self, value: str):
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "StringLiteral", "value": self.value}

# ---------- Syntax error hint helpers ----------

def _token_friendly_name(token_type: str) -> str:
    """Map internal token type names to human-readable descriptions."""
    names = {
        'IDENTIFIER': 'a variable name',
        'NUMBER': 'a number',
        'STRING': 'a string',
        'ASSIGN': "'='",
        'PLUS': "'+'",
        'MINUS': "'-'",
        'MUL': "'*'",
        'DIV': "'/'",
        'MOD': "'%'",
        'POW': "'**'",
        'FLOORDIV': "'//'",
        'EQ': "'=='",
        'NEQ': "'!='",
        'LT': "'<'",
        'GT': "'>'",
        'LE': "'<='",
        'GE': "'>='",
        'LPAREN': "'('",
        'RPAREN': "')'",
        'COLON': "':'",
        'COMMA': "','",
        'NEWLINE': 'a new line',
        'INDENT': 'an indented block',
        'DEDENT': 'end of indented block',
        'EOF': 'end of file',
        'IF': "'if'",
        'ELIF': "'elif'",
        'ELSE': "'else'",
        'WHILE': "'while'",
        'FOR': "'for'",
        'IN': "'in'",
        'RANGE': "'range'",
        'PRINT': "'print'",
        'AND': "'and'",
        'OR': "'or'",
        'NOT': "'not'",
    }
    return names.get(token_type, f"'{token_type}'")

def _syntax_hint(expected: str, found: str, context: str = "") -> str:
    """Generate a helpful hint based on what was expected vs what was found."""
    hints = []
    
    if expected == 'COLON' and found in ('NEWLINE', 'EOF', 'INDENT'):
        hints.append("Hint: Did you forget ':' at the end of your if/elif/else/while/for statement?")
        hints.append("Example: if x == 5:")
    elif expected == 'INDENT' and found in ('IDENTIFIER', 'IF', 'ELIF', 'ELSE', 'WHILE', 'FOR', 'PRINT'):
        hints.append("Hint: The code block after if/elif/else/while/for must be indented (use 4 spaces).")
        hints.append("Example:\nif x == 5:\n    print(x)")
    elif expected == 'RPAREN':
        hints.append("Hint: Missing closing parenthesis ')'.")
    elif expected == 'LPAREN' and context == 'print':
        hints.append("Hint: print requires parentheses. Write 'print(x)' not 'print x'.")
    elif expected == 'LPAREN' and context == 'range':
        hints.append("Hint: range requires parentheses. Write 'range(n)' not 'range n'.")
    elif expected == 'IN' and context == 'for':
        hints.append("Hint: 'for' loop requires 'in'. Write 'for i in range(n):'")
    elif expected == 'RANGE' and context == 'for':
        hints.append("Hint: 'for' loop requires 'range'. Write 'for i in range(n):'")
    
    return " ".join(hints)

# ---------- Parser ----------

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def expect(self, token_type: str, context: str = ""):
        if self.current_token and self.current_token.type == token_type:
            self.advance()
        else:
            found = self.current_token.type if self.current_token else "EOF"
            line = self.current_token.line if self.current_token else 'unknown'
            expected_name = _token_friendly_name(token_type)
            found_name = _token_friendly_name(found)
            hint = _syntax_hint(token_type, found, context)
            msg = f"Syntax Error at line {line}: Expected {expected_name} but found {found_name}."
            if hint:
                msg += f" {hint}"
            raise SyntaxError(msg)

    def parse(self) -> Program:
        statements = []
        while self.current_token and self.current_token.type != 'EOF':
            if self.current_token.type == 'NEWLINE':
                self.advance()
                continue
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return Program(statements)

    def parse_statement(self) -> ASTNode:
        if self.current_token.type == 'NEWLINE':
            self.advance()
            return None
            
        if self.current_token.type == 'IDENTIFIER':
            return self.parse_assignment()
        elif self.current_token.type == 'PRINT':
            return self.parse_print()
        elif self.current_token.type == 'IF':
            return self.parse_if()
        elif self.current_token.type == 'WHILE':
            return self.parse_while()
        elif self.current_token.type == 'FOR':
            return self.parse_for()
        else:
            token = self.current_token
            # Provide specific hints for common mistakes
            if token.type == 'ELSE':
                raise SyntaxError(
                    f"Syntax Error at line {token.line}: 'else' without a matching 'if'. "
                    "Hint: 'else' must come directly after an 'if' or 'elif' block."
                )
            elif token.type == 'ELIF':
                raise SyntaxError(
                    f"Syntax Error at line {token.line}: 'elif' without a matching 'if'. "
                    "Hint: 'elif' must come after an 'if' block."
                )
            elif token.type in ('NUMBER', 'STRING'):
                raise SyntaxError(
                    f"Syntax Error at line {token.line}: Unexpected {_token_friendly_name(token.type)} '{token.value}'. "
                    "Hint: A statement must start with a variable name, 'if', 'elif', 'else', 'while', 'for', or 'print'."
                )
            else:
                raise SyntaxError(
                    f"Syntax Error at line {token.line}: Unexpected token {_token_friendly_name(token.type)}. "
                    "Hint: A statement must start with a variable name, 'if', 'while', 'for', or 'print'."
                )

    def consume_end_of_statement(self):
        if self.current_token and self.current_token.type == 'NEWLINE':
            self.advance()
        elif self.current_token and self.current_token.type == 'EOF':
            pass
        else:
            self.expect('NEWLINE')

    def parse_assignment(self) -> ASTNode:
        identifier = self.current_token.value
        self.expect('IDENTIFIER')
        self.expect('ASSIGN')
        expr = self.parse_expression()
        self.consume_end_of_statement()
        return Assignment(identifier, expr)

    def parse_print(self) -> ASTNode:
        self.expect('PRINT')
        self.expect('LPAREN', context='print')
        
        if self.current_token.type == 'STRING':
            val = StringLiteral(self.current_token.value)
            self.advance()
        else:
            val = self.parse_expression()
            
        self.expect('RPAREN')
        self.consume_end_of_statement()
        return PrintStatement(val)

    def _parse_block(self) -> List[ASTNode]:
        """Parse an indented block of statements (used by if/elif/else/while/for)."""
        self.expect('NEWLINE')
        self.expect('INDENT')
        block = []
        while self.current_token and self.current_token.type not in ('DEDENT', 'EOF'):
            if self.current_token.type == 'NEWLINE':
                self.advance()
                continue
            stmt = self.parse_statement()
            if stmt:
                block.append(stmt)
        if self.current_token and self.current_token.type == 'DEDENT':
            self.expect('DEDENT')
        return block

    def parse_if(self) -> ASTNode:
        self.expect('IF')
        condition = self.parse_condition()
        self.expect('COLON')
        then_block = self._parse_block()
        
        # Parse elif chains
        elif_chains = []
        while self.current_token and self.current_token.type == 'ELIF':
            self.expect('ELIF')
            elif_cond = self.parse_condition()
            self.expect('COLON')
            elif_block = self._parse_block()
            elif_chains.append((elif_cond, elif_block))
        
        # Parse optional else
        else_block = None
        if self.current_token and self.current_token.type == 'ELSE':
            self.expect('ELSE')
            self.expect('COLON')
            else_block = self._parse_block()
            
        return IfStatement(condition, then_block, elif_chains, else_block)

    def parse_while(self) -> ASTNode:
        self.expect('WHILE')
        condition = self.parse_condition()
        self.expect('COLON')
        body = self._parse_block()
        return WhileStatement(condition, body)

    def parse_for(self) -> ASTNode:
        """Parse: for <var> in range(<args>):"""
        self.expect('FOR')
        
        if not self.current_token or self.current_token.type != 'IDENTIFIER':
            line = self.current_token.line if self.current_token else 'unknown'
            raise SyntaxError(
                f"Syntax Error at line {line}: Expected a variable name after 'for'. "
                "Hint: Write 'for i in range(n):'"
            )
        var_name = self.current_token.value
        self.advance()
        
        self.expect('IN', context='for')
        self.expect('RANGE', context='for')
        self.expect('LPAREN', context='range')
        
        # Parse range arguments: range(end) or range(start, end) or range(start, end, step)
        first_arg = self.parse_expression()
        
        if self.current_token and self.current_token.type == 'COMMA':
            # range(start, end, ...)
            self.advance()  # consume comma
            second_arg = self.parse_expression()
            start = first_arg
            end = second_arg
            
            if self.current_token and self.current_token.type == 'COMMA':
                # range(start, end, step)
                self.advance()
                step = self.parse_expression()
            else:
                step = None
        else:
            # range(end) — start defaults to 0
            start = NumberLiteral(0)
            end = first_arg
            step = None
        
        self.expect('RPAREN')
        self.expect('COLON')
        body = self._parse_block()
        
        return ForStatement(var_name, start, end, step, body)

    def parse_condition(self) -> ASTNode:
        """Parse logical expressions: or has lowest precedence, then and, then not, then comparisons."""
        return self.parse_or()

    def parse_or(self) -> ASTNode:
        node = self.parse_and()
        while self.current_token and self.current_token.type == 'OR':
            self.advance()
            right = self.parse_and()
            node = BinaryOp(node, 'or', right)
        return node

    def parse_and(self) -> ASTNode:
        node = self.parse_not()
        while self.current_token and self.current_token.type == 'AND':
            self.advance()
            right = self.parse_not()
            node = BinaryOp(node, 'and', right)
        return node

    def parse_not(self) -> ASTNode:
        if self.current_token and self.current_token.type == 'NOT':
            self.advance()
            operand = self.parse_not()
            return UnaryOp('not', operand)
        return self.parse_comparison()

    def parse_comparison(self) -> ASTNode:
        left = self.parse_expression()
        if self.current_token and self.current_token.type in ('EQ', 'NEQ', 'LT', 'GT', 'LE', 'GE'):
            op = self.current_token.value
            self.advance()
            right = self.parse_expression()
            return BinaryOp(left, op, right)
        return left

    def parse_expression(self) -> ASTNode:
        node = self.parse_term()
        while self.current_token and self.current_token.type in ('PLUS', 'MINUS'):
            op = self.current_token.value
            self.advance()
            right = self.parse_term()
            node = BinaryOp(node, op, right)
        return node

    def parse_term(self) -> ASTNode:
        node = self.parse_power()
        while self.current_token and self.current_token.type in ('MUL', 'DIV', 'MOD', 'FLOORDIV'):
            op = self.current_token.value
            self.advance()
            right = self.parse_power()
            node = BinaryOp(node, op, right)
        return node

    def parse_power(self) -> ASTNode:
        node = self.parse_factor()
        # ** is right-associative in Python
        if self.current_token and self.current_token.type == 'POW':
            op = self.current_token.value
            self.advance()
            right = self.parse_power() # Recursive for right-associativity
            node = BinaryOp(node, op, right)
        return node

    def parse_factor(self) -> ASTNode:
        token = self.current_token
        if token is None:
            raise SyntaxError(
                "Syntax Error: Unexpected end of input. "
                "Hint: Expression is incomplete. Did you forget a value after an operator?"
            )
        if token.type == 'NUMBER':
            self.advance()
            return NumberLiteral(float(token.value) if '.' in token.value else int(token.value))
        elif token.type == 'IDENTIFIER':
            self.advance()
            return Identifier(token.value)
        elif token.type == 'STRING':
            self.advance()
            return StringLiteral(token.value)
        elif token.type == 'LPAREN':
            self.advance()
            node = self.parse_expression()
            self.expect('RPAREN')
            return node
        elif token.type == 'MINUS':
            # Support unary minus: -5, -(x + 1)
            self.advance()
            operand = self.parse_factor()
            return BinaryOp(NumberLiteral(0), '-', operand)
        
        # Helpful error messages for common mistakes
        if token.type == 'RPAREN':
            raise SyntaxError(
                f"Syntax Error at line {token.line}: Unexpected ')'. "
                "Hint: You may have an extra closing parenthesis or an empty expression."
            )
        elif token.type == 'COLON':
            raise SyntaxError(
                f"Syntax Error at line {token.line}: Unexpected ':'. "
                "Hint: ':' can only appear after if/elif/else/while/for conditions."
            )
        elif token.type == 'ASSIGN':
            raise SyntaxError(
                f"Syntax Error at line {token.line}: Unexpected '='. "
                "Hint: Did you mean '==' for comparison? '=' is only for assignment."
            )
        
        raise SyntaxError(
            f"Syntax Error at line {token.line}: Unexpected {_token_friendly_name(token.type)} in expression. "
            "Hint: Expected a number, variable name, string, or '('."
        )

# Quick script test if executed directly
if __name__ == "__main__":
    from lexer import Lexer
    import json
    
    test_code = """
for i in range(5):
    print(i)
x = 3
if x > 0 and x < 10:
    print('yes')
if not x == 0:
    print('not zero')
"""
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    print(json.dumps(ast.to_dict(), indent=2))
