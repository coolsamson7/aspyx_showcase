import json

from aspyx_message_server.message_mapper import MessageMapper
from aspyx_message_server.compiler import ExpressionCompiler, ParseContext, ClassContext

class JSONMapper(MessageMapper):
    def __init__(self, template, context: ParseContext):
        self.compiler = ExpressionCompiler()
        self.parse_context = context

        # replace the values with functions

        self.template = self.build_json_dict(template)


    # internal

    def compile(self, expression):
        return self.compiler.parse(expression, self.parse_context)

    def build_json_dict(self, template):
        result = {}

        for key, mapping in template.items():
            if isinstance(mapping, dict):
                # nested object
                result[key] = self.build_json_dict(mapping)
            else:
                result[key] = self.compile(mapping)

        return result

    def evaluate_json_dict(self, compiled_template, context):
        result = {}

        for key, value in compiled_template.items():
            if isinstance(value, dict):
                # recurse into nested dict
                result[key] = self.evaluate_json_dict(value, context)
            else:
                # evaluate callable
                result[key] = value.eval(context)

        return result

    # override

    def create(self, instance) -> str:
        tree = self.evaluate_json_dict(self.template, ClassContext(instance))

        return json.dumps(tree, indent=2)

