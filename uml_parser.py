# Copyright 2018 Pedro Cuadra - pjcuadra@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
from lark import Lark, Tree
from sys import argv
import os


class ParserPythonClassDiagram(object):
    def __init__(self, class_digram, out_dir="./output"):
        grammar_file_path = os.path.join("grammar", "grammar.ebnf")
        with open(grammar_file_path) as f:
            parser = Lark(f.read())
        self._root = None
        with open(class_digram) as f:
            self._root = parser.parse(f.read())
        self._out_dir = out_dir

    @staticmethod
    def _find_items(tree: Tree, key: str):
        ret = []
        for children in tree.children:
            if children.data == key:
                ret.append(children)
        return ret

    @staticmethod
    def _find_item(tree: Tree, key: str):
        if tree is not None:
            for children in tree.children:
                if children.data == key:
                    return children
        return None

    @staticmethod
    def _item_to_string(tree: Tree):
        return str(tree.children[0])

    def _parse_argument(self, p: Tree):
        n = self._item_to_string(self._find_item(p, "var"))
        t = self._find_item(p, "type")
        if t is not None:
            t = self._parse_type(t)
        return n, t

    def _parse_type(self, t: Tree):
        is_dict = self._find_item(t, "dict")
        is_list = self._find_item(t, "list")
        if is_dict is not None:
            params = self._find_items(t, "type_name")
            t = "Dict[" + self._item_to_string(params[0]) + ", " + self._item_to_string(params[1]) + "]"
        elif is_list is not None:
            t = "List[" + self._item_to_string(self._find_item(t, "type_name")) + "]"
        else:
            t = self._item_to_string(self._find_item(t, "type_name"))
        return t

    def generate_objects(self):
        classes = self._root.find_data("class")
        enums = self._root.find_data("enum")
        interfaces = self._root.find_data("interface")
        relationships = self._root.find_data("relationship")

        rels = self._parse_relationships(relationships)
        self._parse_classes(classes, rels)

    def _parse_relationships(self, relationships):
        ret = []
        for r in relationships:
            c = self._find_item(r, "arrow_end_1")
            p = self._find_item(c, "package")
            package = self._item_to_string(p)
            p = self._find_item(c, "class_name")
            class_name = self._item_to_string(p)
            p = self._find_item(c, "separator")
            separator = self._item_to_string(p)
            from_class = package + separator + class_name
            c = self._find_item(r, "arrow_end_2")
            p = self._find_item(c, "package")
            package = self._item_to_string(p)
            p = self._find_item(c, "class_name")
            class_name = self._item_to_string(p)
            p = self._find_item(c, "separator")
            separator = self._item_to_string(p)
            to_class = package + separator + class_name
            p = self._find_item(r, "arrow_head_1")
            separator = self._item_to_string(p)
            p = self._find_item(r, "arrow_body")
            separator += self._item_to_string(p)
            if separator == "<|-":
                ret.append((to_class, from_class))
        return ret

    def _parse_classes(self, classes, rels):
        for c in classes:

            has_init = False

            p = self._find_item(c, "package")
            package = self._item_to_string(p)
            p = self._find_item(c, "class_name")
            class_name = self._item_to_string(p)
            p = self._find_item(c, "separator")
            separator = self._item_to_string(p)
            methods = self._find_items(c, "method")
            attributes = self._find_items(c, "attribute")

            full_name = class_name
            if package != "":
                # Create package
                try:
                    os.makedirs(os.path.join(self._out_dir, package))
                    with open(os.path.join(self._out_dir, package, "__init__.py"), "w") as f:
                        f.writelines(["# Package generated automatically", "\n"])
                except FileExistsError:
                    pass
                full_name = package + "." + class_name

            parent = "object"
            l = filter(lambda x: x[0] == full_name, rels)
            res = list(l)
            if len(res) > 0:
                f, t = res[0]
                from_class = t.split(separator)[1]
                parent = from_class

            msg = ["# Class generated automatically", "\n",
                   "class {class_name}({parent}):".format(class_name=class_name, parent=parent), "\n"]
            attribute_list = []
            for a in attributes:
                attribute_name = ""
                p = self._find_item(a, "private")
                if p is not None:
                    attribute_name = "_"
                p = self._find_item(a, "variable")
                n, t = self._parse_argument(p)
                attribute_list.append((attribute_name + n, t))

            for m in methods:
                is_init = False
                method_name = ""
                param_list = []
                p = self._find_item(m, "private")
                if p is not None:
                    method_name = "_"
                fn = self._find_item(m, "function")
                p = self._find_item(fn, "method_name")
                method_name += self._item_to_string(p)
                p = self._find_item(fn, "param_list")
                args = self._find_items(p, "variable")
                for a in args:
                    n, t = self._parse_argument(a)
                    param_list.append((n, t))

                if method_name == class_name:
                    method_name = "__init__"
                    has_init = True
                    is_init = True
                p = self._find_item(fn, "rtype")
                rtype = ""
                if p is not None:
                    rtype = " -> " + self._parse_type(p)
                msg.append("    def {method_name}(self".format(method_name=method_name.lower()))
                if len(param_list) > 0:
                    for n, t in param_list:
                        msg.append(", {name}: {type}".format(name=n, type=t))
                msg.extend([")" + rtype + ":", "\n"])
                if is_init:
                    for n, t in attribute_list:
                        msg.append("        self.{name} = None\n".format(name=n))
                    msg.append("\n")
                else:
                    msg.append("        pass\n\n")

            if not has_init and len(attribute_list) > 0:
                msg.append("    def {method_name}(self):\n".format(method_name="__init__".lower()))
                for n, t in attribute_list:
                    msg.append("        self.{name} = None\n".format(name=n))
                msg.append("\n")
            with open(os.path.join(self._out_dir, package, class_name.lower() + ".py"), "w") as f:
                f.writelines(msg)

            print(package + separator + class_name)


def getopts(argv):
    opts = {}  # Empty dictionary to store key-value pairs.
    while argv:  # While there are arguments left to parse...
        if argv[0][0] is '-':  # Found a "-name value" pair.
            if len(argv) > 1:
                if argv[1][0] != '-':
                    opts[argv[0]] = argv[1]
                else:
                    opts[argv[0]] = True
            elif len(argv) == 1:
                opts[argv[0]] = True

        # Reduce the argument list by copying it starting from index 1.
        argv = argv[1:]
    return opts


if __name__ == '__main__':
    myargs = getopts(argv)
    parser = ParserPythonClassDiagram(myargs['-i'])
    parser.generate_objects()
