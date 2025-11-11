import ast
import unittest

from aspyx_message_server.compiler import ParseContext, TypedFunction, ExpressionCompiler, EvalContext, ClassContext
from aspyx_message_server.format import JSONMapper, XMLMapper
from aspyx_message_server.message_dispatcher import Filter
from .model import Turnaround, Flight, Money

class TestCompiler(unittest.TestCase):
    #testEnvironment = Environment(SampleModule)

    def test_compile(self):
        expr = "a.b.c"
        tree = ast.parse(expr, mode="eval")
        print(ast.dump(tree, indent=2))
        print(1)

    def test_eval(self):
        expr = "num > 3 and length(id) > 0"

        parse_context = ParseContext(
            Turnaround,
            functions={
                "length": TypedFunction(lambda str: len(str), [str], int)
            }
        )

        parser = ExpressionCompiler()

        eval = parser.parse(expr, parse_context)

        # eval

        result = eval.eval(EvalContext(
            Turnaround(id="id", flight_id="123", num=1,price=Money(currency="EUR", value=1)),
            variables={
                "id": lambda : "id",
                "num": lambda : 7
            }
        ))

    def test_eval_class(self):
        expr = "num > 3 and length(id) > 0"

        parse_context = ParseContext(
            Turnaround,
            functions={
                "length": TypedFunction(lambda str: len(str), [str], int)
            }
        )

        parser = ExpressionCompiler()

        eval = parser.parse(expr, parse_context)
        turnaround = Turnaround(id="id", flight_id="123", num=1, price=Money(currency="EUR", value=1))

        result = eval.eval(ClassContext(turnaround))

        self.assertFalse(result)

        turnaround = Turnaround(id="id", flight_id="123", num=4, price=Money(currency="EUR", value=1))

        result = eval.eval(ClassContext(turnaround))

        self.assertTrue(result)

    def test_filter(self):
        parse_context = ParseContext(
            Turnaround,
            functions={
                "length": TypedFunction(lambda str: len(str), [str], int)
            }
        )
        filter = Filter("num > 0", context=parse_context)

        turnaround = Turnaround(id="id", flight_id="123", num=4, price=Money(currency="EUR", value=1))

        ok = filter.accepts(turnaround)

        self.assertTrue(ok)


    def test_json(self):
        turnaround = Turnaround(id="id", flight_id="123", num=4, price=Money(currency="EUR", value=1))

        parse_context = ParseContext(
            Turnaround,
            functions={
                "length": TypedFunction(lambda str: len(str), [str], int),
                "flight": TypedFunction(lambda id: Flight(id=id, iata=id+"iata"), [str], Flight)
            }
        )

        mapper = JSONMapper(template={
            "foo": "id",
            "currency": "price.currency",
            "bla": {
                "iata": "flight(flight_id).iata",
                "blu": "length(flight(flight_id).iata)",
                "num": "2 * num"
            }
        }, context=parse_context)

        json = mapper.create(turnaround)

        print(json)

    def test_xml(self):
        turnaround = Turnaround(id="id", flight_id="123", num=4, price=Money(currency="EUR", value=1))

        parse_context = ParseContext(
            Turnaround,
            functions={
                "length": TypedFunction(lambda str: len(str), [str], int),
                "flight": TypedFunction(lambda id: Flight(id=id, iata=id+"iata"), [str], Flight)
            }
        )

        mapper = XMLMapper(template={
            "message": {
                "foo": "id",
                "bla": {
                    "_attributes": {
                        "blu": "length(flight(flight_id).iata)"
                    },
                    "iata": "flight(flight_id).iata",

                    "num": "2 * num"
                }
            }
        }, context=parse_context)

        xml = mapper.create(turnaround)

        print(xml)


if __name__ == '__main__':
    unittest.main()