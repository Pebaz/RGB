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

Contains functionality to use compiler classes for each type of desired cross-
compilation target from a C header file.
"""

import os # Get only filename from path
from pyparsing import * # Best parsing framework in Python
from compilers.pound_define import PoundDefineCompiler # Compiles Pound Defines
from compilers.macro import MacroCompiler # Compiles macros
from compilers.func_ptr import FuncPtrCompiler # Compiles Function Pointers
from compilers.typedef import TypedefCompiler # Compiles Typdefs
from compilers.function import FunctionCompiler # Compiles Functions
from compilers.global_var import GlobalVarCompiler # Compiles Global Vars
from compilers.struct import StructCompiler # Compiles Structs
from compilers.enum import EnumCompiler # Compiles Enums


class RGB:
	"""
	Takes each declaration obtained from running Clang-Format and compiles it
	to a Red/System form.

	The first pass encompasses parsing out all the parts that Red/System will
	care about. The second pass then writes the correct Red/System version to
	the output file.

	Attributes:
		declarations(list): list of strings that represent declarations.
		dynlib(str): the path to the dynamic lib to import into Red/System.
		call_con(str): one of (cdecl/stdcall).
		outfile(str): the file to write all the compiled declarations.
	"""
	def __init__(self, declarations, dynlib, call_con, outfile=None):
		"""
		Constructor.
		
		If the output file path is not given, one that matches the C library
		target will be used.

		Args:
			declarations(list): list of declarations to parse/generate.
			dynlib(str): the dynamic library target.
			call_con(str): one of (cdecl/stdcall).
			outfile(str): path to output file with Red/System file extension.
		"""
		self.declarations = declarations
		self.dynlib = os.path.basename(dynlib)
		self.call_con = call_con

		if outfile == None:
			self.outfile = dynlib.split('.')[0] + '.reds'
		else:
			self.outfile = outfile

	def compile(self):
		"""
		Parses and then generates each declaration to the output file.

		Meant to be called from other modules to perform the compilation steps.
		"""
		results = self.__parse_all(self.declarations)
		self.__generate(results)

	def __parse_all(self, lines):
		"""
		Go through each line in the declarations list and parse it according to
		its type.

		Every type of C declaration gets parsed one line at a time. However,
		for special declarations like structs, they are multiline, which means
		that each line that makes them up should be added to `self.line`. Since
		structs can also be nested this makes the job of parsing them that much
		harder.

		Args:
			lines(list): declarations list
		"""

		# Contains compilers that have their line attached to them
		results = []

		# One of 'Enum' or 'Struct'
		state = None

		# Add lines that belong to Enum or Struct to this compiler
		compiler = None

		# For nested structs
		nest_level = 0

		for line in lines:

			# If there is no state set, a new compiler can be created
			if state == None:
				compiler = self.__choose_compiler(line)

				if compiler != None:

					# Set the state if there will be multiple lines
					if compiler.__class__.__name__ == 'EnumCompiler':
						state = 'Enum'

					elif compiler.__class__.__name__ == 'StructCompiler':
						state = 'Struct'

					# Finally, add the compiler to the list for parsing
					results.append(compiler)

			# Handle multiple lines
			elif state == 'Struct' or state == 'Enum':

				# Add the line to the current compiler in either case
				compiler.line += line

				# End of (possibly nested) declaration
				if '}' in line:
					nest_level -= 1

					# End of top-level declaration?
					if nest_level == 0:
						state = None

				# Nesting level 1 equals a single struct/enum declaration
				elif '{' in line:
					nest_level += 1

		# Gather results from each compiler
		for i in results:
			i.parse()

		return results

	def __choose_compiler(self, line):
		"""
		Figures out which compiler to use for a given line.

		Determines which compiler should be used to parse and then generate the
		Red/System version of a C declaration by looking for attributes unique
		to each one.

		Args:
			line(str): The line obtained from running Clang-Format.
		"""
		if len(line.strip()) == 0:
			return

		compiler_state = 'Single_Line'

		# Global Variable
		if line.startswith('extern'):
			return GlobalVarCompiler(line)

		# Could be pound define or macro
		elif '#define' in line:
			if MacroCompiler.try_parse(line):
				return MacroCompiler(line)
			else:
				return PoundDefineCompiler(line)

		# Struct declaration start
		elif 'struct' in line and ';' not in line:
			return StructCompiler(line)

		# Enum declaration start
		elif 'enum' in line:
			if line[line.index('enum') - 1] not in alphanums + '_':
				return EnumCompiler(line)

		# Function Pointer
		elif FuncPtrCompiler.try_parse(line):
			return FuncPtrCompiler(line)

		# Typedef only since 'struct' and 'enum' were not run
		elif 'typedef' in line:
			return TypedefCompiler(line)

		# Has to be a Function if it didn't ping anything else
		else:
			return FunctionCompiler(line)

	def __generate(self, results):
		"""
		Writes all Red/System declarations to the header file.

		All declarations are written in their proper order so that they remain
		organized.

		Args:
			results(list): contains all the compilers.
		"""

		# Control the output of the generated code
		with open(self.outfile, 'w') as file:

			# Write the Red/System header
			file.write('Red/System []\n\n')

			# Structs
			for i in results:
				if i.__class__.__name__ == 'StructCompiler':
					i.generate(file)

			# Pound Defines
			for i in results:
				if i.__class__.__name__ == 'PoundDefineCompiler':
					i.generate(file)

			# Macros
			for i in results:
				if i.__class__.__name__ == 'MacroCompiler':
					i.generate(file)

			# Enums
			for i in results:
				if i.__class__.__name__ == 'EnumCompiler':
					i.generate(file)
			
			# Typedefs
			for i in results:
				if i.__class__.__name__ == 'TypdefCompiler':
					i.generate(file)

			# Function Pointers
			for i in results:
				if i.__class__.__name__ == 'FuncPtrCompiler':
					i.generate(file)

			# Import the library with the appropriate calling convention:
			file.write(f'\n\n\n#import [\n\t"{self.dynlib}" {self.call_con} [\n')
			
			# Functions
			for i in results:
				if i.__class__.__name__ == 'FunctionCompiler':
					i.generate(file)

			# Global Variabls
			for i in results:
				if i.__class__.__name__ == 'GlobalVarCompiler':
					i.generate(file)

			# Finally write the closing square bracket
			file.write('\t]\n]')
