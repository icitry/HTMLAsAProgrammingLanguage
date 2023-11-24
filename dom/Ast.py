from enum import Enum


class InstructionType(Enum):
    SCRIPT = 'script'
    FUNC = 'func'
    SIGN = 'sign'
    META = 'meta'
    PARAM = 'param'
    BLOCK = 'block'
    IF = 'if'
    ELSE_IF = 'elif'
    ELSE = 'else'
    COND = 'cond'
    FOR = 'for'
    INIT = 'init'
    INCR = 'incr'
    WHILE = 'while'
    RETURN = 'return'
    VAR = 'var'
    ASSIGN = 'assign'
    DECLVAR = 'declvar'
    LIT = 'lit'
    OP = 'op'
    PARENTHESES = 'parentheses'
    CALL = 'call'
    READ = 'read-cli'
    WRITE = 'write-cli'
    BREAK = 'break'
    LOG = 'log'
    UNKNOWN = ''

    @classmethod
    def from_string(cls, input_str):
        try:
            opt = cls(input_str)
            return cls[opt.name]
        except:
            return cls.UNKNOWN


class Node:
    def __init__(self, parent, node_type, data=None):
        self._node_type = node_type
        self._data = data
        self._parent = parent
        self._children = list()

    def append_child(self, child):
        self._children.append(child)

    def __str__(self):
        return f'Node [ Type: {self._node_type} | Data: {self._data} | Children: {len(self._children)} ]'

    @property
    def children(self):
        return self._children

    @property
    def type(self):
        return self._node_type

    @property
    def data(self):
        return self._data


class ScriptAst:
    def __init__(self, root):
        self._root = root
        self._parsed_root = None

    def _create_tree(self, src_node, dest_parent_node):
        node_type = InstructionType.from_string(src_node.nodeName)

        if node_type == InstructionType.UNKNOWN:
            return

        data = dict()
        if node_type == InstructionType.LIT or node_type == InstructionType.OP:
            data['value'] = src_node.firstChild.data
            if src_node.hasAttribute('type'):
                data['type'] = src_node.getAttribute('type')
        if node_type in [InstructionType.DECLVAR, InstructionType.SIGN, InstructionType.PARAM, InstructionType.VAR,
                         InstructionType.CALL, InstructionType.INCR] \
                and src_node.hasAttribute('name'):
            data['name'] = src_node.getAttribute('name')
        if node_type == InstructionType.META or node_type == InstructionType.FUNC:
            if src_node.hasAttribute('type'):
                data['type'] = src_node.getAttribute('type')

        curr_node = Node(parent=dest_parent_node, node_type=node_type, data=data)

        if dest_parent_node is None:
            self._parsed_root = curr_node
        else:
            dest_parent_node.append_child(curr_node)

        for child in src_node.childNodes:
            self._create_tree(child, curr_node)

    def _open_statement(self, node):
        if node.type == InstructionType.FUNC:
            if node.data.get('type') == 'async':
                return '\nasync function '
            return '\nfunction '

        if node.type == InstructionType.SIGN:
            return f"{node.data['name']}("

        if node.type == InstructionType.META:
            if node.data['type'] == 'cli-main':
                return '__writeToCli,__readFromCli,'

        if node.type == InstructionType.PARAM:
            return f"{node.data['name']},"

        if node.type == InstructionType.BLOCK:
            return " {\n"

        if node.type == InstructionType.DECLVAR:
            return f"let {node.data['name']}"

        if node.type == InstructionType.LIT:
            if node.data.get('type') == 'string':
                return f"\"{node.data['value']}\""
            else:
                return f"{node.data['value']}"

        if node.type == InstructionType.PARENTHESES:
            return '('

        if node.type == InstructionType.OP:
            return f"{node.data['value']}"

        if node.type == InstructionType.VAR:
            return f"{node.data['name']}"

        if node.type == InstructionType.ASSIGN:
            return "="

        if node.type == InstructionType.IF:
            return 'if '

        if node.type == InstructionType.ELSE_IF:
            return 'else if '

        if node.type == InstructionType.ELSE:
            return 'else '

        if node.type == InstructionType.WHILE:
            return 'while '

        if node.type == InstructionType.COND:
            return '('

        if node.type == InstructionType.RETURN:
            return 'return '

        if node.type == InstructionType.BREAK:
            return 'break'

        if node.type == InstructionType.READ:
            return 'await __readFromCli('

        if node.type == InstructionType.WRITE:
            return '__writeToCli('

        if node.type == InstructionType.LOG:
            return f"console.log("

        if node.type == InstructionType.CALL:
            return f"{node.data['name']}("

        if node.type == InstructionType.FOR:
            return f"for "

        if node.type == InstructionType.INIT:
            return f"(\n"

        if node.type == InstructionType.INCR:
            return f"\n; {node.data['name']}+="

        return ''

    def _close_statement(self, node):
        if node.type in [InstructionType.SIGN, InstructionType.PARENTHESES, InstructionType.COND, InstructionType.READ,
                         InstructionType.WRITE, InstructionType.LOG, InstructionType.CALL, InstructionType.INCR]:
            return ')'

        if node.type == InstructionType.BLOCK:
            return "\n}\n"

        if node.type == InstructionType.DECLVAR:
            return f"\n"

        if node.type == InstructionType.INIT:
            return f"; "

        return ''

    def _traverse_tree(self, node):
        tree_str = ''

        tree_str += self._open_statement(node)

        for child in node.children:
            tree_str += self._traverse_tree(child)

        if node.type in [InstructionType.SIGN, InstructionType.PARENTHESES, InstructionType.COND, InstructionType.READ,
                         InstructionType.WRITE, InstructionType.LOG, InstructionType.CALL, InstructionType.INCR] \
                and tree_str[-1] == ',':
            tree_str = tree_str[:-1]

        tree_str += self._close_statement(node)

        return tree_str

    def parse(self):
        self._create_tree(self._root, None)
        return self._parsed_root

    def to_string(self):
        return self._traverse_tree(self._parsed_root)
