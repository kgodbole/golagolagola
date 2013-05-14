#
# version 1:
#   no nesting, only arithmetic operations and assignment,
#   dynamically typed, print and read, only integer values,
#   variable/tag names consist of only lowercase letters.
#
#       - implement the grammar
#           - arithmetic expression evaluator
#       - need a symbol table
#       - basic IO functionality for print and read
#

import sys
import string
import pprint
import logging
from pyparsing import Word, ZeroOrMore, ParseException, Or, Forward, Literal
from pyparsing import Keyword, StringEnd, operatorPrecedence, opAssoc, oneOf

#variable: string of lowercase characters
#number: integer
#operator: +,-,*,/
#
#term ->
#    variable |
#    number
#
#expression ->
#    term |
#    expression operator term
#
#assignment ->
#    variable '=' expression
#
#output ->
#    'print' expression
#
#input ->
#    'read' variable
#
#statement ->
#    assignment |
#    output |
#    input

logger = None
symbol_table = {}

def print_tree(s, loc, toks):
    global symbol_table, logger
    logger.debug("string:" + s)
    logger.debug("tokens:" + str(toks))
    logger.debug(pprint.pformat(symbol_table))
    logger.debug("\n")

def parse_expression(s, loc, tokens):
    logger.debug("parsing expression: tokens = " + str(tokens))
    global symbol_table
    [toks] = tokens
    vals = [str(get_value(tok)) if i % 2 == 0 else tok for i,tok in enumerate(toks)]
    return [eval("".join(vals))]

def get_value(var):
    global symbol_table
    try:
        val = int(var)
        return val
    except:
        if var not in symbol_table:
            raise Exception(var + " not defined")
        return symbol_table[var]

def parse_assignment_stmt(s, loc, tokens):
    global symbol_table
    var = tokens[0]
    value = tokens[2]
    symbol_table[var] = int(value)
    
def parse_output_stmt(s, loc, tokens):
    logger.debug("parsing output stmt: tokens = " + str(tokens))
    print get_value(tokens[1])

def parse_input_stmt(s, loc, tokens):
    logger.debug("parsing input stmt: tokens = " + str(tokens))
    line = sys.stdin.readline()
    symbol_table[tokens[1]] = int(line)


alphas = string.lowercase
digits = string.digits

add = Literal("+")
subtract = Literal("-")
multiply = Literal("*")
divide = Literal("/")
equals = Literal("=")

output_fn = Keyword("print")
input_fn = Keyword("read")

variable = Word(alphas)
number = Word(digits)
operator = Or([add, subtract, multiply, divide])

term = Or([variable, number])

#option 1: left recursion causes infinite recursion though
#expression = Forward()
#expression << Or([term, expression + operator + term])

#option 2: this works, but how to handle operator precedence
# ultimately, a list of tokens would be returned and then need to evaluate
# this list using a operator precedence aware stack
#expression = term + ZeroOrMore(operator + term)

#option 3: use pyparsing's operatorPrecedence function
# in this too, defining add_or_subtract and multiply_or_divide as follows
# does not work.
#multiply_or_divide = Or(multiply, divide)
#add_or_subtract = Or(add, subtract)
#
# parsing action can now be set separately for */ and +-
# this allows for evaluation of the expression while it is being parsed
#

expression = operatorPrecedence(term,
                [(oneOf("* /"), 2, opAssoc.LEFT, parse_expression),
                 (oneOf("+ -"), 2, opAssoc.LEFT, parse_expression)]
            )

assignment_stmt = variable + equals + expression + StringEnd()
assignment_stmt.setParseAction(parse_assignment_stmt)

output_stmt = output_fn + expression + StringEnd()
output_stmt.setParseAction(parse_output_stmt)

input_stmt = input_fn + term + StringEnd()
input_stmt.setParseAction(parse_input_stmt)

stmt = Or([assignment_stmt, input_stmt, output_stmt])
stmt.setParseAction(print_tree)

def parser_init():
    global symbol_table
    symbol_table = {}

def test_negative():
    parser_init()
    test_negative_string("x=1 +")
    test_negative_string("x==1 ** x /")
    test_negative_string("z 1 3 + 4")
    test_negative_string("z  =1 3 + 4")
    test_negative_string("z  =1 3 + 4;")

def test_negative_string(expr):
    try:
        stmt.parseString(expr)
    except:
        logger.debug("Unable to parse " + expr)

def test_positive():
    parser_init()
    stmt.parseString("x=1")
    stmt.parseString("y = x + 1")
    stmt.parseString("x =  1 +  4")
    stmt.parseString("x =  43 - 3")
    stmt.parseString("x =  32 *  4")
    stmt.parseString("x =  1 *  4 + 45")
    stmt.parseString("x =  0 *  4 + 45 * 5")
    stmt.parseString("x =  30/10")
    stmt.parseString("yyyy = 1 * 2 + 5 / 2 - 99")
    stmt.parseString("print 1")
    stmt.parseString("print 2  +3 + 888888888")
    stmt.parseString("read count")

def test_program():
    parser_init()
    stmt.parseString("x=1")
    stmt.parseString("y = 2")
    stmt.parseString("delta = 1")
    stmt.parseString("z = x * x + y * y")
    stmt.parseString("answer = z - delta")
    stmt.parseString("print x")
    stmt.parseString("print y")
    stmt.parseString("print z")
    stmt.parseString("print delta")
    stmt.parseString("print answer")

def test_program1():
    parser_init()
    stmt.parseString("read x")
    stmt.parseString("read y")
    stmt.parseString("print x * x + y * y")

def test_grammar():
    logger.debug("\nTesting grammar ...")
    #test_positive()
    #test_negative()
    test_program()
    #test_program1()

def logging_init():
    global logger
    logger = logging.getLogger('simple_example')
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler('gola.log')
    fh.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARN)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

logging_init()
test_grammar()
