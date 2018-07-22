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

Convenience functions for parsing different C language constructs into their
Red/System equivalents.
"""

from random import choice # For creating random IDs


def c_code_warning(file, c_code, line):
	"""
	Convenience function for printing/writing a warning to the console/header
	file respectively.

	Writes a warning to the console and the output header so that the person
	porting the given library will check/convert the C code to Red/System.

	Args:
		file (file): the file to write to.
		c_code (str): the code to write to the output header.
		line (str): the actual line from the C header.
	"""

	file.write('; ' + '-' * 78 + '\n')
	file.write('; WARNING! Raw C Code Detected, Please Review and Correct:\n')
	file.write(c_code + '\n\n')
	file.write('; Line in Question from Header:\n')
	file.write('; %s' % line)
	file.write('; ' + '-' * 78 + '\n\n')

	print('-' * 80)
	print(' WARNING! Raw C Code Detected, Please Review and Correct\n')
	print('', line)
	print('-' * 80 + '\n\n')


def fix_hex_num(num):
	"""
	Converts a C-style hexadecimal literal into a Red/System equivalent.

	Turns 0xFAEBAE12 into FAEBAE12h.

	Args:
		num(str): hexidecimal integer literal from C.

	Returns:
		The string equivalent of a C hexidecimal literal in Red/System.
		Since Red/System cannot handle hex numbers that have more than 8
		digits, the integer version of the given number may be returned.
		For example, the number: 0xFFFFFFFF12
		Is longe than 8 digits, so this will be returned instead: 1099511627538
	"""
	num = num[2:].upper()

	# Red/System cannot handle hex literals longer than 8 characters
	if len(num) > 8:

		# Return the integer version of the hex literal
		return str(int(num, base=16))
	else:
		return num + 'h'


def rand_id(count):
	"""
	Generates a random identifier for use in Red/System code.

	Some functions declarations do not provide argument names, this function
	can be used to generate some since Red/System needs them for importing such
	functions.

	Args:
		count(int): the number of letters + numbers that the id will have.

	Returns:
		A string consisting of (letters * `count`) + (numbers * `count`).
		For example, if count is 3, "abc123" will be returned.
	"""
	r = range(count)
	alphabet = ''.join([choice('abcdefghijklmnopqrstuvwxyz') for i in r])
	nums = ''.join([choice('0123456789') for i in r])
	return alphabet + nums


def split_list(the_list, delimiter):
	"""
	Equivalent to string.split(`delimiter`), but for lists.

	If a flat list contains a sequence of items and then a uniform sequence
	terminator, it is difficult to get each sequence by itself in its own list.
	This function does just that.

	Args:
		the_list(list): the list to delimit.
		delimiter(str): the delimiter by which to split the list on.

	Returns:
		A list of lists containing each sequence separated by the delimiter.
		For example, the list:
		['int', 'age', ',', 'int', '*', 'numbers', ',', 'char', 'middle_initial']
		Can be split using the comma character: "," and will be turned into:
		[['int', 'age'], ['int', '*', 'numbers'], ['char', 'middle_initial']]
	"""
	if delimiter not in the_list:
		return [the_list]

	else:
		copy = the_list.copy()
		new_list = []

		while delimiter in copy:
			index = copy.index(delimiter)
			new_list.append(copy[:index])
			copy = copy[index + 1:]

		new_list.append(copy)

		return new_list


def mangle_type(the_type):
	"""
	Turns `the_type` into its Red/System equivalent.

	Note: This list will grow as issues are submitted that contain specific
	types that have exact Red/System built-in equivalents.

	Args:
		the_type(str): the C type to change to Red/System.

	Returns:
		The converted type. For example, Red/System does not contain a native
		64-bit integer type, so float64 is used instead.

		`long` in C becomes `float64` in Red/System.
	"""
	if the_type == 'char':
		return 'byte'

	elif the_type == 'bool':
		return 'logic'

	elif the_type == 'long':
		# NOTE(Pebaz): The Red/System float (float64) datatype is 64-bits
		# wide so it will accept 64-bit integer literals.
		return 'float64'

	elif the_type == 'short':
		return 'integer'

	elif the_type == 'int':
		return 'integer'

	elif the_type == 'double':
		return 'float64'

	elif the_type == 'float':
		return 'float32' 

	elif the_type == '__int8':
		return 'byte'

	elif the_type == '__int16':
		return 'integer'

	elif the_type == '__int32':
		return 'integer'

	elif the_type == '__int64':
		return 'float64'

	else:
		return the_type


def make_type(target):
	"""
	Turns the target type into a useable Red/System version.

	For instance, `int age;` would become `age: [integer!]` in Red/System,
	and this function creates the value in the square brackets.

	Args:
		target(str): the type string to be converted to Red/System.

	Returns:
		A string of the Red/System type. `integer` becomes `[integer!]`.
	"""
	return f'[{target}!]'


def pointer(target, ptr_count):
	"""
	Dynamically creates a pointer declaration in Red/System.

	Sadly, this function had be changed because Red/System does not support
	multiple pointers. For instance, the function argument:
	`int*** value`
	Simply cannot be ported to Red/System. The only compileable version is:
	`value [pointer! [integer!]]`

	Args:
		target(str): the type to be pointed to.
		ptr_count(int): the number of pointer redirects.

	Returns:
		Simply returns `"[pointer! [integer!]]"`
		It used to create a string that contained as many pointers as needed.
		E.G.: target == "integer" and ptr_count == 3 would look like this:
		`[pointer! [pointer! [pointer! [integer!]]]]`
	"""
	# NOTE(Pebaz): Red/System can only support a single pointer
	return '[pointer! [integer!]]'


def argument(target):
	"""
	Turns a list of strings into a function argument in Red/System.

	The list can contain: `['int', 'age']`, and this function will return:
	`age [integer!]`

	Args:
		target(list): the list of strings to convert.

	Returns:
		A string that contains a compileable Red/System version of the given C
		function argument. For instance:
		`int age`
		Will be turned into:
		`age [integer!]`
	"""
	ptr_count = target.count('*')
	name = target[-1]
	the_type = target[:len(target) - ptr_count - 1]

	# If the argument has no name, we have to generate one
	if len(the_type) == 0:
		target.append('arg_name_' + rand_id(2))
		return argument(target)

	elif len(the_type) > 1:
		raise Exception('Type longer than 1 word: %s' % str(target))

	the_type = mangle_type(the_type[0])

	# If the type is a pointer, handle it
	if ptr_count > 0:
		return f'{name} {pointer(the_type, ptr_count)}'

	# Else handle it's type
	else:
		return f'{name} {make_type(the_type)}'


def get_return_type(target):
	"""
	Returns a Red/System version of the return type of a C function.

	Turns: `['int', '*', '*']` into:
	`[pointer! [integer!]]`

	Args:
		target(list): the list of strings that make up the C return type.

	Returns:
		A string containing the Red/System version of the C return type.
	"""
	ptr_count = target.count('*')
	the_type = target[:len(target) - ptr_count]
	the_type = mangle_type(the_type[0])

	# If the type is a pointer, handle it
	if ptr_count > 0:
		return f'{pointer(the_type, ptr_count)}'

	# Else handle it's type
	else:
		return f'{make_type(the_type)}'
