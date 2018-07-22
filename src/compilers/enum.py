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


class EnumCompiler:
	"""
	Parses an Enum from C code and generates a Red/System version of it.

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
		self.result = Enum.parseString(self.line)

	def generate(self, file):
		"""
		Generate a Red/System version of the parsing result.

		Args:
			file(file): the already-opened file to write the Red/System code.
		"""
		res = list(self.result)
		args = split_list(res[1][:], ',')

		c_code = False

		values = ''
		for i in args:
			if len(i) > 1:

				# Possible C code expression for enum value
				if len(i) > 3:
					c_code = True

				values += f'{i[0]}: ' + ' '.join(i[2:]) + ' '

			else:
				values += f'{i[0]} '

		if c_code:
			file.write('; ' + '-' * 77)
			file.write('; WARNING: Potential C expression, please review:')

		file.write(f'#enum {res[0]}! [ {values} ]\n')

		if c_code:
			file.write('; ' + '-' * 77)
