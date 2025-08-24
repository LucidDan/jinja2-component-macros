from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from jinja2 import Environment

if TYPE_CHECKING:
    from _fixtures import TemplateFactory


def test_attributes_with_special_characters_collected_in_underscore(
    make_jinja_template: TemplateFactory,
) -> None:
    """Attributes with special characters should be collected in the _ parameter."""

    tmpl = make_jinja_template(
        """
        {% from "test_components.html" import Button %}
        <Button text="Click" data-id="123" @click="handle" :disabled="true" />
    """,
        templates={
            "test_components.html": """{% macro Button(text) %}{{ text }}{{ kwargs|jcm_attr }}{% endmacro %}""",
        },
    )

    processed = tmpl.render()
    # Should contain the special attributes as HTML attributes
    assert 'data-id="123"' in processed
    assert '@click="handle"' in processed
    assert ':disabled="true"' in processed


def test_jcm_attr_helper_function(
    make_jinja_template: TemplateFactory,
) -> None:
    """Test the jcm_attr helper function works correctly."""

    tmpl = make_jinja_template("""
        {% set attrs = {"data-id": "123", "class": "btn", "disabled": true} %}
        <div{{ attrs|jcm_attr }}>Content</div>
    """)

    processed = tmpl.render()
    assert 'data-id="123"' in processed
    assert 'class="btn"' in processed
    assert 'disabled="True"' in processed


def test_jcm_attr_skips_null_attrs(
    make_jinja_template: TemplateFactory,
) -> None:
    """Test the jcm_attr helper function skips attributes with None value"""

    tmpl = make_jinja_template("""
        {% set attrs = {"data-id": "123", "class": "btn", "disabled": none} %}
        <div{{ attrs|jcm_attr }}>Content</div>
    """)

    processed = tmpl.render()
    assert 'data-id="123"' in processed
    assert 'class="btn"' in processed
    assert "disabled=" not in processed


def test_jcm_attr_raises_on_invalid_attr(
    make_jinja_template: TemplateFactory,
) -> None:
    """Test the jcm_attr helper function raises a ValueError on invalid attributes"""

    tmpl = make_jinja_template("""
        {% set attrs = {"data-id": "123", "class": "btn", "invalid>": "123"} %}
        <div{{ attrs|jcm_attr }}>Content</div>
    """)

    with pytest.raises(ValueError, match="Invalid character in attribute name"):
        tmpl.render()


def test_jcm_attr_with_autoescape_off(
    make_jinja_template: TemplateFactory,
) -> None:
    """Test the jcm_attr helper function works normally in a jinja environment without autoescape"""

    tmpl = make_jinja_template(
        """
        {% set attrs = {"data-id": "123", "class": "btn"} %}
        <div{{ attrs|jcm_attr }}>Content</div>
    """,
        autoescape=False,
    )

    processed = tmpl.render()
    assert 'data-id="123"' in processed
    assert 'class="btn"' in processed


def test_jcm_attr_with_autospace(
    jinja_env: Environment,
) -> None:
    """Test the jcm_attr helper function raises a ValueError on invalid attributes"""

    tmpl = jinja_env.from_string("""{{ {}|jcm_attr(autospace=True) }}""")
    tmpl2 = jinja_env.from_string("""{{ {"foo": "bar"}|jcm_attr(autospace=True) }}""")

    processed = tmpl.render()
    processed2 = tmpl2.render()
    # When no content, does not add any space:
    assert processed == ""
    # When there is content, adds a space before the content:
    assert processed2 == ' foo="bar"'


def test_classx_helper_function(
    make_jinja_template: TemplateFactory,
) -> None:
    """Test the classx helper function works correctly."""

    tmpl = make_jinja_template("""
        {{ classx("btn", {"btn-primary": true, "btn-large": false}, "extra", "") }}
    """)

    processed = tmpl.render()
    # Should contain btn, btn-primary, and extra but not btn-large
    assert "btn" in processed
    assert "btn-primary" in processed
    assert "extra" in processed
    assert "btn-large" not in processed
