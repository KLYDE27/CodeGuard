import re
import sys
from dataclasses import dataclass


# TOKEN

@dataclass
class Token:
    type: str
    value: str
    line: int

    def __repr__(self):
        return f"[{self.type}: {self.value}]"



# PHASE 1: LEXICAL ANALYZER


class Lexer:
    KEYWORDS = {"int", "float", "if", "while", "return"}

    TOKEN_SPECIFICATION = [
        ("FLOAT",      r"\d+\.\d+"),
        ("INTEGER",    r"\d+"),
        ("IDENTIFIER", r"[A-Za-z][A-Za-z0-9]*"),
        ("OPERATOR",   r"[=+\-<>]"),
        ("SYMBOL",     r"[{}();]"),
        ("NEWLINE",    r"\n"),
        ("WHITESPACE", r"[ \t\r]+"),
        ("MISMATCH",   r"."),
    ]

    def __init__(self, source_code):
        self.source_code = source_code
        self.tokens = []
        self.errors = []

    def tokenize(self):
        pattern = "|".join(
            f"(?P<{name}>{regex})"
            for name, regex in self.TOKEN_SPECIFICATION
        )

        line = 1

        for match in re.finditer(pattern, self.source_code):
            token_type = match.lastgroup
            value = match.group()

            if token_type == "NEWLINE":
                line += 1
                continue

            if token_type == "WHITESPACE":
                continue

            if token_type == "MISMATCH":
                self.errors.append(
                    f"Lexical Error on line {line}: "
                    f"Unexpected character '{value}'"
                )
                continue

            if token_type == "IDENTIFIER" and value in self.KEYWORDS:
                token_type = "KEYWORD"

            elif token_type in ("FLOAT", "INTEGER"):
                token_type = "LITERAL"

            self.tokens.append(
                Token(token_type, value, line)
            )

        # EOF makes it easier for the parser to know when input ends.
        self.tokens.append(Token("EOF", "EOF", line))

        return self.tokens



# ABSTRACT SYNTAX TREE


@dataclass
class Program:
    statements: list


@dataclass
class Declaration:
    data_type: str
    identifier: str
    line: int


@dataclass
class Assignment:
    identifier: str
    expression: object
    line: int


@dataclass
class IfStatement:
    condition: object
    body: list
    line: int


@dataclass
class WhileLoop:
    condition: object
    body: list
    line: int


@dataclass
class BinaryExpression:
    left: object
    operator: str
    right: object
    line: int


@dataclass
class Identifier:
    name: str
    line: int


@dataclass
class Literal:
    value: str
    data_type: str
    line: int



# CUSTOM SYNTAX ERROR


class CodeGuardSyntaxError(Exception):
    pass



# PHASE 2: PARSER
# Recursive-Descent Parser


class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.errors = []

    def current(self):
        return self.tokens[self.position]

    def advance(self):
        token = self.current()

        if self.position < len(self.tokens) - 1:
            self.position += 1

        return token

    def match(self, token_type=None, value=None):
        token = self.current()

        if token_type is not None and token.type != token_type:
            return False

        if value is not None and token.value != value:
            return False

        return True

    def expect(self, token_type=None, value=None):
        token = self.current()

        if not self.match(token_type, value):

            expected = value if value else token_type

            raise CodeGuardSyntaxError(
                f"Syntax Error on line {token.line}: "
                f"Expected '{expected}', "
                f"but found '{token.value}'"
            )

        return self.advance()


    # Program -> StatementList


    def parse(self):
        statements = []

        while not self.match("EOF"):

            try:
                statement = self.parse_statement()

                if statement is not None:
                    statements.append(statement)

            except CodeGuardSyntaxError as error:
                self.errors.append(str(error))
                self.synchronize()

        return Program(statements)

    # Statement


    def parse_statement(self):
        token = self.current()

        # Declaration
        if token.type == "KEYWORD" and token.value in ("int", "float"):
            return self.parse_declaration()

        # If statement
        if token.type == "KEYWORD" and token.value == "if":
            return self.parse_if()

        # While loop
        if token.type == "KEYWORD" and token.value == "while":
            return self.parse_while()

        # Assignment
        if token.type == "IDENTIFIER":
            return self.parse_assignment()

        raise CodeGuardSyntaxError(
            f"Syntax Error on line {token.line}: "
            f"Unexpected token '{token.value}'"
        )

  
    # Declaration -> DataType Identifier ";"


    def parse_declaration(self):

        data_type = self.advance()

        identifier = self.expect("IDENTIFIER")

        self.expect("SYMBOL", ";")

        return Declaration(
            data_type.value,
            identifier.value,
            data_type.line
        )

    # Assignment -> Identifier "=" Expression ";"


    def parse_assignment(self):

        identifier = self.expect("IDENTIFIER")

        self.expect("OPERATOR", "=")

        expression = self.parse_expression()

        self.expect("SYMBOL", ";")

        return Assignment(
            identifier.value,
            expression,
            identifier.line
        )


    # IfStatement ->
    # "if" "(" Condition ")" "{" StatementList "}"


    def parse_if(self):

        if_token = self.expect("KEYWORD", "if")

        self.expect("SYMBOL", "(")

        condition = self.parse_condition()

        self.expect("SYMBOL", ")")

        self.expect("SYMBOL", "{")

        body = self.parse_block()

        return IfStatement(
            condition,
            body,
            if_token.line
        )

  
    # WhileLoop ->
    # "while" "(" Condition ")" "{" StatementList "}"
 

    def parse_while(self):

        while_token = self.expect("KEYWORD", "while")

        self.expect("SYMBOL", "(")

        condition = self.parse_condition()

        self.expect("SYMBOL", ")")

        self.expect("SYMBOL", "{")

        body = self.parse_block()

        return WhileLoop(
            condition,
            body,
            while_token.line
        )


    # Parse statements inside { ... }


    def parse_block(self):

        statements = []

        while not self.match("SYMBOL", "}"):

            if self.match("EOF"):
                token = self.current()

                raise CodeGuardSyntaxError(
                    f"Syntax Error on line {token.line}: "
                    "Expected '}' before end of file"
                )

            statement = self.parse_statement()
            statements.append(statement)

        self.expect("SYMBOL", "}")

        return statements

   
    # Condition ->
    # Expression ("<" | ">") Expression
   

    def parse_condition(self):

        left = self.parse_expression()

        operator = self.current()

        if not (
            operator.type == "OPERATOR"
            and operator.value in ("<", ">")
        ):
            raise CodeGuardSyntaxError(
                f"Syntax Error on line {operator.line}: "
                "Expected '<' or '>' in condition"
            )

        self.advance()

        right = self.parse_expression()

        return BinaryExpression(
            left,
            operator.value,
            right,
            operator.line
        )


    # Expression -> Term (("+" | "-") Term)*


    def parse_expression(self):

        expression = self.parse_term()

        while (
            self.current().type == "OPERATOR"
            and self.current().value in ("+", "-")
        ):

            operator = self.advance()

            right = self.parse_term()

            expression = BinaryExpression(
                expression,
                operator.value,
                right,
                operator.line
            )

        return expression

    # Term -> Identifier | Literal


    def parse_term(self):

        token = self.current()

        if token.type == "IDENTIFIER":

            self.advance()

            return Identifier(
                token.value,
                token.line
            )

        if token.type == "LITERAL":

            self.advance()

            if "." in token.value:
                data_type = "float"
            else:
                data_type = "int"

            return Literal(
                token.value,
                data_type,
                token.line
            )

        raise CodeGuardSyntaxError(
            f"Syntax Error on line {token.line}: "
            f"Expected identifier or literal, "
            f"but found '{token.value}'"
        )

  
    # Error Recovery
    # Skip tokens until a likely statement boundary.


    def synchronize(self):

        while not self.match("EOF"):

            if self.match("SYMBOL", ";"):
                self.advance()
                return

            if self.match("SYMBOL", "}"):
                self.advance()
                return

            self.advance()



# PHASE 3: SEMANTIC ANALYZER


class SemanticAnalyzer:

    def __init__(self):

        # Stack of dictionaries.
        #
        # Example:
        #
        # [
        #     {"x": "int"},
        #     {"y": "float"}
        # ]
        #
        # First dictionary = global scope
        # Last dictionary = current scope

        self.scopes = [{}]

        self.errors = []


    # Scope Management


    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        self.scopes.pop()


    # Symbol Table Operations


    def declare(self, name, data_type, line):

        current_scope = self.scopes[-1]

        if name in current_scope:

            self.errors.append(
                f"Semantic Error on line {line}: "
                f"Variable '{name}' is already declared "
                "in this scope."
            )

            return

        current_scope[name] = data_type

    def lookup(self, name):

        # Search from innermost scope outward.
        for scope in reversed(self.scopes):

            if name in scope:
                return scope[name]

        return None


    # Main analysis


    def analyze(self, program):

        for statement in program.statements:
            self.analyze_statement(statement)

    # Statement Analysis


    def analyze_statement(self, statement):

        if isinstance(statement, Declaration):

            self.declare(
                statement.identifier,
                statement.data_type,
                statement.line
            )

        elif isinstance(statement, Assignment):

            self.analyze_assignment(statement)

        elif isinstance(statement, IfStatement):

            self.analyze_expression(statement.condition)

            self.enter_scope()

            for child in statement.body:
                self.analyze_statement(child)

            self.exit_scope()

        elif isinstance(statement, WhileLoop):

            self.analyze_expression(statement.condition)

            self.enter_scope()

            for child in statement.body:
                self.analyze_statement(child)

            self.exit_scope()


    # Assignment Analysis


    def analyze_assignment(self, assignment):

        variable_type = self.lookup(
            assignment.identifier
        )

        # Declared-before-use
        if variable_type is None:

            self.errors.append(
                f"Semantic Error on line {assignment.line}: "
                f"Variable '{assignment.identifier}' "
                "was used before declaration."
            )

            # Still inspect the expression for other errors.
            self.analyze_expression(assignment.expression)

            return

        expression_type = self.analyze_expression(
            assignment.expression
        )

        if expression_type is None:
            return

        # Type consistency
        if variable_type != expression_type:

            self.errors.append(
                f"Semantic Error on line {assignment.line}: "
                f"Cannot assign value of type "
                f"'{expression_type}' to variable "
                f"'{assignment.identifier}' of type "
                f"'{variable_type}'."
            )

    # Expression Analysis


    def analyze_expression(self, expression):

        # Literal
        if isinstance(expression, Literal):
            return expression.data_type

        # Identifier
        if isinstance(expression, Identifier):

            variable_type = self.lookup(
                expression.name
            )

            if variable_type is None:

                self.errors.append(
                    f"Semantic Error on line {expression.line}: "
                    f"Variable '{expression.name}' "
                    "was used before declaration "
                    "or is outside its scope."
                )

                return None

            return variable_type

        # Binary expression
        if isinstance(expression, BinaryExpression):

            left_type = self.analyze_expression(
                expression.left
            )

            right_type = self.analyze_expression(
                expression.right
            )

            if left_type is None or right_type is None:
                return None

            if left_type != right_type:

                self.errors.append(
                    f"Semantic Error on line {expression.line}: "
                    f"Type mismatch between "
                    f"'{left_type}' and '{right_type}'."
                )

                return None

            # Relational expressions conceptually produce
            # a boolean result, although bool is not part
            # of the defined C-subset.
            if expression.operator in ("<", ">"):
                return "bool"

            return left_type

        return None



# AST DISPLAY


def print_ast(node, indent=0):

    spacing = "  " * indent

    if isinstance(node, Program):

        print(spacing + "Program")

        for statement in node.statements:
            print_ast(statement, indent + 1)

    elif isinstance(node, Declaration):

        print(
            spacing
            + f"Declaration(type={node.data_type}, "
            + f"name={node.identifier})"
        )

    elif isinstance(node, Assignment):

        print(
            spacing
            + f"Assignment(name={node.identifier})"
        )

        print_ast(node.expression, indent + 1)

    elif isinstance(node, IfStatement):

        print(spacing + "IfStatement")

        print(spacing + "  Condition:")

        print_ast(node.condition, indent + 2)

        print(spacing + "  Body:")

        for statement in node.body:
            print_ast(statement, indent + 2)

    elif isinstance(node, WhileLoop):

        print(spacing + "WhileLoop")

        print(spacing + "  Condition:")

        print_ast(node.condition, indent + 2)

        print(spacing + "  Body:")

        for statement in node.body:
            print_ast(statement, indent + 2)

    elif isinstance(node, BinaryExpression):

        print(
            spacing
            + f"BinaryExpression({node.operator})"
        )

        print_ast(node.left, indent + 1)
        print_ast(node.right, indent + 1)

    elif isinstance(node, Identifier):

        print(
            spacing
            + f"Identifier({node.name})"
        )

    elif isinstance(node, Literal):

        print(
            spacing
            + f"Literal({node.value}: {node.data_type})"
        )


# ============================================================
# CODEGUARD DRIVER
# ============================================================

def analyze_code(source_code):

    print("=" * 60)
    print("CODEGUARD - STATIC ANALYZER FOR A C-SUBSET")
    print("=" * 60)

    # --------------------------------------------------------
    # Phase 1: Lexical Analysis
    # --------------------------------------------------------

    print("\nPHASE 1: LEXICAL ANALYSIS")
    print("-" * 60)

    lexer = Lexer(source_code)

    tokens = lexer.tokenize()

    if lexer.errors:

        for error in lexer.errors:
            print(error)

        print("\nAnalysis stopped due to lexical errors.")
        return

    for token in tokens:

        if token.type != "EOF":
            print(
                f"Line {token.line}: "
                f"[{token.type}: {token.value}]"
            )

    print("\nLexical analysis successful.")

    
    # Phase 2: Syntax Analysis


    print("\nPHASE 2: SYNTAX ANALYSIS")
    print("-" * 60)

    parser = Parser(tokens)

    program = parser.parse()

    if parser.errors:

        for error in parser.errors:
            print(error)

        print("\nSyntax analysis found errors.")
        return

    print("Syntax analysis successful.")

    # --------------------------------------------------------
    # AST
    # --------------------------------------------------------

    print("\nABSTRACT SYNTAX TREE")
    print("-" * 60)

    print_ast(program)


    # Phase 3: Semantic Analysis
  

    print("\nPHASE 3: SEMANTIC ANALYSIS")
    print("-" * 60)

    analyzer = SemanticAnalyzer()

    analyzer.analyze(program)

    if analyzer.errors:

        for error in analyzer.errors:
            print(error)

        print("\nSemantic analysis found errors.")

    else:

        print("Semantic analysis successful.")

    # Final Report
 
    print("\n" + "=" * 60)
    print("CODEGUARD ANALYSIS SUMMARY")
    print("=" * 60)

    total_errors = (
        len(lexer.errors)
        + len(parser.errors)
        + len(analyzer.errors)
    )

    if total_errors == 0:

        print(
            "RESULT: PASSED\n"
            "No lexical, syntax, or semantic errors detected."
        )

    else:

        print(
            f"RESULT: FAILED\n"
            f"Total errors detected: {total_errors}"
        )



# FILE INPUT


def main():

    if len(sys.argv) != 2:

        print("Usage:")
        print("    python codeguard.py <source_file>")
        print("\nExample:")
        print("    python codeguard.py test.cg")

        return

    filename = sys.argv[1]

    try:

        with open(filename, "r", encoding="utf-8") as file:
            source_code = file.read()

    except FileNotFoundError:

        print(
            f"Error: File '{filename}' was not found."
        )

        return

    analyze_code(source_code)


if __name__ == "__main__":
    main()