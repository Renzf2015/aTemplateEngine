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
