from typing import Any, Protocol

import jinja2
import pytest
from jinja2 import DictLoader

from jinja2_component_macros import ComponentsExtension


# Use Protocols here because the Callable syntax doesn't quite cut it
class EnvFactory(Protocol):
    def __call__(
        self, templates: dict[str, str] | None = None, **kwargs: Any
    ) -> jinja2.Environment: ...


class TemplateFactory(Protocol):
    def __call__(
        self, template: str, *, templates: dict[str, str] | None = None, **kwargs: Any
    ) -> jinja2.Template: ...


@pytest.fixture
def make_jinja_env() -> EnvFactory:
    def mkenv(templates: dict[str, str] | None = None, **kwargs: Any) -> jinja2.Environment:
        autoescape = kwargs.pop("autoescape", True)
        return jinja2.Environment(
            autoescape=autoescape,
            **kwargs,
            extensions=[ComponentsExtension],
            loader=DictLoader(templates) if templates else None,
        )

    return mkenv


@pytest.fixture
def jinja_env(make_jinja_env: EnvFactory, **kwargs: Any) -> jinja2.Environment:
    return make_jinja_env(**kwargs)


@pytest.fixture
def make_jinja_template(make_jinja_env: EnvFactory) -> TemplateFactory:
    def mktemplate(
        template: str, *, templates: dict[str, str] | None = None, **kwargs: Any
    ) -> jinja2.Template:
        env = make_jinja_env(templates, **kwargs) if templates else make_jinja_env(**kwargs)
        return env.from_string(template)

    return mktemplate
