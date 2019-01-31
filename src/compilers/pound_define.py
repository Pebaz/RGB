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
"""

from pyparsing import * # Best parsing library for Python
from red_utils import * # Tools for parsing C/Red/System code
from parse_utils import * # Tools for parsing in general


# Configuration Variables for testing
RGB_ENABLE_EMPTY_DEF 			= True
RGB_ENABLE_PAREN_INTEGER		= True
RGB_ENABLE_PAREN_UNKNOWN		= True
RGB_ENABLE_SIMPLE_DEF 			= True
RGB_ENABLE_POSSIBLE_C_CODE 		= True
RGB_ENABLE_WARNINGS 			= True
RGB_ENABLE_NESTED_MACRO_CALL 	= True


class PoundDefineCompiler:
	"""
	Parses a Pound Define from C code and generates a Red/System version of it.

	Attributes:
		line(str): the line (or lines) of C code to parse.
		result(str): the resulting Red/System code from parsing the C code.
	"""
	def __init__(self, line):
		"""
		Constructor.

		Args:
			line(str): the line to parse.
		"""
		self.line = line
		self.result = None

	def parse(self):
		"""
		Split the line into its constituent parts for code generation.
		"""
		try:
			self.result = PoundDefine.parseString(self.line)
		except Exception as e:
			print(e)
			print(self.line)

	def generate(self, file):
		"""
		Generate a Red/System version of the parsing result.

		Args:
			file(file): the already-opened file to write the Red/System code.
		"""
		res = list(self.result)

		# DONE {

		# Simplest possible case
		if len(res) == 2:
			if RGB_ENABLE_EMPTY_DEF:
				file.write(f'{res[0]} {res[1]} []\n')

		# A pound define with a single value in parentheses
		elif len(res) == 5 and res[2] == '(' and res[4] == ')':

			# If it's a number, it will be easy to fix
			try:
				num = Number.parseString(res[3])
				name = res[1]

				if RGB_ENABLE_PAREN_INTEGER:
					# Integer
					if num.Integer != '':
						file.write(f'{res[0]} {name} {num[0]}\n')

					# Hex Number
					elif num.HexNumber != '':
						file.write(f'{res[0]} {name} {fix_hex_num(num[0])}\n')

			# Try to strip the parentheses and write the definition to file.
			except:
				if RGB_ENABLE_PAREN_UNKNOWN:
					print(
						f'WARNING: {res[1]}\nhas a potentially-flawed'
						'binding, check for accuracy.'
					)
					file.write(f'{res[0]} {res[1]} {res[3]}')

		# }

		# Potentially raw C code
		elif RGB_ENABLE_POSSIBLE_C_CODE and res[2] == '(':
			c_code_warning(
				file,
				f'{res[0]} {res[1]} [{" ".join(res[2:])}]',
				self.line
			)
		
		# Has to be #define PBZ 11
		elif RGB_ENABLE_SIMPLE_DEF and len(res) == 3:
			file.write(f'{res[0]} {res[1]} {res[2]}\n')

		else:
			# If it starts with a '(', it is most likely C code
			if RGB_ENABLE_POSSIBLE_C_CODE and '(' not in res and ')' not in res:
				c_code_warning(
					file,
					f'{res[0]} {res[1]} [{" ".join(res[2:])}]',
					self.line
				)

			# Contains a nested macro call
			elif (
					RGB_ENABLE_NESTED_MACRO_CALL and
					#'__pragma' not in res and
					'(' in res and
					')' in res and
					res[1] != '('
				):

				if '__pragma' in res:
					print('-' * 80)
					print(
						' WARNING! This line contains a pragma, please review.'
						'\nHeader:\n'
					)
					print('', self.line)
					print('-' * 80 + '\n\n')


				name = res[1]

				# Solve recursive pound defines by initially defining the name
				# as an empty block
				if res.count(name) > 1:
					file.write(
						f'\n; The following {name} definition refers to'
						' itself so Red/System needs this empty definition\n'
					)
					file.write(f'#define {name} []\n')

				out = res[3:]

				# NOTE(Pebaz) Simple check for sanity
				if out[-1] != ')' or out[0] != '(':
					#raise Exception(f'Paren `)` error. {out}\n    {res}')
					c_code_warning(
						file,
						f'{res[0]} {res[1]} [{" ".join(res[2:])}]',
						self.line
					)

				# Surround individual arguments with parentheses for Red/System
				for i in range(len(out)):
					sym = out[i]

					if sym not in '(),':
						out[i] = f'({sym})'

				# Remove all the commas from the macro
				while ',' in out:
					out.remove(',')

				res.insert(2, '[')
				res.append(']')

				file.write(f'{res[0]} {res[1]} [ {res[3]} ')
				file.write(' '.join(out))
				file.write(']\n')


			# Can only be C code from here on out because it contains a pragma
			else:
				# raise Exception(
				# 	'Should never get here!\n'
				# 	f'Offending line: {self.line}'
				# )
				c_code_warning(
					file,
					f'UNSUPPORTED SYNTAX: CREATE AN ISSUE ON GITHUB.\n{res[0]} {res[1]} [{" ".join(res[2:])}]',
					self.line
				)

