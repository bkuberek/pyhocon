from pyparsing import Word, alphas, ZeroOrMore, alphanums, Optional, Or, Regex, Literal, oneOf, OneOrMore, Forward, \
    QuotedString, Suppress, delimitedList, Group, Dict, Keyword, replaceWith, Combine, nums, quotedString
from pyhocon.config_tree import ConfigTree, ConfigTreeParser


class ConfigParser(object):
    """
    Parse HOCON files: https://github.com/typesafehub/config/blob/master/HOCON.md
    """

    def parse(self, content):
        dict_expr = Forward()
        list_expr = Forward()
        assign_expr = Forward()

        true_expr = Keyword("true").setParseAction(replaceWith(True))
        false_expr = Keyword("false").setParseAction(replaceWith(False))
        null_expr = Keyword("null").setParseAction(replaceWith(None))

        key = Word(alphanums + '._')

        number_expr = Combine(Optional('-') + ('0' | Word('123456789', nums)) +
                              Optional('.' + Word(nums)) +
                              Optional(Word('eE', exact=1) + Word(nums + '+-', nums)))

        string_expr = QuotedString('"""', escChar='\\', multiline=True, unquoteResults=True) | QuotedString('"', escChar='\\') | Regex('.*')

        value_expr = number_expr | true_expr | false_expr | null_expr | string_expr
        list_expr << Group(Suppress('[') + OneOrMore(list_expr | value_expr | dict_expr) + Suppress(']'))

        # for a dictionary : or = is optional
        dict_expr << ConfigTreeParser(Suppress('{') + ZeroOrMore(assign_expr) + Suppress('}'))
        assign_dict_expr = key + Suppress(Optional(oneOf(['=', ':']))) + dict_expr
        assign_value_or_list_expr = key + Suppress(oneOf(['=', ':'])) + (value_expr | list_expr)
        assign_expr << Group(assign_dict_expr | assign_value_or_list_expr)

        config_expr = ConfigTreeParser(ZeroOrMore(assign_expr))
        return config_expr.parseString(content, parseAll=True)[0]
