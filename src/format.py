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


In order for this formatter to work, the .clang-format file must reside in the
folder in which format.py is run.
"""

import sys # command line arguments
import os # Run OS commands
import subprocess # Run OS commands and get output as str


def format_header(header, llvm_dir, includes):
	"""
	Runs clang on the given header file to obtain pound defines and
	declarations and then clean up the resulting file.

	The includes argument is there for the express purpose of allowing you to
	run RGB against a larger library with potentially hundreds of header files.

	Args:
		header (str): The header file to format.
		includes (str): The path of the folder containing relevant headers.
	"""

	# First delete any previously-generated results:
	if os.path.exists('out/Output.h'):
		os.remove('out/Output.h')

	# Get the LLVM bin dir
	if llvm_dir[-1] not in '/\\':
		llvm_dir += '/'

	# Run clang and get declarations
	clang = subprocess.Popen([f'{llvm_dir}clang', '-I', includes, '-E', header],
			stdout=subprocess.PIPE)

	# Run clang-format and clean up those declarations
	clang_format = subprocess.Popen([f'{llvm_dir}clang-format', '-style=file'], stdin=clang.stdout,
			stdout=subprocess.PIPE)

	# Close the pipe
	clang.stdout.close()

	# Get the cleansed output
	declarations = []
	record = False
	for line in clang_format.communicate()[0].decode('UTF-8').split('\n'):
		line = line.strip()
		if line.startswith('#'):
			# Checks to see if the __FILE__ has switched back to `header`
			# If it has, start recording lines again and stop when __FILE__ is
			# one of the included headers.
			record = f'"{header}"' in line
		elif record and line and not line.startswith('#'):
			declarations.append(line + '\n')

	# Run clang again with the purpose of obtaining all pound defines
	cmd_line = [f'{llvm_dir}clang', '-dM', '-E', header]
	defines = subprocess.check_output(cmd_line).decode('UTF-8')
	defines = [i + '\n' for i in defines.split('\n')]

	# Combine all the info into one large list
	defines.extend(declarations)

	# Append the defines to the end of the file containing the declarations
	with open('out/Output.txt', 'w') as file:
		file.writelines(defines)

	# NOTE(Pebaz): In the future, it may be of concern to support massive
	# header files by yielding each line in the file rather than putting it all
	# into RAM at the same time.
	return defines
