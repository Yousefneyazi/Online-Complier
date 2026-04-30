from typing import List
from parser import ASTNode, Program, Assignment, IfStatement, WhileStatement, ForStatement, PrintStatement, BinaryOp, UnaryOp, Identifier, NumberLiteral, StringLiteral

class CodeGenerator:
    def __init__(self, ast: Program):
        self.ast = ast
        self.assembly: List[str] = []
        self.label_counter = 0

    def get_new_label(self) -> str:
        self.label_counter += 1
        return f"L{self.label_counter}"

    def generate(self) -> str:
        self.assembly = ["; --- Start Execution ---"]
        for statement in self.ast.statements:
            self.visit(statement)
        self.assembly.append("HALT")
        return "\n".join(self.assembly)

    def visit(self, node: ASTNode):
        if isinstance(node, Assignment):
            self.visit_assignment(node)
        elif isinstance(node, IfStatement):
            self.visit_if_statement(node)
        elif isinstance(node, WhileStatement):
            self.visit_while_statement(node)
        elif isinstance(node, ForStatement):
            self.visit_for_statement(node)
        elif isinstance(node, PrintStatement):
            self.visit_print_statement(node)
        else:
            raise ValueError(f"Unknown statement node: {type(node).__name__}")

    def visit_assignment(self, node: Assignment):
        self.assembly.append(f"; Assignment {node.identifier}")
        self.visit_expression(node.value)
        self.assembly.append(f"MOV {node.identifier}, R0")

    def visit_print_statement(self, node: PrintStatement):
        if isinstance(node.value, StringLiteral):
            self.assembly.append(f"; Print String")
            self.assembly.append(f"PRINT \"{node.value.value}\"")
        else:
            self.assembly.append("; Print Expression")
            self.visit_expression(node.value)
            self.assembly.append("PRINT R0")

    def visit_if_statement(self, node: IfStatement):
        end_label = self.get_new_label()
        
        # If condition
        next_label = self.get_new_label()
        self.assembly.append("; If Condition")
        self.visit_condition(node.condition)
        self.assembly.append(f"JMP_FALSE {next_label}")
        
        self.assembly.append("; Then Block")
        for stmt in node.then_block:
            self.visit(stmt)
        self.assembly.append(f"JMP {end_label}")
        
        # Elif chains
        for elif_cond, elif_block in node.elif_chains:
            self.assembly.append(f"{next_label}:")
            next_label = self.get_new_label()
            self.assembly.append("; Elif Condition")
            self.visit_condition(elif_cond)
            self.assembly.append(f"JMP_FALSE {next_label}")
            self.assembly.append("; Elif Block")
            for stmt in elif_block:
                self.visit(stmt)
            self.assembly.append(f"JMP {end_label}")
        
        # Else block
        self.assembly.append(f"{next_label}:")
        if node.else_block:
            self.assembly.append("; Else Block")
            for stmt in node.else_block:
                self.visit(stmt)
                
        self.assembly.append(f"{end_label}:")

    def visit_while_statement(self, node: WhileStatement):
        start_label = self.get_new_label()
        end_label = self.get_new_label()
        
        self.assembly.append(f"; While Loop")
        self.assembly.append(f"{start_label}:")
        self.visit_condition(node.condition)
        self.assembly.append(f"JMP_FALSE {end_label}")
        
        self.assembly.append("; Loop Body")
        for stmt in node.body:
            self.visit(stmt)
        
        self.assembly.append(f"JMP {start_label}")
        self.assembly.append(f"{end_label}:")

    def visit_for_statement(self, node: ForStatement):
        start_label = self.get_new_label()
        end_label = self.get_new_label()
        
        # Initialize loop variable
        self.assembly.append(f"; For Loop ({node.var_name})")
        self.visit_expression(node.start)
        self.assembly.append(f"MOV {node.var_name}, R0")
        
        # Loop start: compare var < end
        self.assembly.append(f"{start_label}:")
        self.visit_expression(node.end)
        self.assembly.append("PUSH R0")
        self.assembly.append(f"MOV R0, {node.var_name}")
        self.assembly.append("POP R1")
        self.assembly.append(f"CMP R0, R1 ; Operator: <")
        self.assembly.append(f"JMP_FALSE {end_label}")
        
        # Loop body
        self.assembly.append("; For Body")
        for stmt in node.body:
            self.visit(stmt)
        
        # Increment loop variable
        step_val = 1  # default step
        if node.step and isinstance(node.step, NumberLiteral):
            step_val = node.step.value
        self.assembly.append(f"; Increment {node.var_name}")
        self.assembly.append(f"MOV R0, {node.var_name}")
        self.assembly.append(f"MOV R1, {step_val}")
        self.assembly.append(f"ADD R0, R1")
        self.assembly.append(f"MOV {node.var_name}, R0")
        
        self.assembly.append(f"JMP {start_label}")
        self.assembly.append(f"{end_label}:")

    def visit_condition(self, node: ASTNode):
        """Generate assembly for any condition expression (comparisons, and/or/not)."""
        if isinstance(node, BinaryOp) and node.operator in ('==', '!=', '<', '>', '<=', '>='):
            self.visit_expression(node.right)
            self.assembly.append("PUSH R0")
            self.visit_expression(node.left)
            self.assembly.append("POP R1")
            self.assembly.append(f"CMP R0, R1 ; Operator: {node.operator}")
        elif isinstance(node, BinaryOp) and node.operator == 'and':
            false_label = self.get_new_label()
            end_label = self.get_new_label()
            self.visit_condition(node.left)
            self.assembly.append(f"JMP_FALSE {false_label}")
            self.visit_condition(node.right)
            self.assembly.append(f"JMP {end_label}")
            self.assembly.append(f"{false_label}:")
            self.assembly.append("MOV R0, 0  ; false")
            self.assembly.append(f"{end_label}:")
        elif isinstance(node, BinaryOp) and node.operator == 'or':
            true_label = self.get_new_label()
            end_label = self.get_new_label()
            self.visit_condition(node.left)
            self.assembly.append(f"JMP_TRUE {true_label}")
            self.visit_condition(node.right)
            self.assembly.append(f"JMP {end_label}")
            self.assembly.append(f"{true_label}:")
            self.assembly.append("MOV R0, 1  ; true")
            self.assembly.append(f"{end_label}:")
        elif isinstance(node, UnaryOp) and node.operator == 'not':
            self.visit_condition(node.operand)
            self.assembly.append("NOT R0")
        else:
            # Boolean-like expression (e.g., just a variable)
            self.visit_expression(node)

    def visit_expression(self, node: ASTNode):
        if isinstance(node, NumberLiteral):
            self.assembly.append(f"MOV R0, {node.value}")
        elif isinstance(node, Identifier):
            self.assembly.append(f"MOV R0, {node.name}")
        elif isinstance(node, BinaryOp):
            self.visit_expression(node.right)
            self.assembly.append("PUSH R0")
            self.visit_expression(node.left)
            self.assembly.append("POP R1")
            
            if node.operator == '+':
                self.assembly.append("ADD R0, R1")
            elif node.operator == '-':
                self.assembly.append("SUB R0, R1")
            elif node.operator == '*':
                self.assembly.append("MUL R0, R1")
            elif node.operator == '/':
                self.assembly.append("DIV R0, R1")
            elif node.operator == '%':
                self.assembly.append("MOD R0, R1")
            elif node.operator == '**':
                self.assembly.append("POW R0, R1")
            elif node.operator == '//':
                self.assembly.append("FDIV R0, R1")
        else:
            raise ValueError(f"Unknown expression node: {type(node).__name__}")

# Quick run script
if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser

    test_code = """
for i in range(3):
    print(i)
"""
    
    ast = Parser(Lexer(test_code).tokenize()).parse()
    generator = CodeGenerator(ast)
    print(generator.generate())
