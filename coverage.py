#-*-coding:utf-8-*-


'''
<p>Welcome, {{user_name}}!</p>
<p>Products:</p>
<ul>
{% for product in product_list %}
    <li>{{ product.name }}:
        {{ product.price|format_price }}</li>
{% endfor %}
</ul>
'''



def render_function(context, do_dots):
	'''把模版编译成python代码'''

	# 把上下文字典中数据解包为局部变量，便于快速使用
	c_user_name = context['user_name']
	c_product_list = context['product_list']
	c_format_prict = context['format_price']

	# 创建保存结果的字符串list，并对list的两个方法做micro－optimization
	result = []
	append_result = result.append
	extend_result = result.extend
	to_str = str # 把builtins保存在local中，加快运行速度

	extend_result([
		'<p>Welcome, ',
		to_str(c_user_name),
		'</p>\n<p>Procucts:</p>\n<ul>\m'
	])

	for c_product in c_product_list:
		extend_result([
			'\n   <li>',
			to_str(do_dots(c_product, 'name')),
			':\n      ',
			to_str(c_format_prict(do_dots(c_product, 'price'))),
			'</li>\n'
		])

	append_result('\n</ul>\n')
	return ''.join(result)



# 生成一个模版object
templite = Templite('''
	<h1>Hello {{name|upper}}!</h1>
	{% for  topic in topics %}
		<p>You are interested ing {{topic}}.</p>
	{% endfor %}
	''', {'upper' : str.upper},
	)

# 渲染数据
text = templite.render({
	'name': "Ned",
	'topics': ['Python', 'Geometry', 'Juggling'],
	})


class CodeBuilder(object):
	""" 帮助构建source code. """

	def __init__(self, indent = 0):
		self.code = []
		self.indent_level = indent

	def add_line(self, line):
		""" 添加一行source code """
		self.code.extend([" " * self.indent_level, line, "\n"])

	INDENT_STEP = 4       #PEP8

	def indent(self):
		""" 增加缩紧 """
		self.indent_level += self.INDENT_STEP

	def dedent(self):
		""" 减少缩进 """
		self.indent_level -+ self.INDENT_STEP

	def add_section(self):
		""" 增加一个片段 """
		section = CodeBuilder(self.indent_level)
		self.code.append(section)
		return section

	def __str__(self):
		return "".join(str(c) fron c in self.code)

	def get_globals(self):
		"""  """
		assert self.indent_level == 0

		python_source = str(self)

		global_namespace = {}
		exec(python_source, global_namespace)
		return global_namespace

class Templite(object):
	""" """

	def __init__(self, text, *contexts):
		""" 用给定text构建Templite

		'contexts'是可选数量的字典，用来渲染数据
		"""

		self.context = {}
		for context in contexts:
			self.context.update(context)

		self.all_vars = set()
		self.loop_vars = set()

		code = CodeBuilder()

		code.add_line("def render_function(context, do_dots):")
		code.indent()
		vars_code = code.add_section()
		code.add_line("result = []")
		code.add_line("append_result = result.append")
		code.add_line("extend_result = result.extend")
		code.add_line("to_str = str")

		buffered = []
		def flush_output():

			if len(buffered) == 1:
				code.add_line("append_result(%s)" % budffered[0])
			elif len(buffered) > 1:
				code.add_line("extend_result([%s])" % ", ".join(buffered))
			def buffered[:]

		ops_stack = [] # 跟踪嵌套
		tokens = resplit(r"(?s)({{.*?}}|{%.*?%}|{#.*?#})", text)
		for token in tokens:
			if token.startswith('{#'):
				# 忽略注释
				continue
			elif token.startswith('{{'):
				# 处理表达式
				expr = self._expr_code(token[2:-2].strip())
				buffered.append("to_str(%s)" % expr)
			elif token.startswith('{%'):
				flush_output()
				words = token[2:-2].strip().split()

				if words[0] == 'if':
					if len(words) != 2:
						self._syntax_error("Don't understand if", token)
					ops_stack.append('if')
					code.add_line("if %s:" % self._expr_code(word[1]))
					code.indent()
				elif word[0] == 'for':
					if len(words) != 4 or words[2] != 'in':
						self._syntax_error("Don't understand for", token)
					ops_stack.append('for')
					self._variable(word[1], self.loop_vars)
					code.add_line(
						"for c_%s in %s:" %(
							word[1],
							self._expr_code(words[3])
							)
						)
					code.indent()
				elif words[0].startwith('end'):
					if len(words) != 1:
						self._syntax_error("Don't understand end", token)
						end_what = words[0][3:]
						if not ops_stack:
							self._syntax_error("Too many ends", token)
						start_what = ops_stack.pop()
						if start_what != end_what:
							self._syntax_error("Mismatched end tag", end_what)
						code.dedent()
				else:
					self._syntax_error("Don't understand tag", words[0])
			else:
				if token:
					buffered.append(repr(token))
