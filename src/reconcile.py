#!usr/bin/env python

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

reconcile.py
"""


import pyparsing # Best Python parsing library


class ReconciliationException(Exception):
	"""
	Exception class to deal with Reconcile class names that do not show up in
	the global namespace when they are used.

	Basically, a KeyError but with the goal of providing a way to give the user
	a better idea of what happened.
	"""


class Reconcile(pyparsing.Forward):
	"""
	Forwarder class with capability to name what should be left-shifted at a
	later time.

	This class is meant to be used as a better version of the `Forward` class
	in that instead of putting a generic placeholder into a grammar and then
	fixing it later in the code, you can name the exact parser that needs to be
	put there after it has been defined.

	For instance:
	
	>>> from pyparsing import *
	>>> parser = Word(nums, exact=3) + Forward() + Word(nums, exact=3)
	>>> # Replace the Forward with the correct parser
	>>> parser[0][1] << Literal('-')
	>>> parser.parseString('123-456')
	(['123', '-', '456'], {})

	Instead of going through all that trouble to figure out the exact index of
	a particular Forward instance in your parser, why not use something that
	does all of that for you and is as natural as putting the full class name
	so that your code is not cluttered:

	>>> from pyparsing import *
	>>> parser = Word(nums, exact=3) + Reconcile('Dash') + Word(nums, exact=3)
	>>> Dash = Literal('-')
	>>> Reconcile.reconcile_all(parser)
	>>> parser.parseString('123-456')
	(['123', '-', '456'], {})

	In conclusion, it makes your grammar look like this:

	>>> Line = Reconcile('Keywords') + Reconcile('Otherthing')
	>>> Keywords = OneOrMore(Word(alphas))
	>>> Otherthing = Literal(';')
	>>> Reconcile.reconcile_all(Line)

	Rather than this:

	>>> Line = Forward() + Forward()
	>>> Keywords = OneOrMore(Word(alphas))
	>>> Otherthing = Literal(';')
	>>> # Usually have to manually check each index first
	>>> Line[0] << Keywords
	>>> Line[1] << Otherthing

	Attributes:
		classname (str): the classname to find in the global scope during
			reconciliation of any Forward values found in a given parser.

		target_defined (bool): determines whether or not this Forward has been
			left-shifted with the correct parser value.
	"""

	def __init__(self, classname):
		"""
		Initializes this `Forward` subclass with a classname that will later be
		used to left-shift '<<' the value into the Forward's placeholder
		mechanics.

		Args:
			self (Reconcile): this object.

			classname (str): The name of the object in the global namespace
				that should be used to left-shift '<<' the correct value in the
				slot that was previously occupied by the placeholder.
		"""
		pyparsing.Forward.__init__(self)
		self.classname = classname
		self.target_defined = False

	def __repr__(self):
		"""
		Returns a string representation of 'self'.
		"""
		return f'Reconcile({self.classname})'

	@staticmethod
	def __check_iterable(obj):
		"""
		Checks whether or not a given object is iterable.

		Uses a list comprehension to quickly throw a TypeError if a given
		object is not a parser that contains other parsers.

		Args:
			obj: the object for which to check for iteracy.

		Returns:
			True if the object can be iterated through (contains other parsers)
			and False if it is just a lone parser.
		"""
		try:
			_ = [i for i in obj]
			return True
		except TypeError as e:
			return False

	@staticmethod
	def reconcile_all(parser, global_scope, reconciling=[]):
		"""
		Automatically left-shifts the correct parser object into every
		`Forward` slot in a given parser.

		Goes through each and every element contained in a given parser,
		searches the global namespace (globals()) and left-shifts the correct
		parser into the `Forward` slot for you instead of having to manually
		figure out each index and left-shift them yourself.

		Args:
			parser: the parser to reconcile all `Reconcile` instances.

		Raises:
			ReconciliationException: Couldn't find the parser name in globals()
		"""
		if Reconcile.__check_iterable(parser):
			for item in parser:

				# The item is a Reconcile, so it can be reconciled
				if type(item) == Reconcile:

					# Only reconcile it if it has not been already
					if not item.target_defined and item.classname not in reconciling:

						# Obtain the parser from the global namespace
						try:
							target = global_scope[item.classname]
						except KeyError as e:
							raise ReconciliationException(
								('\n\n"%s" not found in the global scope.\n' +
								'Is "%s" a typo? If not, make sure that no' +
								' other module is proliferating the' +
								' namespace with names that could be' +
								' obscuring it.\nThis can definitely happen' +
								' if you are using a starred import (from' +
								' math import *).')
								% (e.args[0], e.args[0])
							) from e

						# Make sure we are not trying to reconcile something
						# that is currently being reconciled
						if item.classname not in reconciling:
							reconciling.append(item.classname)

							# First, reconcile the target so that this instance is
							# not given a partial definition.
							Reconcile.reconcile_all(target, global_scope, reconciling)

							# Finally, left-shift the right parser into the slot
							item << target

							# Mark this forwarder as done
							item.target_defined = True

				# The object iterable and Reconcile, so reconcile it
				else:
					Reconcile.reconcile_all(item, global_scope, reconciling)


if __name__ == '__main__':
	WORD = pyparsing.Word(pyparsing.alphas)
	Line = Reconcile('Keywords') + Reconcile('Otherthing')
	Keywords = pyparsing.OneOrMore(WORD)
	Otherthing = pyparsing.Literal(';')
	Reconcile.reconcile_all(Line)
	print(Line.parseString('Say hello world to the world;'))
