# -*- coding: utf-8 -*-
"""
 This file is part of PyBexpp.

 PyBexpp is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 PyBexpp is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with PyBexpp.  If not, see <http://www.gnu.org/licenses/>.
"""

from enum import Enum
import sys

#Antes de nada, comprobar la versión de Python actual (Requerida 2.7)
if sys.version_info[0] != 2 or sys.version_info[1] < 7:
    raise SystemError("This script requires Python 2.7. Current Python version: %d.%d" \
    % (sys.version_info[0], sys.version_info[1]))
    

class ParseError(Exception):
    pass

class Operators(Enum):
    NONE = (0, 1)
    NOT = (1, 1)
    XOR = (2, 2)
    AND = (3, 2)
    OR = (4, 2)
    
    def __init__(self, id, operc):
        self.id = id
        self.operc = operc
        
    def __lt__(self, other):
        return self.id < other.id
            
    def __le__(self, other):
        return self.id <= other.id
        
    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id
        
    def __gt__(self, other):
        return self.id > other.id
        
    def __ge__(self, other):
        return self.id >= other.id

class Operation(object):
    def __init__(self, operator, operands):
        self.operator = operator
        self.operands = operands
    
    def eval(self, variables):
        values = []
        for operand in self.operands:
            if isinstance(operand, basestring):
                val = False
                if operand == '0':
                    val = False
                elif operand == '1':
                    val = True
                else:
                    if not variables.has_key(operand):
                        raise KeyError("Value not defined for variable %c" % operand)
                    val = variables[operand]
                    if val == 0:
                        val = False
                    elif val == 1:
                        val = True
                    if not isinstance(val, bool):
                        raise TypeError("Expected boolean value for variable %c" % operand)
                values.append(val)
            else:
                values.append(operand.eval(variables))
                
        if self.operator == Operators.NONE:
            return values[0]
        if self.operator == Operators.NOT:
            return not values[0]
        if self.operator == Operators.XOR:
            return values[0] ^ values[1]
        if self.operator == Operators.AND:
            return values[0] and values[1]
        if self.operator == Operators.OR:
            return values[0] or values[1]

    def truth_set(self, variables):
        vcount = len(variables)
        vrange = range(0, vcount)
        mx = pow(2, vcount)
        st = set()
        dvars = {}

        for i in range(0, mx):
            for j in vrange:
                value = (i >> (vcount - j - 1)) & 1
                dvars[variables[j]] = value
            if self.eval(dvars) == True:
                truthe = ""
                for j in vrange:
                    if dvars[variables[j]] == 1:
                        truthe += '1'
                    else:
                        truthe += '0'
                st.add(truthe)
        return st
    
    def polish_notation(self, beautify = False):
        s = ""
        if self.operator == Operators.NOT:
            s += '~'
        elif self.operator == Operators.XOR:
            s += '^'
        elif self.operator == Operators.AND:
            s += '*'
        elif self.operator == Operators.OR:
            s += '+'

        if self.operator != Operators.NONE:
            if beautify:
                s += "( "
            else:
                s += " "
        
        first = True
        for operand in self.operands:
            if first:
                first = False
            elif beautify:
                s += ", "
            else:
                s += " "
            if isinstance(operand, basestring):
                s += operand
            else:
                s += operand.polish_notation(beautify)
        if beautify and self.operator != Operators.NONE:
            s += " )"
        return s
        
    def __require_parenthesis(self, operand):
        return operand.operator > self.operator

    def __can_omit_and_operator(self, operand, alignment):
        if isinstance(operand, Operation):
            if self.__require_parenthesis(operand):
                return False;
            else:
                if alignment == 'left':
                    return self.__can_omit_and_operator(operand.operands[0], alignment)
                else:
                    return self.__can_omit_and_operator(operand.operands[len(operand.operands) - 1], alignment)
        else:
            return True

    def __str_operand(self, operand):
        s = ""
        if isinstance(operand, basestring):
            s += operand
        else:
            bracketsRequired = self.__require_parenthesis(operand)
            if bracketsRequired:
                s += "("
            s += operand.common_notation()
            if bracketsRequired:
                s += ")"
        return s

    def common_notation(self):
        s = ""
        s += self.__str_operand(self.operands[0])
        if self.operator == Operators.NOT:
            s += '\''
        elif self.operator == Operators.XOR:
            s += '^'
        elif self.operator == Operators.AND and \
             (not self.__can_omit_and_operator(self.operands[0], 'right') \
              or not self.__can_omit_and_operator(self.operands[1], 'left')):
            s += '*'
        elif self.operator == Operators.OR:
            s += '+'
        if self.operator.operc > 1:
            s += self.__str_operand(self.operands[1])
        return s;
            
def is_valid_var_name(ch):
    if len(ch) != 1:
        return False
    c = ord(ch)
    return (c >= ord('A') and c <= ord('Z')) or \
    (c >= ord('a') and c <= ord('z'))
    
def __clean_operand(buf, off, length):
    lastindex = off + length
    return buf[off:lastindex].replace(" ", "")
    
def __build_operand(buf, off, length):
    s = __clean_operand(buf, off, length)
    if len(s) < 1:
        raise ParseError("Expecting operand at offset %d" % off)
    if s == '0' or s == '1' or is_valid_var_name(s):
        return s;
    else:
        return parse_expr(buf, off, length)
        
def __check_operand_kind(buf, off, length):
    s = __clean_operand(buf, off, length)
    if len(s) < 1:
        raise ParseError("Expecting operand at offset %d" % off)
    if s == '0' or s == '1' or is_valid_var_name(s):
        return 'var'
    else:
        return 'op'
    
def parse_expr(buf, off = 0, length = -1):
    if not isinstance(off, int):
        raise TypeError("Expecting an int in parameter 'off'")
    if not isinstance(length, int):
        raise TypeError("Expecting an int in parameter 'length'")
    if not isinstance(buf, basestring):
        raise TypeError("Expecting an string in parameter 'buf'")

    foundOp = Operators.NONE
    opIndex = -1
    level = 0
    out = Operation(Operators.NONE, [])
    
    if length == -1:
        length = len(buf)
        
    #Ajustar offset y length para no tener en cuenta los espacios
    #iniciales y finales
    while buf[off] == ' ':
        off += 1;
        length -= 1;
    
    while buf[off + length - 1] == ' ':
        length -= 1;

    strlen = off + length

    #True si el último carácter (sin tener en cuenta las negaciones)
    #se correspondía a una variable
    lastWasVar = False

    for i in range(off, strlen):
        #Carácter actual
        c = buf[i]
        if c == '(':
            level += 1
        elif c == ')':
            if level == 0:
                raise ParseError("Unbalanced brackets at offset %d" % i)
            else:
                level -= 1
        elif c == '+':
            if level == 0 and foundOp < Operators.OR:
                foundOp = Operators.OR
                opIndex = i
        elif c == '*':
            if level == 0 and foundOp < Operators.AND:
                foundOp = Operators.AND
                opIndex = i
        elif c == '^':
            if level == 0 and foundOp < Operators.XOR:
                foundOp = Operators.XOR
                opIndex = i
        elif c == '\'':
            #IMPORTANTE EN EL NOT EL '<=': Al ser un operador
            #ubicado a la derecha de sus operandos, siempre se debe
            #tomar el que esté más a la derecha de la expresión.
            if level == 0 and foundOp <= Operators.NOT:
                foundOp = Operators.NOT
                opIndex = i
            continue
        elif (is_valid_var_name(c) or c == '0' or c == '1'):
            #Esto sucede cuando el programa encuentra algo tal que
            #a'b, que realmente es a' * b, pero con la multiplicación
            #omitida.
            if lastWasVar:
                if level == 0 and foundOp < Operators.AND:
                    foundOp = Operators.AND
                    opIndex = i
            else:
                lastWasVar = True
            continue
        elif c == ' ':
            continue
        else:
            raise ParseError("Unknown symbol %c at offset %d" % (c, i))
        lastWasVar = False
    
    if level > 0:
        raise ParseError("End of sequence reached while expecting ')'")
    
    if foundOp == Operators.NONE:
        #Si la expresión actual comienza por () y no se han encontrado
        #operaciones en este nivel, se analiza el siguiente nivel
        if buf[off] == '(' and buf[off+length-1] == ')':
            #Operación que empieza y termina con paréntesis, y no hay ningún otro
            #operador en este nivel.
            return parse_expr(buf, off + 1, length - 2)
        elif __check_operand_kind(buf, off, length) == 'var':
            #Si la expresión actual corresponde a una sola variable
            #devolvemos dicha variable
            return Operation(Operators.NONE, __build_operand(buf, off, length))
        else:
            #Si en el nivel actual no hemos encontrado ningún operando
            #y tampoco estamos ante una expresión que representa una sola
            #variable, debemos considerar que el usuario ha olvidado colocar
            #algún operador
            raise ParseError("Missing main operator in operand located at offset %d to %d" \
            % (off, strlen - 1))
    
    out.operator = foundOp
    if foundOp == Operators.NOT or foundOp == Operators.NONE:
        olen = 0
        if foundOp == Operators.NONE:
            olen = length
        else:
            if (opIndex != strlen - 1):
                #Un operador NOT debe de ser el último carácter en la expresión
                raise ParseError("Unexpected symbol after NOT operator at offset %d" % (opIndex + 1))
            olen = opIndex - off
        out.operands.append(__build_operand(buf, off, olen))
    else:
        len1 = opIndex - off
        off2 = 0
        
        if foundOp == Operators.AND and buf[opIndex] != '*':
            #Operador omitido
            off2 = opIndex
        else:
            #Operador explícito
            off2 = opIndex + 1
        len2 = strlen - off2
        
        out.operands.append(__build_operand(buf, off, len1))
        out.operands.append(__build_operand(buf, off2, len2))
    return out
