"""
MIT License

Copyright (c) 2018 Samuel Wilder

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Contains several utilities for parsing with the Pyparsing library as well as
all of the parsers for all the compilers.
"""

from pyparsing import *
from red_utils import fix_hex_num


'''
Simple function to return a lambda to replace 'tokens' with 'replace'.

Usage:
>>> op_exponent = Literal('**').setParseAction(ReplaceWith('^'))
'''
ReplaceWith = lambda replace: lambda string, loc, tokens: replace


'''
Convenience function to shorten the syntax necessary to use the 'ReplaceWith'
lambda.

Usage A vs. B:
	A. op_exponent = Replace(Literal('**'), '^') # <- Way shorter
	B. op_exponent = Literal('**').setParseAction(ReplaceWith('^'))
'''
Replace = lambda parser, string: parser.setParseAction(ReplaceWith(string))

'''
Kills the storage specifiers of C integers because they cannot be compiled in
Red/System.
'''
IntegerSuffix = (
	CaselessLiteral('ui8').suppress()
	| CaselessLiteral('ui16').suppress()
	| CaselessLiteral('ui32').suppress()
	| CaselessLiteral('ui64').suppress()
	| CaselessLiteral('ull').suppress()
	| CaselessLiteral('ul').suppress()
	| CaselessLiteral('u').suppress()
	| CaselessLiteral('ll').suppress()
	| CaselessLiteral('l').suppress()
	| CaselessLiteral('i8').suppress()
	| CaselessLiteral('i16').suppress()
	| CaselessLiteral('i32').suppress()
	| CaselessLiteral('i64').suppress()
)

'''
Kills the storage specifiers of C floats because they cannot be compiled in
Red/System.
'''
FloatSuffix = (
	CaselessLiteral('f8').suppress()
	| CaselessLiteral('f16').suppress()
	| CaselessLiteral('f32').suppress()
	| CaselessLiteral('f64').suppress()
	| CaselessLiteral('f').suppress()
)

'''
Parses a hex literal and automatically changes it to the Red/System equivalent.
'''
HexNumber = Combine(
	Literal('0x') +
	Word(nums + 'abcdefABCDEF') +
	Optional(IntegerSuffix)
	# Make sure that the replacement of the '0x' to 'h' happens here
).setParseAction(lambda s, l, tokens: fix_hex_num(tokens[0]))('HexNumber')

'''
Parses a C integer.
'''
Integer = Combine(
	Optional(Literal('-')) +
	(
		Word(nums) + CaselessLiteral('e') + (
			Literal('+') | Literal('-')
		) +
		Word(nums) + Optional(IntegerSuffix)
		| Word(nums) + Optional(IntegerSuffix)
	)
)('Integer')

'''
Parses a C floating point decimal.
'''
FloatNumber = Combine(
	Optional(Literal('-')) + (
		Optional(Word(nums)) + Literal('.') + Word(nums) + CaselessLiteral('e') + (Literal('+') | Literal('-')) + Word(nums) + Optional(FloatSuffix | IntegerSuffix)
		| Optional(Word(nums)) + Literal('.') + Word(nums) + Optional(FloatSuffix | IntegerSuffix)
	)
)('FloatNumber')

'''
Parses any type of C integer literal.
'''
Number = FloatNumber | HexNumber | Integer

'''
Identifier:
	age
	_123
	__abc123
	th1s1samaz3box
'''
Identifier = Word(alphas + '_', bodyChars=alphanums + '_')

'''
Parses a C pound define.
'''
PoundDefine = (
	Keyword('#define') +
	Identifier +
	Optional(
		OneOrMore(
			Number
			| quotedString
			| Identifier
			| Keyword('()')
			| Keyword('( )')
			| Literal('(')
			| Literal(')')
			| Literal(',')
			| Keyword('...')
			| Word('!@#$%^&*-=+|.')
		)
	)
)

'''
Parses a C macro.
'''
Macro = (
	Keyword('#define').suppress() +
	Identifier +
	Literal('(').suppress() +
	Group(
		ZeroOrMore(
			Identifier
			| Literal(',')
			| Keyword('...')
		)
	) +
	Literal(')').suppress()
)

'''
Parses a C prefix such as a function return type. Replaces any occurance of a
specific storage type with a single type so it can be ingested by RGB.
'''
Prefix = OneOrMore(
	Keyword('__declspec(dllimport)').suppress()
	| Keyword('__declspec(dllexport)').suppress()
	| Keyword('__declspec(noreturn)').suppress()
	| Keyword('__stdcall').suppress()
	| Keyword('__cdecl').suppress()
	| Keyword('unsigned').suppress()
	| Keyword('signed').suppress()
	| Keyword('long long unsigned int').setParseAction(ReplaceWith('int'))
	| Keyword('long long signed int').setParseAction(ReplaceWith('int'))
	| Keyword('long long int').setParseAction(ReplaceWith('int'))
	| Keyword('long long').setParseAction(ReplaceWith('long'))
	| Keyword('long unsinged int').setParseAction(ReplaceWith('int'))
	| Keyword('long signed int').setParseAction(ReplaceWith('int'))
	| Keyword('long int').setParseAction(ReplaceWith('int'))
	| Keyword('long double').setParseAction(ReplaceWith('double'))
	| Keyword('short int').setParseAction(ReplaceWith('int'))
	| Keyword('const').suppress()
	| Identifier
)

'''
Parses a C function pointer.
'''
FunctionPtr = (
	Keyword('typedef void').suppress() +
	Literal('(').suppress() +
	Optional(Keyword('__stdcall').suppress() | Keyword('__cdecl').suppress()) +
	Literal('*').suppress() +
	Identifier +
	Literal(')').suppress() +
	Literal('(').suppress() +
	Group(
		ZeroOrMore(
			(Prefix | Literal('*')) +
			Optional(Literal(','))
		)
	) +
	Literal(')').suppress() +
	Literal(';').suppress()
)

'''
Any C type.  Filters out simple unacceptable occurances.
'''
Types = OneOrMore(
	Keyword('unsigned').suppress()
	| Keyword('signed').suppress()
	| Replace(Keyword('long long unsigned int'), 'int')
	| Replace(Keyword('long long signed int'), 'int')
	| Replace(Keyword('long long int'), 'int')
	| Replace(Keyword('long long'), 'long')
	| Replace(Keyword('long unsigned int'), 'int')
	| Replace(Keyword('long signed int'), 'int')
	| Replace(Keyword('long int'), 'int')
	| Replace(Keyword('long double'), 'double')
	| Replace(Keyword('short int'), 'int')
	| Keyword('const').suppress()
	| Identifier
)

'''
Parses a C typedef.
'''
Typedef = (
	Keyword('typedef').suppress() +
	OneOrMore(Types)
)

'''
Parses a C function.
'''
Function = (
	Group(OneOrMore(Prefix) + Optional(OneOrMore(Literal('*'))) + Optional(Prefix)) +
	Literal('(').suppress() +
	Group(ZeroOrMore(
		Prefix
		| Literal('*')
		| Literal(',')
		| Keyword('...')
	)) +
	Literal(')').suppress() +
	Literal(';').suppress()
)

'''
Parses a C global variable.
'''
GlobalVar = (
	Keyword('extern').suppress() +
	OneOrMore(Prefix | Literal('*')) +
	Literal(';').suppress()
)

'''
Parses a C struct prefix.
'''
StructPrefix = OneOrMore(
	Keyword('__declspec(dllimport)').suppress()
	| Keyword('__declspec(dllexport)').suppress()
	| Keyword('__declspec(noreturn)').suppress()
	| Keyword('__stdcall').suppress()
	| Keyword('__cdecl').suppress()
	| Keyword('unsigned').suppress()
	| Keyword('signed').suppress()
	| Keyword('long long unsigned int').setParseAction(ReplaceWith('int'))
	| Keyword('long long signed int').setParseAction(ReplaceWith('int'))
	| Keyword('long long int').setParseAction(ReplaceWith('int'))
	| Keyword('long long').setParseAction(ReplaceWith('long'))
	| Keyword('long unsinged int').setParseAction(ReplaceWith('int'))
	| Keyword('long signed int').setParseAction(ReplaceWith('int'))
	| Keyword('long int').setParseAction(ReplaceWith('int'))
	| Keyword('long double').setParseAction(ReplaceWith('double'))
	| Keyword('short int').setParseAction(ReplaceWith('int'))
	| Keyword('const').suppress()
)

'''
Parses a variable declaration within a struct.
'''
Decl = OneOrMore(
	StructPrefix
	| Identifier
	| Literal('*')
	| Literal(',')
) + Literal(';').suppress()

'''
Parses the start of a C struct.
'''
StructStart = (
	Optional(Keyword('typedef').suppress()) +
	Keyword('struct').suppress() +
	Identifier
)

'''
Parses the end of a C struct.
'''
StructEnd = (
	Literal('}').suppress() +
	Group(
	ZeroOrMore(Identifier +
	Optional(Literal(','))) +
	Literal(';').suppress()
))

'''
Parses a C enum.
'''
Enum = (
	Keyword('enum').suppress() +
	Identifier +
	Literal('{').suppress() +
	Group(OneOrMore(
		Identifier + Replace(Literal('='), ': ') + Word(alphanums + '_-.\'"') + Literal(',')
		| Identifier + Replace(Literal('='), ': ') + Word(alphanums + '_-.\'"')
		| Identifier + Literal(',')
		| Identifier
	)) +
	Literal('}').suppress() +
	Optional(Identifier) +
	Literal(';').suppress()
)
