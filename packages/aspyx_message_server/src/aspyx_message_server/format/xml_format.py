import xml.etree.ElementTree as ET

from aspyx_message_server.push_interfaces.message_mapper import MessageMapper
from aspyx_message_server.push_interfaces.compiler import ClassContext, ExpressionCompiler, ParseContext

class XMLMapper(MessageMapper):
    def __init__(self, template, context: ParseContext):
        self.compiler = ExpressionCompiler()
        self.parse_context = context
        self.template = self.build_xml_template(template)

    def compile(self, expression):
        return self.compiler.parse(expression, self.parse_context)

    def build_xml_template(self, template):
        # Recursively compile template values and attribute expressions.
        result = {}
        for key, mapping in template.items():
            if key == "_attributes" and isinstance(mapping, dict):
                result[key] = {attr: self.compile(expr) for attr, expr in mapping.items()}
            elif isinstance(mapping, dict):
                result[key] = self.build_xml_template(mapping)
            else:
                result[key] = self.compile(mapping)
        return result

    def evaluate_xml_template(self, compiled, context):
        def build_element(tag, body):
            attributes = {}
            children = {}
            text = None
            for k, v in body.items():
                if k == "_attributes":
                    for attr, evalexpr in v.items():
                        attributes[attr] = str(evalexpr.eval(context))
                elif isinstance(v, dict):
                    children[k] = v
                else:
                    # Text value as direct scalar (or expression)
                    text = str(v.eval(context))
            elem = ET.Element(tag, attrib=attributes)
            for child_tag, child_body in children.items():
                sub_elem = build_element(child_tag, child_body)
                elem.append(sub_elem)
            if text is not None:
                elem.text = text
            return elem

        # Start from the root (top-level should be single key)
        if not compiled:
            return None
        if len(compiled) != 1:
            raise ValueError("Root XML must have one element")
        root_tag, root_body = list(compiled.items())[0]
        return build_element(root_tag, root_body)

    # override

    def create(self, instance) -> str:
        ctx = ClassContext(instance)
        elem = self.evaluate_xml_template(self.template, ctx)
        return ET.tostring(elem, encoding="unicode", method="xml")
