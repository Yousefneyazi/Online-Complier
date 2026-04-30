from parser import ASTNode, Program, Assignment, IfStatement, WhileStatement, ForStatement, PrintStatement, BinaryOp, UnaryOp, Identifier, NumberLiteral, StringLiteral

MAX_LOOP_ITERATIONS = 10000  # Safety limit to prevent infinite loops

class Interpreter:
    def __init__(self, ast: Program):
        self.ast = ast
        self.environment = {}
        self.output = []

    def run(self) -> str:
        try:
            for statement in self.ast.statements:
                self.visit(statement)
            return "\n".join(self.output)
        except Exception as e:
            return f"Runtime Error: {str(e)}"

    def visit(self, node: ASTNode):
        if isinstance(node, Assignment):
            self.environment[node.identifier] = self.evaluate(node.value)
        elif isinstance(node, PrintStatement):
            val = self.evaluate(node.value)
            self.output.append(str(val))
        elif isinstance(node, IfStatement):
            condition_val = self.evaluate(node.condition)
            if condition_val:
                for stmt in node.then_block:
                    self.visit(stmt)
            else:
                # Check elif chains
                handled = False
                for elif_cond, elif_block in node.elif_chains:
                    if self.evaluate(elif_cond):
                        for stmt in elif_block:
                            self.visit(stmt)
                        handled = True
                        break
                # Fall through to else if no elif matched
                if not handled and node.else_block:
                    for stmt in node.else_block:
                        self.visit(stmt)
        elif isinstance(node, WhileStatement):
            iterations = 0
            while self.evaluate(node.condition):
                iterations += 1
                if iterations > MAX_LOOP_ITERATIONS:
                    raise RuntimeError(f"Infinite loop detected: exceeded {MAX_LOOP_ITERATIONS} iterations")
                for stmt in node.body:
                    self.visit(stmt)
        elif isinstance(node, ForStatement):
            start_val = self.evaluate(node.start)
            end_val = self.evaluate(node.end)
            step_val = self.evaluate(node.step) if node.step else 1
            
            if step_val == 0:
                raise RuntimeError("for loop step cannot be zero")
            
            i = start_val
            iterations = 0
            while (step_val > 0 and i < end_val) or (step_val < 0 and i > end_val):
                iterations += 1
                if iterations > MAX_LOOP_ITERATIONS:
                    raise RuntimeError(f"Infinite loop detected: exceeded {MAX_LOOP_ITERATIONS} iterations")
                self.environment[node.var_name] = i
                for stmt in node.body:
                    self.visit(stmt)
                i += step_val

    def evaluate(self, node: ASTNode):
        if isinstance(node, NumberLiteral):
            return node.value
        elif isinstance(node, StringLiteral):
            return node.value
        elif isinstance(node, Identifier):
            if node.name not in self.environment:
                raise ValueError(f"Undefined variable '{node.name}'")
            return self.environment[node.name]
        elif isinstance(node, UnaryOp):
            if node.operator == 'not':
                return not self.evaluate(node.operand)
        elif isinstance(node, BinaryOp):
            # Short-circuit for logical operators
            if node.operator == 'and':
                left_val = self.evaluate(node.left)
                if not left_val:
                    return False
                return bool(self.evaluate(node.right))
            elif node.operator == 'or':
                left_val = self.evaluate(node.left)
                if left_val:
                    return True
                return bool(self.evaluate(node.right))
            
            left_val = self.evaluate(node.left)
            right_val = self.evaluate(node.right)
            
            if node.operator == '+': return left_val + right_val
            elif node.operator == '-': return left_val - right_val
            elif node.operator == '*': return left_val * right_val
            elif node.operator == '**': return left_val ** right_val
            elif node.operator == '/': 
                if right_val == 0:
                    raise ZeroDivisionError("Division by zero")
                return left_val / right_val
            elif node.operator == '%': 
                if right_val == 0:
                    raise ZeroDivisionError("Modulo by zero")
                return left_val % right_val
            elif node.operator == '//': 
                if right_val == 0:
                    raise ZeroDivisionError("Division by zero")
                return left_val // right_val
            elif node.operator == '==': return left_val == right_val
            elif node.operator == '!=': return left_val != right_val
            elif node.operator == '<': return left_val < right_val
            elif node.operator == '>': return left_val > right_val
            elif node.operator == '<=': return left_val <= right_val
            elif node.operator == '>=': return left_val >= right_val
            
        raise ValueError(f"Unknown expression type: {type(node).__name__}")
