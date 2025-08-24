"""
Some helpers used in conjuction with the extension.
"""

from __future__ import annotations

import re
from itertools import chain
from typing import TYPE_CHECKING, Any

from jinja2 import Undefined, pass_eval_context
from markupsafe import Markup, escape

if TYPE_CHECKING:
    from jinja2.nodes import EvalContext


# Check for characters that would move the parser state from key to value.
# https://html.spec.whatwg.org/#attribute-name-state
_attr_key_re = re.compile(r"[\s/>=]", flags=re.ASCII)


@pass_eval_context
def jcm_attr(eval_ctx: EvalContext, d: dict[str, Any], *, autospace: bool = True) -> str:
    """Convert a set of arguments into HTML attributes. Adapted from xmlattr."""

    # Pop our _ arguments if there are any, and merge them into the dictionary
    kwargs = d.copy()
    args = kwargs.pop("_", {})
    attrs = []
    for key, value in (kwargs | args).items():
        if value is None or isinstance(value, Undefined):
            continue

        if _attr_key_re.search(key) is not None:
            msg = f"Invalid character in attribute name: {key!r}"
            raise ValueError(msg)

        attrs.append(f'{escape(key)}="{escape(value)}"')

    rv = " ".join(attrs)

    if autospace and rv:
        rv = " " + rv

    if eval_ctx.autoescape:
        return Markup(rv)  # noqa: S704

    return rv


def classx(*args: str | dict[str, str | bool], sep: str = " ") -> str:
    """Join arguments together if strings, if a dict then join keys if values are truthy."""

    data = []
    for arg in args:
        if not arg:
            continue
        if isinstance(arg, dict):
            data += [k for k, v in arg.items() if v]
        else:
            data.append(arg)

    return sep.join(set(chain.from_iterable(entry.split(sep) for entry in data)) - {""})
