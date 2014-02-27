import ast
import sys
sys.path.append('pep-463-except-expr/Tools/parser')
sys.path.append('Tools/parser')
import find_except_expr

# If true, comment blocks will be inserted to explain the changes made.
# Otherwise, the translation will be "pure".
explain = True

# If omitted, expression->expression except blocks will be translated. This is
# not recommended for normal use - it leads to many translations which, while
# technically correct, are not really helpful. So it's better to not, except
# maybe to stress-test the translations.
find_except_expr.compare_key[ast.Expr] = lambda node: float("nan")

class Walker(find_except_expr.Walker):
	def __init__(self, *args):
		self.updates=[]
		super().__init__(*args)

	def report(self, node, desc):
		# For this translation, the 'as' keyword is not supported.
		if node.handlers[0].name is not None: return
		# Figure out which lines to edit.
		# TODO: Make sure nothing else has these lines. For now, it
		# just specifies the line numbers to be deleted.
		lines=[n.lineno for n in ast.walk(node) if hasattr(n,'lineno')]
		self.updates.append((min(lines), max(lines), node))

# TODO: This assumes all indentation is done with spaces. Support tabs.
def indent(line):
	"""Return the indentation from a line of source code"""
	return b' ' * (len(line) - len(line.lstrip(b' ')))

def search(fn):
	with open(fn,"rb") as f:
		data = f.read()
	try:
		tree = ast.parse(data)
	except SyntaxError as e:
		return
	w=Walker(fn)
	w.visit(tree)
	if not w.updates: return # Nothing to change.
	w.updates.append((float("inf"),float("inf"),None)) # Marker
	print("Updating",fn)
	with open(fn, "wb") as f:
		stop = -1
		for lineno,line in enumerate(data.split(b"\n")[:-1], 1):
			while lineno > stop:
				start,stop,node = w.updates.pop(0)
			if lineno < start:
				f.write(line + b"\n")
				continue
			if lineno == start:
				# Indent with the same number of spaces as the start line
				sp = indent(line)
				# I have no idea what the encoding of the source file
				# should be. Assume ASCII is enough for these parts.
				# Also, this will be useful only if unparse is loaded.
				if explain: f.write(sp + b"# PEP 463 automated translation:\n")
				# This transformation works for Assign, AugAssign, and Expr.
				exceptexpr = ast.ExceptExp(
					body=node.body[0].value,
					etype=node.handlers[0].type or ast.Name("BaseException", ast.Load()),
					value=node.handlers[0].body[0].value
				)
				node = node.body[0] # Should this do a deepcopy?
				node.value = exceptexpr
				f.write(sp + find_except_expr.dump(node).encode('ascii') + b"\n")
			# Optionally write out a comment block
			if explain:
				f.write(sp + b'# ' + line[len(sp):] + b'\n')
				if lineno == stop:
					f.write(sp + b"# End PEP 463 translation\n")

if __name__ == "__main__":
	for fn in sys.argv[1:]:
		search(fn)
