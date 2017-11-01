# coding: utf-8
#
#  Copyright © 2017 Leo Broska
#
#  This file is not part of Argh.
#
#  arghex is free software under terms of the GNU Lesser
#  General Public License version 3 (LGPLv3)
#
"""
Argh Extensions
~~~~~~~
"""

__version__ = '0.2'

import argparse
import argh
from argh.dispatching import ArghNamespace
from argh.constants import (ATTR_ALIASES, ATTR_ARGS, ATTR_NAME,
                            ATTR_WRAPPED_EXCEPTIONS,
                            ATTR_WRAPPED_EXCEPTIONS_PROCESSOR,
                            ATTR_EXPECTS_NAMESPACE_OBJECT)
from argh.compat import OrderedDict

__all__ = ['ArghParserWithUnknownArgs']


class ArghParserWithUnknownArgs(argh.ArghParser):
    """
    A subclass of :class:`ArghParser` with support for
    unknown arguments
    """
    unknown_args_var = ''

    def __init__(self, unknown_args_var, *args, **kwargs):
        self.unknown_args_var = unknown_args_var
        super(ArghParserWithUnknownArgs, self).__init__(*args, **kwargs)

    def parse_args(self, args=None, namespace=None):
        """
        Replacement for :meth:`ArgParser.parse_args`. It does
        two things:
        (1) It uses :meth:`parse_known_args` for retrieve known and
            unknown arguments and puts the unkponw ones in an argument
            of the the namespace
        (2) If `namespace`is not defined, the class
            :class:`argh.dispatching.ArghNamespace` is used. This is
            required for functions to be properly used as commands.
        """
        namespace = namespace or ArghNamespace()
        (namespace_obj, unknown_args) = super(ArghParserWithUnknownArgs, self).parse_known_args(args=args, namespace=namespace)
        namespace_obj.__dict__[self.unknown_args_var] = unknown_args
        return namespace_obj


def set_default_command(parser, function):
    """
    Replacement for :meth:`ArgParser.set_default_command`.
    It does add the parser's arg variable for the unknown args
    as suppressed argument to the function
    """
    def _get_option_from_var(var):
        return '--{0}'.format(var.replace('_', '-'))

    unknown_args_var = getattr(parser, 'unknown_args_var', None)
    if unknown_args_var is not None:
        unknown_args_suppress_dict = \
            {'help': argparse.SUPPRESS,
             'option_strings': (_get_option_from_var(unknown_args_var),)}
        # prepare for checking whether unknown_args is in function signature
        inferred_args = list(argh.assembling._get_args_from_signature(function))
        dests = OrderedDict()
        for argspec in inferred_args:
            dest = argh.assembling._get_parser_param_kwargs(parser, argspec)['dest']
            dests[dest] = argspec
        if argh.assembling._get_dest(parser, unknown_args_suppress_dict) in dests:
            declared_args = getattr(function, ATTR_ARGS, [])
            declared_args.insert(0, unknown_args_suppress_dict)
            setattr(function, ATTR_ARGS, declared_args)

    argh.set_default_command(parser, function)

