"""
The Extension
"""

from __future__ import annotations

import re

from jinja2 import Environment
from jinja2.ext import Extension

from jinja2_component_macros.helpers import classx, jcm_attr


class ComponentsExtension(Extension):
    """An extension to preprocess and convert html tags into macro calls."""

    regex = re.compile(
        r"{%\s+macro\s+(?P<macro>[^(]+)\(|{%\s*from\s+\"[^\"]+\"\s+import\s+(?P<imports>.+?)\s*(?:(?:with|without)\s+context\s*)?%}"
    )
    imports_regex = re.compile(r"(\w+)(?:\s+as\s+(\w+))?")

    attr_regex = re.compile(
        r'(?P<name>[^\s"\'>/=]+)(?:\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s"\'=<>`]+)))?'
    )
    invalid_attrname = re.compile(r"[@\-:.]")

    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)

        environment.globals["classx"] = classx
        environment.filters["jcm_attr"] = jcm_attr

    def preprocess(
        self,
        source: str,
        _name: str | None = None,
        _filename: str | None = None,
    ) -> str:
        components: dict[str, str] = {}
        regex = self.regex
        imports_regex = self.imports_regex

        for m in regex.finditer(source):
            macro_name = m.group("macro") or ""
            if macro_name:
                components[macro_name] = macro_name
            else:
                for macro_name, tag_name in imports_regex.findall(m.group("imports")):
                    # Note: when using 'from <file> import <macro>', tag_name is blank
                    #  Treat it as if it were written as '... import <macro> as <macro>'
                    components[tag_name or macro_name] = macro_name

        if not components:
            # Short circuit the rest
            return source

        # pre-process the source to replace the imported html tags with the appropriate macro call
        tag_list = "|".join(set(components.keys()))
        tags_regex = re.compile(
            rf"<(?P<tag>{tag_list})(?P<attrs>(?:\s+[a-zA-Z0-9-_:.@]+(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s\"'=<>`]+))?)*)\s*(?P<selfclosing>/?)>"
            rf"|</(?P<endtag>{tag_list})>"
        )
        attr_regex = self.attr_regex
        invalid_attrname = self.invalid_attrname

        def replace_tag(tagm: re.Match[str]) -> str:
            end_tag = tagm.group("endtag")
            if end_tag:
                return f"{{# </{end_tag}> #}}{{% endcall %}}"

            tag, attrs, selfclosing = tagm.group("tag", "attrs", "selfclosing")

            macro_name = components[tag]
            args = {}  # positional argument containing attributes that can't be parameter names
            kwargs = {}  # the rest of the arguments
            # If the attribute is double-quoted, its a string
            # If the attribute is unquoted or single-quoted, its an expression (or literal such as a number or bool)
            for (
                attr_raw_name,
                double_quoted,
                single_quoted,
                unquoted,
            ) in attr_regex.findall(attrs):
                if double_quoted:
                    attr_value = f'"{double_quoted}"'
                elif single_quoted:
                    attr_value = single_quoted
                else:
                    # Default, empty value; make sure it is a quoted empty string
                    attr_value = unquoted or '""'
                # Add it to args or kwargs depending on whether the name is allowed for a parameter or not
                if invalid_attrname.search(attr_raw_name):
                    args[attr_raw_name] = attr_value
                else:
                    kwargs[attr_raw_name.lower()] = attr_value

            if args:
                kwargs["_"] = "{" + ",".join(f'"{k}":{v}' for k, v in args.items()) + "}"
            params = ",".join(f"{k}={v}" for k, v in kwargs.items())
            if selfclosing == "/":
                # For self-closing, we're doing a macro function instead of a call tag
                return f"{{{{ {macro_name}({params}) }}}}"

            # If not self-closing, do a full call tag
            return f"{{# <{macro_name}> #}}{{% call {macro_name}({params}) %}}"

        # Some profiling is needed to work out if .sub() is the best option here
        return tags_regex.sub(replace_tag, source)
