"""
Version 2:  Tree and One dictionary. Save all leaves in one dictionary

Dictionary to store the number of TIMES that the page is crawled
url : times

Tree to store the number of DIFFERENT urls.
Node structure: (node_name, children_num, nodes_num, nonleaf_list)
	node_name: part of url
	children_num: num of children
	nodes_num: num of nodes of the sub-tree with this node as root 
	nonleaf_list: list for non-leaf node


"""

import re
import json

LEAF_UNKNOW = 10
LEAF_BRANCH_UNKNOW = 20


VISUAL_FILE = "visualiztion.txt"
DICT_JSON = "dict.json"
TREE_JSON = "tree.json"

"""
Func: Get standard url. If url is invalid, return False
WARNING: Temporarily only suppor "http://"
** This func can move outside and be used by other projects **
"""
def get_standard_url(url):
	pattern = re.compile(r"^http://.*")
	if not pattern.match(url):
		return False
	return re.sub(r"/*$", "", url)


class Node(object):
	def __init__(self, url = '', children_num = 0, nodes_num = 1, nonleaf_list = []):
		self.__node_name = url
		self.__children_num = children_num
		self.__nodes_num = nodes_num
		self.__nonleaf_list = nonleaf_list

	def get_name(self):
		return self.__node_name

	def get_ch_num(self):
		return self.__children_num

	def get_nd_num(self):
		return self.__nodes_num

	def get_nums(self):
		return self.__children_num, self.__nodes_num

	def get_list(self):
		return self.__nonleaf_list

	def get_list_str(self):
		if len(self.__nonleaf_list) == 0:
			return '[]'
		elem_strs = []
		for elem in self.__nonleaf_list:
			elem_strs.append('('+elem.get_name()+','+str(elem.get_ch_num())+','+str(elem.get_nd_num())+',[...])')
		return '[' + ','.join(elem_strs) + ']'

	def get_node_str(self):
		return '('+self.__node_name+','+str(self.__children_num)+','+str(self.__nodes_num)+', [...])'
	
	def add_leaf_node(self):
		self.__children_num += 1
		self.__nodes_num += 1

	def num_increase(self, children_num_increment, nodes_num_increment):
		self.__children_num += children_num_increment
		self.__nodes_num += nodes_num_increment



class URL_Store(object):
	def __init__(self):
		self.__root = Node("http:/")
		self.__url_dict = {}

	def is_exist(self, url):
		return url in self.__url_dict
	
	def init_with_url(self, root_name):
		self.__root = Node(root_name)

	def get_root(self):
		return self.__root

	"""
	the num always increase, so always from right to left
	"""
	def __add_nd_to_ls(self, node, n_list, start_position):
		if len(n_list) == 0:
			n_list.append(node)
			return 

		node_ch_num, node_nd_num = node.get_nums()
		while n_list[start_position - 1].get_nd_num() < node_nd_num:
			start_position -= 1
			if start_position <= 0:
				n_list.insert(0, node)
				return

		while n_list[start_position - 1].get_nd_num() == node_nd_num and n_list[start_position - 1].get_ch_num < node_ch_num:
			start_position -= 1
			if start_position <= 0:
				start_position = 0
				break
		n_list.insert(start_position, node)

	def __increased_nd_in_ls(self, node, n_list, position):
		if len(n_list) == 1:
			return
		if position == 0:
			return
		front_ch_num, front_nd_num = n_list[position-1].get_nums()
		node_ch_num, node_nd_num = node.get_nums()
		if (front_nd_num < node_nd_num) or (front_nd_num == node_nd_num and front_ch_num < node_nd_num):
			#FF  can be more efficient
			node = n_list.pop(position)
			self.__add_nd_to_ls(node, n_list, position) 

	def __tree_path_create(self, nleaf_list, path, start_index):
		#print("create*****" + '/'.join(path) + str(start_index))
		n = len(path)
		if n == start_index + 1:
			#nleaf_list.num_increase(1, 1)
			return 1

		tmp = Node(path[-2], 1, 2, [])
		i = n - 3
		while i >= start_index:
			tmp = Node(path[i], 1, n - i, [tmp])
			i -= 1
		self.__add_nd_to_ls(tmp, nleaf_list, len(nleaf_list))
		return n - start_index

	def __tree_path_update(self, father_node, path, start_index): 
		#print("update*****" + '/'.join(path) + str(start_index))
		if len(path) == start_index + 1:
			father_node.num_increase(1,1)
			return 1 #FF ?

		node_name = path[start_index]
		nleaf_list = father_node.get_list()
		index = 0
		for elem in nleaf_list:
			if elem.get_name() == node_name:
				increment = self.__tree_path_update(elem, path, start_index + 1)
				father_node.num_increase(0, increment)
				self.__increased_nd_in_ls(elem, nleaf_list, index)
				return increment
			index += 1
		front_part_url = '/'.join(path[:start_index + 1])
		#print(front_part_url+"@@@@@@@@@@@@@@@@"+'/'.join(path))
		if front_part_url in self.__url_dict:
			increment = self.__tree_path_create(nleaf_list, path, start_index)
			#print(father_node.get_name()+"$$$$$$$$$$$"+str(increment))
			father_node.num_increase(0, increment - 1)
			return increment - 1
		else:
			increment = self.__tree_path_create(nleaf_list, path, start_index)
			father_node.num_increase(1, increment)
			#self.__increased_nd_in_ls()
			return increment

	"""
	Func: STORE URL, that's store in tree and dictionary 
	"""
	def add_url(self, url):
		#FF split by /  etc....
		path = (url[7:]).split('/')
		path.insert(0, 'http:/')	
		if len(path) == 1:
			return 1

		if url in self.__url_dict:
			self.__url_dict[url] += 1  #FF
			return 0
		else:
			self.__url_dict[url] = 1  #FF
			if len(path) == 2:
				self.__root.num_increase(1, 1)
				return 1
			else:
				increment = self.__tree_path_update(self.__root, path, 1)
				return increment


	def __gen_visual_stream(self, node, depth):
		#print("!!!!!!!!!!!!!!!")
		#print(node.get_node_str()) ###
		#print("?????????")
		stream = "\t" * depth + node.get_node_str() + "\n"
		# dic = node.get_dict()
		# stream += "\t"*(depth+1) + ("\n" + "\t"*(depth+1)).join(dic.keys()) + "\n"
		ls = node.get_list()
		for elem in ls:
			stream += self.__gen_visual_stream(elem, depth + 1)
		return stream


	def visual(self):
		outstream = self.__gen_visual_stream(self.__root, 0) + "\n\n\n"
		for key in self.__url_dict:
			outstream += key + "\t\t" + str(self.__url_dict[key]) + "\n"
		with open(VISUAL_FILE, "w") as f:
			f.write(outstream + "\n\n\n#############\n\n\n")

	def __gen_list_outstream(self, ls):
		elem_strs = []
		for node in ls:
			elem_str = '{\"node_name\": \"'+node.get_name()+'\", \"children_num\":'+str(node.get_ch_num())+', \"nodes_num\": '+str(node.get_nd_num())+', \"nonleaf_list\":'+self.__gen_list_outstream(node.get_list())+'}'
			elem_strs.append(elem_str)
		return '[' + ', '.join(elem_strs) + ']'

	def output(self):
		outstream = json.dumps(self.__url_dict)
		with open(DICT_JSON, "w") as f:
			f.write(outstream)

		outstream = self.__gen_list_outstream([self.__root])
		with open(TREE_JSON, "w") as f:
			f.write(outstream)

