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


class FunctionCompiler:
	"""
	Parses a Function from C code and generates a Red/System version of it.

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
			self.result = Function.parseString(self.line)
		except:
			print('BROKEN!')
			print(self.line)

	def generate(self, file):
		"""
		Generate a Red/System version of the parsing result.

		Args:
			file(file): the already-opened file to write the Red/System code.
		"""
		res = self.result
		return_sig = list(res[0])
		func_name = return_sig[-1]
		return_sig = return_sig[:-1]
		return_type = return_sig
		ptr_count = return_sig.count('*')
		return_sig = return_sig[:len(return_sig) - ptr_count]
		args = split_list(list(res[1]), ',')

		function_gen = f'{func_name}: "{func_name}"\n[%s'
		variadic = ''

		for i in range(len(args)):
			# Takes care of void do_this(void) <- there is no arg
			if args[i][0] != 'void':
				if args[i][0] != '...':
					function_gen += '\n\t%s' % argument(args[i])

				else:
					# The function has a variable number of arguments
					variadic = '\n\t[variadic]'

		# Add the [variadic] attribute
		function_gen %= variadic

		if not return_sig[0] == 'void' or ptr_count > 0:
			function_gen += '\n\treturn: %s'
			return_sig = get_return_type(return_type)
			function_gen %= return_sig

		function_gen += '\n]\n'

		file.write(function_gen)
		file.write('\n')
