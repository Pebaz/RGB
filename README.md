# RGB - Red Generator of Bindings
-------------------------------------------------------------------------------

![Red Generator of Bindings Logo](./misc/RGB-Logo.png)

Does 95% of the Work Required to Port C Libraries to Red/System by Converting
C Header Files to Red/System Code.

### Hello World

```C
// calculator.h

#ifndef CALC_H
#define CALC_H

__declspec(dllexport) float __cdecl colonist_add(float x, float y);
__declspec(dllexport) float __cdecl colonist_sub(float x, float y);
__declspec(dllexport) float __cdecl colonist_mul(float x, float y);
__declspec(dllexport) float __cdecl colonist_div(float x, float y);

#endif // CALC_H
```

Compile With:

```sh
python src/main.py gen --header="calc.h" --llvm_dir="C:\Program Files\LLVM\bin" --dynlib="calc.dll" --out-file="calc.reds"
```

Result:

```Rebol
;; ...
;; Extraneous pound defines omitted

#import
[
	"calc.dll" cdecl
	[
		colonist_add: "colonist_add"
		[
			x [float32!]
			y [float32!]
			return: [float32!]
		]

		colonist_sub: "colonist_sub"
		[
			x [float32!]
			y [float32!]
			return: [float32!]
		]

		colonist_mul: "colonist_mul"
		[
			x [float32!]
			y [float32!]
			return: [float32!]
		]

		colonist_div: "colonist_div"
		[
			x [float32!]
			y [float32!]
			return: [float32!]
		]
	]
]
```




#### Description
-------------------------------------------------------------------------------

Red Generator of Bindings is a tool that has the potential to save many hours
of work that would be spent porting a C library over to Red/System. Since the
process of importing select functions from a given DLL/SO/DYLIB is mostly
straightforward, I believe that the need for such a tool is often overlooked.

However, in order to improve the maturity of any programming language's
ecosystem, there has to be a wealth of libraries so that everyone is not
reinventing the wheel with each new software project.

When RGB is invoked from the command line, the following actions are completed:

 1. Accepts a C header file as input.

 2. Runs it through the C preprocessor found in Clang (making the bindings for
	a particular library potentially platform-specific).

 3. Formats the output via Clang-Format so that it is easier to parse.

 4. Parses every single item (struct, global var, function pointer).

 5. Generates a Red/System equivalent and writes it to a Red/System source file
	that can be easily imported into an existing application.

##### Please Note

 * The accompanying DLL/SO/DYLIB file must be on the target program's PATH so
   that it can import it.

 * Not all syntax possible in C header files is supported.

 * Clang will include _all_ of the declarations that would normally be included
   if the header file were to be used during compilation of a C program. If
   these are not desired, they can be removed from the resulting Red/System
   file.

 * Warnings will be generated on the command line and inside the generated
   Red/System file so make sure to review it in case RGB is unable to port the
   given declaration cleanly. RGB is not a cross-compiler, so if a macro
   contains C code for example, RGB will warn about this condition and allow
   you to manually port it.

 * POINTERS TO POINTERS (etc.) ARE NOT SUPPORTED BY RED/SYSTEM AT ALL. If your
   library uses these, you must find a way to port them to Red/System in a way
   that is custom to how you will use them.


#### Background
-------------------------------------------------------------------------------

The [Red](https://www.red-lang.org) programming language is an amazing language
with the potential to be used as a be-all-end-all solution for all development.
Languages such as [Python](https://www.python.org/) have innate programmer
productivity boosts that are related to the succinctness of its syntax. Red is
very similar to Python in that it is dead simple to write. Due to its
homoiconic syntax, it is more semmantically compressed than lanauges such as
C++/Java, which according to [Casey Muratori](https://caseymuratori.com/blog_0015),
leads to greater complexity and more bugs.

In addition, the Red ecosystem comes with the
[Red/System](https://static.red-lang.org/red-system-specs-light.html) dialect,
which is a C-level language that allows you to write low-level programs that 
can take advantage of manual memory management, a basic requirement of
high-performance software.

I for one believe that this is my dream ecosystem, as it combines both coding
speed and runtime performance into one package that covers just about every
conceivable use-case, making it the first
[full-stack language](https://www.red-lang.org/p/about.html). I would like to
help contribute to this growing community in an effort to increase the amount
of exposure that it has in other programming circles because I believe in its
potential.

The success of Python may be in part to the ease of which libraries can be ported
over from C. This is why I thought it would be a good idea to create a piece of
software that would automate it as much as possible, much like the project
[SIP](https://www.riverbankcomputing.com/software/sip/intro).


### Installation
-------------------------------------------------------------------------------

```sh
git clone://github.com/Pebaz/RGB
cd RGB
pip install -r requirements.txt
```


### Dependancies
-------------------------------------------------------------------------------

Clang/Clang-Format (Windows build can be found [here](http://llvm.org/builds/))


### Repository

[https://github.com/Pebaz/RGB](https://github.com/Pebaz/RGB)


### See Also

 * [C2Reds](https://github.com/iceflow19/c2reds)
 * [Parse-C-Header](https://github.com/rebolek/parse-c-header)
