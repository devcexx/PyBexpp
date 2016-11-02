# PyBexpp

PyBexpp is a Python project that allows you to parse, represent and evaluate boolean expressions.

### Requirements

 - Python 2 (>=2.7)  **_Not compatible with Python 3_**

### Usage

The purpose of this library is to parse boolean expressions and then, work with them. To accomplish this, the function that should be invoked is called ```parse_expr```. This function will parse an expression contained in a string into a Operation object.

##### Allowed components in a expression
 - Parenthesis: used for change the default precedence of the operations.
   - `a * (b + c)` is equals to `ab + ac` and not `ab + c`
 - Constant values (0 and 1).
   - `a + 1` is equals to `1` and `a*1` is equals to `a`
 - Variables: a case sensitive character between `A-Z` and `a-z`, that can take different boolean values.
 - Operators: a symbol that represents an operation done between one or more operands. The allowed operators are, from most to less precedence:
   - `'` NOT [Unary]: negates the value of an operand. This operator is placed at the right of the operand. Example: `a'`, `(a+b)'`.
   - `^` Or Exclusive (XOr) [Binary]: Returns `1` only if one of the operators has the value `1`. Otherwise `0` is returned.
   - `*` And [Binary]: Returns `1` only if both operators are `1`. Otherwise `0` is returned.
   - `+` Or [Binary]: Returns `0` if both operators are `0`. Otherwise, it returns `1`. It can be omitted between variables or constants. So, the expression `ab` is equivalent to `a*b`; `10` is equivalent to `1*0` and `a1` is equivalent to `a*1`. But `(a + b)(a + c)` is an invalid expression.
##### Examples of valid expressions.
  - `ab+ac'`
  - `(a + b) * (a + cd)'`
  - `a + 0`
  - `a + 1b`
  - `a ^ bc`
  - `abcd + a'bc'd + abcd' + abc'd' + a'b'cd`

##### Working with expressions
First of all, you have to run a Python console. Open a Python terminal in the directory of PyBexpp. Once this is done, you have to import the functions from the file:
```
>>> from bexpp import *
```
Now, if we want to parse an expression into an Operation object, we can do:
```
>>> operation = parse_expr("(a + b) * (a + cd)'")
```

From the Operation object, we can print the function to the console, both in infix notation and the prefix notation:
```
>>> operation.common_notation()
"(a+b)*(a+c*d)'"
>>> operation.polish_notation()
'* + a b ~ + a * c d'
>>> operation.polish_notation(True) #True for beautifying the output with parenthesis and commas.
'*( +( a, b ), ~( +( a, *( c, d ) ) ) )'
```
Now, we can eval the function setting values for each variables:
```
>>> operation.eval({'a': 0, 'b': 1, 'c': 0, 'd': 0})
True
>>> operation.eval({'a': 0, 'b': 0, 'c': 0, 'd': 0})
False
```

Finally, we can compute the whole truth set for the expression. For this, we only have to pass to the function `truth_set` a list of the variables of the expression, so the script can return a truth set with the values of each variable in the same position as they was in the given variable list:

```
>>> operation.truth_set(['a','b','c','d'])
set(['0110', '0101', '0100'])
```

This results means:
```
f(a,b,c,d) = (a + b) * (a + cd)'
f(0,1,1,0) = 1
f(0,1,0,1) = 1
f(0,1,0,0) = 1
... and the value of f(a,b,c,d) will be zero in other case.
```
### License
This software is under the GNU GPL v3 license. This mean, in a nutshell, that you can freely use and distribute open source software that uses this library, but you cannot use it for commercial purposes or closed source projects. For more details about this license, please refer to the file `LICENSE` present in this repository.
