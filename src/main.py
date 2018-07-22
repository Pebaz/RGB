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

This program has multiple stages:

1. Take a given input header(s) and produce formatted:
   - Output.txt

2. Parse this file to obtain only the parts Red/System will care about.

3. Generate a corresponding Red/System import "header" file that can be used
   in a Red program by simply importing the "header" file.
"""

import fire # CLI framework
import format # Launching the formatter
from rgb import RGB # RGB compiler class

class CLI:
	"""
	Red Generator of Bindings's command line interface.
	"""
	def gen(self, header, llvm_dir, dynlib, out_file=None, call_con='cdecl', include_dir='.'):
		"""
		Generate a Red/System binding file from the given header input.
		"""
		# Clean up the header file and obtain all declarations/pound defines
		declarations = format.format_header(header, llvm_dir, include_dir)

		# Both parse and generate the declarations
		rgb_compiler = RGB(declarations, dynlib, call_con, out_file)
		rgb_compiler.compile()


if __name__ == '__main__':
	fire.Fire(CLI)