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
from pycparser import CParser # For parsing C a little easier
from red_utils import * # Tools for parsing C/Red/System code
from parse_utils import * # Tools for parsing in general

RGB_ENABLE_STDOUT = False

class StructCompiler:
	"""
	Parses a Struct from C code and generates a Red/System version of it.

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
		self.result = ''

		w = ' ' * 40

		# List of structure names and the current index level to access them
		struct_name = ['']
		struct_nest = 0

		# The result of each line
		res = None

		for line in self.line.split('\n'):
			if line.strip() == '': continue
			line = line.replace('\r', '')

			tab = '    ' * struct_nest

			if '{' in line:
				tab = '    ' * (struct_nest - 1)
				res = tab + '['

				if RGB_ENABLE_STDOUT:
					print(line + w[len(line):], res)


			# Individual Declarations
			elif ';' in line and '}' not in line:

				# Inline struct value
				if 'struct' in line and '*' not in line:
					vals = line.split(' ')
					nme = vals[-1].replace(';', '')
					strct = vals[-2]
					res = tab + f'{nme} [{strct} value]'
					if RGB_ENABLE_STDOUT:
						print(line + w[len(line):], res)
					continue

				# Pointer to struct
				elif 'struct' in line and line.count('*') == 1:
					vals = line.split(' ')
					nme = vals[-1].replace('*', '').replace(';', '')
					strct = vals[-2]
					res = tab + f'{nme} [{strct}]'
					if RGB_ENABLE_STDOUT:
						print(line + w[len(line):], res)
					continue


				# Anything past here is a normal declaration (remove struct)
				line.replace('struct', '')

				# Handle Multiple Declarations on one line

				the_decl = list(Decl.parseString(line.strip()))
				end_of_type = None # Index where the type ends in list

				# Get the index of where the type ends
				if '*' in the_decl:
					end_of_type = (len(the_decl) - the_decl[::-1].index('*'))
					
				# The first item _is_ the type
				else:
					end_of_type = 1

				# ['int', '*', <-- 'x', ',', 'y', ',', 'z']
				the_type = the_decl[:end_of_type]

				values = split_list(the_decl[end_of_type:], ',')

				'''
				Since the `argument` function needs only one type + id,
				add the type to each and every var and handle them separately
				'''
				values = [the_type + i for i in values]


				for value in values:

					had_to_make_affordances_for_red_system_again = False

					# Handle pointers
					if '*' in value:

						# Only cap it to a single pointer if the decl has > 1
						if value.count('*') > 1:
							value = 'int', '*', value[-1]
							had_to_make_affordances_for_red_system_again = True

					res = tab + argument(value)

					if had_to_make_affordances_for_red_system_again:
						res += f' ; {line.strip()}'

					if RGB_ENABLE_STDOUT:
						print(line + w[len(line):], res)

					# Manually add this res so that each variable can be added
					self.result += res + '\n'

				'''
				Since we manually added each var, we don't need to add the
				last one again
				'''
				res = ''

			elif '}' in line:
				tab = '    ' * (struct_nest - 1)
				ender = StructEnd.parseString(line.strip())[0]

				if struct_nest > 1:
					res = tab + '] value]'
					if RGB_ENABLE_STDOUT:
						print(line + w[len(line):], res)
				else:
					res = tab + ']'
					if RGB_ENABLE_STDOUT:
						print(line + w[len(line):], res)

				struct_nest -= 1
				struct_name.pop()

			else:
				struct_nest += 1
				struct_name.append(StructStart.parseString(line.strip())[0])

				pre = line + w[len(line):]

				if struct_nest > 1:
					res = tab + f'{struct_name[struct_nest]} [struct!'
					if RGB_ENABLE_STDOUT:
						print(pre, res)
				else:
					res = tab + f'{struct_name[struct_nest]}!: alias struct!'
					if RGB_ENABLE_STDOUT:
						print(pre, res)

			# After each iteration, add the result to self.result
			self.result += res + '\n'

	def generate(self, file):
		"""
		Generate a Red/System version of the parsing result.

		Args:
			file(file): the already-opened file to write the Red/System code.
		"""
		file.write('; Please check for accuracy:\n')
		file.write(f'{self.result}\n\n\n')
