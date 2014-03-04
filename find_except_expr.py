"""Attempt to find except-expression candidates

Usage: $ python3 find_except_expr.py filename.py [filename.py ...]

$ find cpython/ -name \*.py|xargs python3 ExceptExpr/find_except_expr.py >ExceptExpr/candidates.txt
"""

import ast
import sys

# Try to locate a cpython install directory. TODO: Locate more
# intelligently, so we have a better chance of actually finding it.
try:
	import io
	sys.path.append('cpython/Tools/parser')
	import unparse

	def dump(node):
		ret = io.StringIO()
		try:
			unparse.Unparser(node,ret)
		except AttributeError:
			# Binary operators can't be unparsed directly.
			# Try to translate back into an operator symbol;
			# if that fails, raise KeyError.
			return unparse.Unparser.binop[node.__class__.__name__]
		return ret.getvalue().strip()
except ImportError:
	# If we can't get Tools/parser/unparse.py, use ast.dump()
	# It's not as tidy but it works.
	dump = ast.dump

verbose = False

compare_key = {
	# Same target(s).
	ast.Assign: lambda node: ' '.join(dump(t) for t in node.targets),
	# Same target and same operator.
	ast.AugAssign: lambda node: dump(node.target) + dump(node.op) + "=",
	# A return statement is always compatible with another.
	ast.Return: lambda node: "(easy)",
	# Calling these never compatible is wrong. Calling them
	# always compatible will give lots of false positives.
	ast.Expr: lambda node: "(maybe)",
	# These ones are never compatible, so return some
	# object that's never equal to anything.
	ast.Import: lambda node: float("nan"),
	ast.ImportFrom: lambda node: float("nan"),
	ast.Pass: lambda node: float("nan"),
	ast.Raise: lambda node: float("nan"),
	ast.If: lambda node: float("nan"),
}

excepts = excepts_with_as = 0
simple_excepts = simple_excepts_with_as = 0

# Look for names that might become keywords
search_for = {"raises":0, "then":0, "when":0, "use":0}
total_names = 0
unique_names = set()
total_isisnots = 0
chosen_isisnots = {None:0, False:0, True:0}

class Walker(ast.NodeVisitor): # For "Ghost who walks", if you read comics
	def __init__(self, filename):
		self.filename = filename

	def visit_Name(self, node):
		# search_for.setdefault(node.id,0) # Uncomment to count all names
		if node.id in search_for:
			search_for[node.id] += 1
		global total_names
		total_names += 1
		unique_names.add(node.id)

	def visit_Compare(self, node):
		if isinstance(node.ops[0], (ast.Is, ast.IsNot)):
			global total_isisnots
			total_isisnots += 1
			if isinstance(node.comparators[0], ast.NameConstant):
				if node.comparators[0].value in chosen_isisnots:
					chosen_isisnots[node.comparators[0].value] += 1

	def visit_ExceptHandler(self, node):
		"""Keep stats on usage of 'as' in except clauses"""
		global excepts, excepts_with_as
		excepts += 1
		if node.name is not None: excepts_with_as += 1
		self.generic_visit(node)

	def visit_Try(self, node):
		"""Report on 'simple' try/except statements.

		The definition of simple is:
		1. No else or finally clause
		2. Only one except clause (currently)
		3. Exactly one statement in the try clause
		4. Exactly one statement in each except clause
		5. Each of those statements is the same type.
		6. That type is one that could be an expression.
		7. Those statements are all compatible.

		The last two are the trickiest."""
		self.generic_visit(node) # Recurse first for simplicity.

		# 1. No else or finally clause
		if node.orelse or node.finalbody: return

		# 2. Only one except clause (currently)
		# Note that having zero handlers shouldn't happen, as a try
		# block with no except clauses will normally have an else or
		# finally.
		if len(node.handlers) != 1: return

		# 3. Exactly one statement in the try clause
		# Again, I don't expect ever to see 0 here.
		# This check is quite optional (the rest of the checks don't
		# depend on it); some versions of the proposal are quite okay
		# with having more than one except clause.
		if len(node.body) != 1: return

		# 4. Exactly one statement in each except clause
		# These ones definitely could have zero statements, though.
		for handler in node.handlers:
			if len(handler.body) != 1: return

		# 5. Each of those statements is the same type.
		try_type = type(node.body[0])
		for handler in node.handlers:
			if type(handler.body[0]) is not try_type: return

		# 6. That type is one that could be an expression.
		# 7. Those statements are all compatible.
		# These two done with a lookup table. If the type isn't in
		# the table, dump it out for debugging (once); otherwise,
		# the function should return a value which is equal for any
		# two compatible nodes.
		if try_type not in compare_key:
			print("Unrecognized type",try_type.__name__,file=sys.stderr)
			compare_key[try_type] = lambda node: float("nan")
		func = compare_key[try_type]
		try_node = func(node.body[0])
		for handler in node.handlers:
			if try_node != func(handler.body[0]): return
		self.report(node, try_node)
		global simple_excepts, simple_excepts_with_as
		for handler in node.handlers:
			simple_excepts += 1
			if handler.name is not None: simple_excepts_with_as += 1

		# What's the cleanest way to get a readable form for display?
		# Some posts on python-list have pointed out viable modules -
		# one that I do think reasonable enough to mention here, as a
		# Lenaledian embedding - but I'm trying to avoid any external
		# deps. So, against the desire for clean display is my strong
		# desire to restrict myself to the standard library, ensuring
		# that this and nothing else is needed for the search. Sorry!

	def report(self, node, desc):
		print("%s:%d: %s: %s"%(self.filename,node.lineno,type(node.body[0]).__name__,desc))

def search(fn):
	with open(fn,"rb") as f:
		data = f.read()
	try:
		tree = ast.parse(data)
	except SyntaxError as e:
		# Some files in the stdlib are deliberately broken
		# (including lib2to3 test data, which is "broken" from
		# the point of view of a Python 3 parser). Just log it
		# (optionally) and move on.
		if verbose:
			print("Unable to parse", fn, file=sys.stderr)
			print(e, file=sys.stderr)
		return
	Walker(fn).visit(tree)

if __name__ == "__main__":
	for fn in sys.argv[1:]:
		# print("Searching", fn, "...")
		search(fn)
	if excepts:
		print("Of",excepts,"except clauses,",excepts_with_as,"use the 'as' clause:",excepts_with_as*100/excepts,"%",file=sys.stderr)
	if simple_excepts:
		print("Simple excepts:",simple_excepts_with_as,"/",simple_excepts,"=",simple_excepts_with_as*100/simple_excepts,"%",file=sys.stderr)
	if total_names:
		print(len(unique_names),"names are referenced",total_names,"times, avg",total_names//len(unique_names),file=sys.stderr)
	for name,count in sorted(search_for.items()):
		if count:
			print(count,"instances of the name",repr(name),file=sys.stderr)
	if total_isisnots:
		print(total_isisnots,"is/is not operators",file=sys.stderr)
	for target,count in chosen_isisnots.items():
		if count:
			print("\t",count,"comparing against",repr(target),file=sys.stderr)
