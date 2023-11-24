from xml.dom import minidom
from xml.etree import ElementTree

from dom import ScriptAst


class DomParser:
    def __init__(self, src):
        self._src = src

        self._dom = {
            'script': list(),
            'head': None,
            'body': None,
        }

    def _remove_whitespace(self, node):
        if node.nodeType == minidom.Node.TEXT_NODE:
            if node.nodeValue.strip() == "":
                node.nodeValue = ""
        for child in node.childNodes:
            self._remove_whitespace(child)

    def _parse_jsx_script_subtree(self, node):
        ast = ScriptAst(node)
        ast.parse()
        return ast.to_string()

    def _parse_default_script_subtree(self, node):
        elem_attributes = dict(node.attributes.items())
        script_node = ElementTree.Element('script', **elem_attributes)
        return script_node

    def _create_cli_elem(self, src_node, parent_node):
        elem_attributes = dict()

        if src_node.hasAttribute('main'):
            elem_attributes['main'] = '{' + src_node.getAttribute('main') + '}'

        ElementTree.SubElement(parent_node, 'Cli', **elem_attributes)

    def _create_call_elem(self, src_node, parent_node):
        elem_attributes = dict()

        if src_node.hasAttribute('name'):
            elem_attributes['call'] = src_node.getAttribute('name') + '('

        for child in src_node.childNodes:
            if child.nodeName == 'param' and child.hasAttribute('name'):
                elem_attributes['call'] += child.getAttribute('name') + ','
            if child.nodeName == 'lit' and child.nodeType == minidom.Node.TEXT_NODE and len(child.data) > 0:
                elem_attributes['call'] += child.data + ','

        if elem_attributes['call'][-1] == ',':
            elem_attributes['call'] = elem_attributes['call'][:-1]
        elem_attributes['call'] += ')'

        ElementTree.SubElement(parent_node, 'div', **elem_attributes)

    def _parse_html_subtree(self, src_node, dest_parent_node):
        if src_node.nodeName == 'script':
            if src_node.getAttribute('type') == 'jsx':
                script = self._parse_jsx_script_subtree(src_node)
                script = {
                    'type': 'jsx',
                    'script': script
                }
            else:
                script = self._parse_default_script_subtree(src_node)
                script = {
                    'type': 'default',
                    'script': script
                }

            self._dom['script'].append(script)
            return

        if src_node.nodeName == 'cli':
            self._create_cli_elem(src_node, dest_parent_node)
            return

        if src_node.nodeName == 'call':
            self._create_call_elem(src_node, dest_parent_node)
            return

        if src_node.nodeType == minidom.Node.TEXT_NODE:
            dest_parent_node.text = src_node.data
            return

        if src_node.nodeName not in ['head', 'body']:
            elem_attributes = dict()

            if src_node.attributes is None:
                return

            for key, value in dict(src_node.attributes.items()).items():
                if key == 'bind' and src_node.nodeName == 'input':
                    elem_attributes['bind:value'] = '{' + value + '}'
                elif key.startswith('on') and len(key) > 2:
                    elem_attributes[f'on:{key[2:]}'] = '{' + value + '}'
                else:
                    elem_attributes[key] = value

            curr_node = ElementTree.SubElement(dest_parent_node, src_node.nodeName, **elem_attributes)
        else:
            curr_node = dest_parent_node

        for child in src_node.childNodes:
            self._parse_html_subtree(child, curr_node)

    def _parse_main_tree_tags(self, node):
        for tag in ['head', 'body']:
            if node.nodeName == tag:
                self._dom[tag] = ElementTree.Element(tag)
                self._parse_html_subtree(node, self._dom[tag])
                self._dom[tag] = ElementTree.ElementTree(self._dom[tag])
                return

        for child in node.childNodes:
            self._parse_main_tree_tags(child)

    def parse(self):
        document = minidom.parse(file=self._src)
        self._remove_whitespace(document)
        document.normalize()
        self._parse_main_tree_tags(document)

    @property
    def dom(self):
        return self._dom
