from ParseTree import *

class CompilerParser :

    def __init__(self,tokens):
        """
        Constructor for the CompilerParser
        @param tokens A list of tokens to be parsed
        """
        self.tokens = tokens
        self.current_token = 0
    

    def compileProgram(self):
        """
        Generates a parse tree for a single program
        @return a ParseTree that represents the program
        """
        if not self.tokens:
            raise ParseException("No tokens to parse")
        
        if self.have('keyword', 'class'):
            return self.compileClass()
        else:
            raise ParseException("The program doesn't begin with keyword class")
    
    
    def compileClass(self):
        """
        Generates a parse tree for a single class
        @return a ParseTree that represents a class
        """
        if not self.have('keyword', 'class'):
            raise ParseException("The class declaration doesn't begin with a class")
    
        tree = ParseTree('class', '')
        # class keyword
        tree.addChild(self.mustBe('keyword', 'class'))
        
        # className (identifier)
        class_name = self.current().getValue()
        tree.addChild(self.mustBe('identifier', class_name))
        
        # Opening brace
        tree.addChild(self.mustBe("symbol", "{"))

        # classVarDec
        while self.have('keyword', 'static'):
            VarDec = self.compileClassVarDec()
            tree.addChild(VarDec)

        # subroutineDec
        while self.have('keyword', ['constructor', 'function', 'method']):
            Subroutine = self.compileSubroutine()
            tree.addChild(Subroutine)
        
        # Closing brace
        tree.addChild(self.mustBe('symbol', '}'))
        
        return tree 
    

    def compileClassVarDec(self):
        """
        Generates a parse tree for a static variable declaration or field declaration
        @return a ParseTree that represents a static variable declaration or field declaration
        """
        tree = ParseTree('classVarDec', '')

        # variable declaration - can be either 'static' or 'field'
        if self.have('keyword', 'static'):
            tree.addChild(self.mustBe('keyword', 'static'))
        elif self.have('keyword', 'field'):
            tree.addChild(self.mustBe('keyword', 'field'))
        else:
            raise ParseException("Class variable declaration must begin with 'static' or 'field'")
        
        # type
        classVar_type = self.current().getValue()
        if classVar_type in ['int', 'char', 'boolean']:
            tree.addChild(self.mustBe('keyword', classVar_type))
        else:
            tree.addChild(self.mustBe('identifier', classVar_type))
        
        # varName
        classVar_name = self.current().getValue()
        tree.addChild(self.mustBe('identifier', classVar_name))
        
        # Handle multiple variable names (separated by commas)
        while self.have('symbol', ','):
            tree.addChild(self.mustBe('symbol', ','))
            var_name = self.current().getValue()
            tree.addChild(self.mustBe('identifier', var_name))
        
        # Semicolon
        tree.addChild(self.mustBe('symbol', ';'))
        
        return tree
    

    def compileSubroutine(self):
        """
        Generates a parse tree for a method, function, or constructor
        @return a ParseTree that represents the method, function, or constructor
        """
        tree = ParseTree('subroutine', '')

        # subroutine declaration
        sub_dec = self.current().getValue()
        if sub_dec in ['constructor', 'method', 'function']:
            tree.addChild(self.mustBe('keyword', sub_dec))
        else:
            raise ParseException("The subroutine doesn't start with constructor, function or method")
        
        # subroutine type
        sub_type = self.current().getValue()
        if sub_type in ['void', 'int', 'char', 'boolean']:
            tree.addChild(self.mustBe('keyword', sub_type))
        else:
            tree.addChild(self.mustBe('identifier', sub_type))
        
        # subroutine identifier
        sub_name = self.current().getValue()
        tree.addChild(self.mustBe('identifier', sub_name))

        # open parenthesis
        tree.addChild(self.mustBe('symbol', '('))

        # ParameterList
        tree.addChild(self.compileParameterList())

        # closed parenthesis
        tree.addChild(self.mustBe('symbol', ')'))

        # Compile statements or variable declarations inside the subroutine body
        # Compile subroutine body
        SubroutineBody = self.compileSubroutineBody()
        if SubroutineBody is not None:
            tree.addChild(SubroutineBody)
    
        return tree
    
    
    def compileParameterList(self):
        """
        Generates a parse tree for a subroutine's parameters
        @return a ParseTree that represents a subroutine's parameters
        """
        tree = ParseTree('parameterList', '')

        # Check for empty parameter list
        if self.have('symbol', ')'):
            return tree
        
        param_type = self.current().getValue()
        if param_type in ['int', 'char', 'boolean']:
            tree.addChild(self.mustBe('keyword', param_type))
        else:
            tree.addChild(self.mustBe('identifier', param_type))

        param_name = self.current().getValue()
        tree.addChild(self.mustBe('identifier', param_name))

        while self.have('symbol', ','):
            tree.addChild(self.mustBe('symbol', ','))

            param_type = self.current().getValue()
            if param_type in ['int', 'char', 'boolean']:
                tree.addChild(self.mustBe('keyword', param_type))
            else:
                tree.addChild(self.mustBe('identifier', param_type))

            param_name = self.current().getValue()
            tree.addChild(self.mustBe('identifier', param_name))

        return tree
    
    
    def compileSubroutineBody(self):
        """
        Generates a parse tree for a subroutine's body
        @return a ParseTree that represents a subroutine's body
        """
        tree = ParseTree('subroutineBody', '')

        # Opening brace
        tree.addChild(self.mustBe('symbol', '{'))

        # Variable declarations
        while True:
            varDec = self.compileVarDec()
            if varDec is None:
                break
            tree.addChild(varDec)

        # Statements (if you have a compileStatements method)
        if hasattr(self, 'compileStatements'):
            statements = self.compileStatements()
            if statements is not None:
                tree.addChild(statements)

        # Closing brace
        tree.addChild(self.mustBe('symbol', '}'))

        return tree
        
    
    def compileVarDec(self):
        """
        Generates a parse tree for a variable declaration
        @return a ParseTree that represents a var declaration
        """
        if not self.have('keyword', 'var'):
            return None
        
        tree = ParseTree('varDec', '')

        # 'var' keyword
        tree.addChild(self.mustBe('keyword', 'var'))

        # Type can be either a primitive type (keyword) or class type (identifier)
        var_type = self.current().getValue()
        if var_type in ['int', 'char', 'boolean']:
            tree.addChild(self.mustBe('keyword', var_type))
        else:
            tree.addChild(self.mustBe('identifier', var_type))

        # Variable name
        var_name = self.current().getValue()
        tree.addChild(self.mustBe('identifier', var_name))

        # Handle multiple variable names (separated by commas)
        while self.have('symbol', ','):
            tree.addChild(self.mustBe('symbol', ','))
            var_name = self.current().getValue()
            tree.addChild(self.mustBe('identifier', var_name))

        # Semicolon
        tree.addChild(self.mustBe('symbol', ';'))

        return tree
        

    def compileStatements(self):
        """
        Generates a parse tree for a series of statements
        @return a ParseTree that represents the series of statements
        """
        tree = ParseTree('statements', '')
    
        # Continue processing statements until we reach a closing brace or end of tokens
        while True:
            # Check for each type of statement and compile accordingly
            if self.have('keyword', 'let'):
                tree.addChild(self.compileLet())
            elif self.have('keyword', 'if'):
                tree.addChild(self.compileIf())
            elif self.have('keyword', 'while'):
                tree.addChild(self.compileWhile())
            elif self.have('keyword', 'do'):
                tree.addChild(self.compileDo())
            elif self.have('keyword', 'return'):
                tree.addChild(self.compileReturn())
            else:
                # No more statements to process
                break
        
        return tree
    
    
    def compileLet(self):
        """
        Generates a parse tree for a let statement
        @return a ParseTree that represents the statement
        """
        tree = ParseTree('letStatement', '')
    
        # let keyword
        tree.addChild(self.mustBe('keyword', 'let'))
        
        # Variable name
        var_name = self.current().getValue()
        tree.addChild(self.mustBe('identifier', var_name))
        
        # Check for array indexing
        if self.have('symbol', '['):
            tree.addChild(self.mustBe('symbol', '['))
            tree.addChild(self.compileExpression())
            tree.addChild(self.mustBe('symbol', ']'))
        
        # Equals sign
        tree.addChild(self.mustBe('symbol', '='))
        
        # Expression (or skip keyword for testing)
        if self.have('keyword', 'skip'):
            tree.addChild(self.mustBe('keyword', 'skip'))
        else:
            tree.addChild(self.compileExpression())
        
        # Semicolon
        tree.addChild(self.mustBe('symbol', ';'))
        
        return tree

    def compileIf(self):
        """
        Generates a parse tree for an if statement
        @return a ParseTree that represents the statement
        """
        tree = ParseTree("ifStatement", "")
        
        # if keyword
        tree.addChild(self.mustBe("keyword", "if"))
        
        # Opening parenthesis
        tree.addChild(self.mustBe("symbol", "("))
        
        # Condition
        tree.addChild(self.compileExpression())
        
        # Closing parenthesis
        tree.addChild(self.mustBe("symbol", ")"))
        
        # Opening brace
        tree.addChild(self.mustBe("symbol", "{"))
        
        # If statements
        tree.addChild(self.compileStatements())
        
        # Closing brace
        tree.addChild(self.mustBe("symbol", "}"))
        
        # Optional else clause
        if self.have("keyword", "else"):
            tree.addChild(self.mustBe("keyword", "else"))
            tree.addChild(self.mustBe("symbol", "{"))
            tree.addChild(self.compileStatements())
            tree.addChild(self.mustBe("symbol", "}"))
        
        return tree

    
    def compileWhile(self):
        """
        Generates a parse tree for a while statement
        @return a ParseTree that represents the statement
        """
        tree = ParseTree("whileStatement", "")
        
        # while keyword
        tree.addChild(self.mustBe("keyword", "while"))
        
        # Opening parenthesis
        tree.addChild(self.mustBe("symbol", "("))
        
        # Condition
        tree.addChild(self.compileExpression())
        
        # Closing parenthesis
        tree.addChild(self.mustBe("symbol", ")"))
        
        # Opening brace
        tree.addChild(self.mustBe("symbol", "{"))
        
        # Statements
        tree.addChild(self.compileStatements())
        
        # Closing brace
        tree.addChild(self.mustBe("symbol", "}"))
        
        return tree


    def compileDo(self):
        """
        Generates a parse tree for a do statement
        @return a ParseTree that represents the statement
        """
        tree = ParseTree("doStatement", "")
        
        # do keyword
        tree.addChild(self.mustBe("keyword", "do"))
        
        # Expression (subroutineCall)
        tree.addChild(self.compileExpression())
        
        # Semicolon
        tree.addChild(self.mustBe("symbol", ";"))
        
        return tree


    def compileReturn(self):
        """
        Generates a parse tree for a return statement
        @return a ParseTree that represents the statement
        """
        tree = ParseTree("returnStatement", "")
        
        # return keyword
        tree.addChild(self.mustBe("keyword", "return"))
        
        # Optional expression
        if not self.have("symbol", ";"):
            tree.addChild(self.compileExpression())
        
        # Semicolon
        tree.addChild(self.mustBe("symbol", ";"))
        
        return tree


    def compileExpression(self):
        """
        Generates a parse tree for an expression
        @return a ParseTree that represents the expression
        """
        tree = ParseTree('expression', '')
    
        # Handle special case of 'skip' keyword
        if self.have('keyword', 'skip'):
            tree.addChild(self.mustBe('keyword', 'skip'))
            return tree
        
        # Handle regular expression: term (op term)*
        tree.addChild(self.compileTerm())
        
        # Check for operators and additional terms
        operators = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
        while self.current_token < len(self.tokens) and self.current().getType() == 'symbol' and self.current().getValue() in operators:
            tree.addChild(self.mustBe('symbol', self.current().getValue()))
            tree.addChild(self.compileTerm())
        
        return tree

    def compileTerm(self):
        """
        Generates a parse tree for an expression term
        @return a ParseTree that represents the expression term
        """
        tree = ParseTree('term', '')
        current = self.current()
        
        # Handle different types of terms
        if current.getType() == 'integerConstant':
            tree.addChild(self.mustBe('integerConstant', current.getValue()))
        
        elif current.getType() == 'stringConstant':
            tree.addChild(self.mustBe('stringConstant', current.getValue()))
        
        elif current.getType() == 'keyword' and current.getValue() in ['true', 'false', 'null', 'this']:
            tree.addChild(self.mustBe('keyword', current.getValue()))
        
        elif current.getType() == 'symbol' and current.getValue() == '(':
            # Handle parenthesized expression
            tree.addChild(self.mustBe('symbol', '('))
            tree.addChild(self.compileExpression())
            tree.addChild(self.mustBe('symbol', ')'))
        
        elif current.getType() == 'symbol' and current.getValue() in ['-', '~']:
            # Handle unary operators
            tree.addChild(self.mustBe('symbol', current.getValue()))
            tree.addChild(self.compileTerm())
        
        elif current.getType() == 'identifier':
            # This could be a variable name, array access, or subroutine call
            tree.addChild(self.mustBe('identifier', current.getValue()))
            
            if self.current_token < len(self.tokens):
                if self.have('symbol', '['):
                    # Array access
                    tree.addChild(self.mustBe('symbol', '['))
                    tree.addChild(self.compileExpression())
                    tree.addChild(self.mustBe('symbol', ']'))
                elif self.have('symbol', '('):
                    # Subroutine call
                    tree.addChild(self.mustBe('symbol', '('))
                    tree.addChild(self.compileExpressionList())
                    tree.addChild(self.mustBe('symbol', ')'))
                elif self.have('symbol', '.'):
                    # Method call
                    tree.addChild(self.mustBe('symbol', '.'))
                    tree.addChild(self.mustBe('identifier', self.current().getValue()))
                    tree.addChild(self.mustBe('symbol', '('))
                    tree.addChild(self.compileExpressionList())
                    tree.addChild(self.mustBe('symbol', ')'))
        
        return tree 


    def compileExpressionList(self):
        """
        Generates a parse tree for an expression list
        @return a ParseTree that represents the expression list
        """
        tree = ParseTree('expressionList', '')
    
        # Empty expression list
        if self.have('symbol', ')'):
            return tree
        
        # First expression
        tree.addChild(self.compileExpression())
        
        # Handle additional expressions separated by commas
        while self.have('symbol', ','):
            tree.addChild(self.mustBe('symbol', ','))
            tree.addChild(self.compileExpression())
        
        return tree


    def next(self):
        """
        Advance to the next token
        """
        self.current_token += 1
        return


    def current(self):
        """
        Return the current token
        @return the token
        """
        if self.current_token < len(self.tokens):
            return self.tokens[self.current_token]
        else:
            raise ParseException("No more token to parse!")


    def have(self,expectedType,expectedValue):
        """
        Check if the current token matches the expected type and value.
        @return True if a match, False otherwise
        """
        try:
            current = self.current()
            if isinstance(expectedValue, (list, tuple)):
                return current.getType() == expectedType and current.getValue() in expectedValue
            return current.getType() == expectedType and current.getValue() == expectedValue
        except ParseException:
            return False


    def mustBe(self,expectedType,expectedValue):
        """
        Check if the current token matches the expected type and value.
        If so, advance to the next token, returning the current token, otherwise throw/raise a ParseException.
        @return token that was current prior to advancing.
        """
        current = self.current()
        if self.have(expectedType, expectedValue):
            self.next()
            return current
        else:
            raise ParseException(f"Expected {expectedType}:{expectedValue}, got {current.getType()}:{current.getValue()}")
    

if __name__ == "__main__":


    """ 
    Tokens for:
        class Main {
            static int a ;

            function void myFunc
            ( int a ) {

                var int a ;

                let a = skip;

                do skip;

                if (skip) {
                } else {
                }

                while (skip) {
                }

                return skip;
            }

            1 + (a - b) 
        }
    """
    tokens = []
    tokens.append(Token("keyword","class"))
    tokens.append(Token("identifier","Main"))
    tokens.append(Token("symbol","{"))

    tokens.append(Token("keyword","static"))
    tokens.append(Token("keyword","int"))
    tokens.append(Token("identifier","a"))
    tokens.append(Token("symbol",";"))

    tokens.append(Token("keyword","function"))
    tokens.append(Token("keyword","void"))
    tokens.append(Token("identifier","myFunc"))
    tokens.append(Token("symbol","("))
    tokens.append(Token("keyword","int"))
    tokens.append(Token("identifier","a"))
    tokens.append(Token("symbol",")"))
    tokens.append(Token("symbol","{"))

    tokens.append(Token("keyword","var"))
    tokens.append(Token("keyword","int"))
    tokens.append(Token("identifier","a"))
    tokens.append(Token("symbol",";"))

    tokens.append(Token("keyword","let"))
    tokens.append(Token("identifier","a"))
    tokens.append(Token("symbol","="))
    tokens.append(Token("keyword","skip"))
    tokens.append(Token("symbol",";"))

    tokens.append(Token("keyword","do"))
    tokens.append(Token("keyword","skip"))
    tokens.append(Token("symbol",";"))

    tokens.append(Token("keyword","if"))
    tokens.append(Token("symbol","("))
    tokens.append(Token("keyword","skip"))
    tokens.append(Token("symbol",")"))
    tokens.append(Token("symbol","{"))
    tokens.append(Token("symbol","}"))
    tokens.append(Token("keyword","else"))
    tokens.append(Token("symbol","{"))
    tokens.append(Token("symbol","}"))

    tokens.append(Token("keyword","while"))
    tokens.append(Token("symbol","("))
    tokens.append(Token("keyword","skip"))
    tokens.append(Token("symbol",")"))
    tokens.append(Token("symbol","{"))
    tokens.append(Token("symbol","}"))

    tokens.append(Token("keyword","return"))
    tokens.append(Token("keyword","skip"))
    tokens.append(Token("symbol",";"))

    tokens.append(Token("symbol","}"))

    tokens.append(Token("symbol","}"))

    parser = CompilerParser(tokens)
    try:
        result = parser.compileProgram()
        print(result)
    except ParseException:
        print("Error Parsing!")