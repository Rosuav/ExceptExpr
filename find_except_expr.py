"""Attempt to find except-expression candidates

Usage: $ python3 find_except_expr.py filename.py [filename.py ...]

$ find cpython/ -name \*.py|xargs python3 ExceptExpr/find_except_expr.py >ExceptExpr/candidates.txt
"""

import ast

class walker(ast.NodeVisitor): # For "Ghost who walks", if you read comics
	def __init__(self, filename):
		self.filename = filename

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

		The last two are the trickiest. Currently I'm looking
		only for assignments, where both try and except assign
		to the same target. This is, however, too narrow."""
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
		# Currently cheating, as per docstring.
		if try_type is not ast.Assign: return

		# 7. Those statements are all compatible.
		# Currently looking for the same target.
		# Since I am fairly clueless with the ast module, I'm
		# looking for string equality of ast.dump(), which is
		# hardly the best way to do things!
		try_target = ast.dump(node.body[0].targets[0])
		for handler in node.handlers:
			if try_target != ast.dump(handler.body[0].targets[0]):
				return

		# What's the easiest way to get a readable form for display?
		print("%s:%d: %s"%(self.filename,node.lineno,try_target))

def search(fn):
	with open(fn,"rb") as f:
		data = f.read()
	try:
		tree = ast.parse(data)
	except SyntaxError as e:
		# Some files in the stdlib are deliberately broken
		# (including lib2to3 test data, which is "broken" from
		# the point of view of a Python 3 parser). Just log it
		# and move on.
		print("Unable to parse", fn, file=sys.stderr)
		print(e, file=sys.stderr)
		return
	walker(fn).visit(tree)

if __name__ == "__main__":
	import sys
	for fn in sys.argv[1:]:
		# print("Searching", fn, "...")
		search(fn)
