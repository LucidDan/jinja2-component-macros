from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _fixtures import TemplateFactory

# Tests to be added:
#  - check if regex detects value-less attribute correctly such as "novalidate" and "disabled"
#  - Does the regex ignore "raw"/"comment" blocks for replacement purposes?


def test_no_components_makes_no_changes(
    make_jinja_template: TemplateFactory,
) -> None:
    """A template with no 'component' tags should not be modified."""

    tmpl = make_jinja_template("""
        <div>Hello World</div>
        {% if something %}
            <p>Some conditional content</p>
        {% endif %}
    """)

    processed = tmpl.render(something=False)
    assert processed.strip() == "<div>Hello World</div>"


def test_imported_component_gets_substituted(
    make_jinja_template: TemplateFactory,
) -> None:
    """A template with a 'component' import causes that tag to be replaced with macro calls."""

    tmpl = make_jinja_template(
        """
                {% from "test_components.html" import Layout %}
                <Layout>
                <div>Hello World</div>
                </Layout>
            """,
        templates={
            "test_components.html": """{% macro Layout() %} {{ caller() }} {% endmacro %}""",
        },
    )

    processed = tmpl.render(something=False)
    assert processed.strip() == "<div>Hello World</div>"


def test_imported_component_gets_substituted_with_context(
    make_jinja_template: TemplateFactory,
) -> None:
    """A template with a 'component' import causes that tag to be replaced with macro calls."""

    tmpl = make_jinja_template(
        """
        {% from "test_components.html" import Layout with context %}
        <Layout>
        <div>Hello World</div>
        </Layout>
        """,
        templates={
            "test_components.html": """{% macro Layout() %} {{ caller() }} {% endmacro %}""",
        },
    )

    processed = tmpl.render(something=False)
    assert processed.strip() == "<div>Hello World</div>"


def test_imported_component_gets_substituted_without_context(
    make_jinja_template: TemplateFactory,
) -> None:
    """A template with a 'component' import causes that tag to be replaced with macro calls."""

    tmpl = make_jinja_template(
        """
        {% from "test_components.html" import Layout without context %}
        <Layout>
        <div>Hello World</div>
        </Layout>
    """,
        templates={
            "test_components.html": """{% macro Layout() %} {{ caller() }} {% endmacro %}""",
        },
    )

    processed = tmpl.render(something=False)
    assert processed.strip() == "<div>Hello World</div>"


def test_string_attributes_get_passed_correctly(
    make_jinja_template: TemplateFactory,
) -> None:
    """A template with a 'component' using attributes works correctly."""

    tmpl = make_jinja_template(
        """
        {% from "test_components.html" import Layout %}
        <Layout data="hello">
        </Layout>
        """,
        templates={
            "test_components.html": """{% macro Layout(data="") %}{{ data }}{{caller()}}{% endmacro %}""",
        },
    )

    processed = tmpl.render(something=False)
    assert processed.strip() == "hello"


def test_int_attributes_get_passed_correctly(
    make_jinja_template: TemplateFactory,
) -> None:
    """A template with a 'component' using attributes works correctly."""

    tmpl = make_jinja_template(
        """
        {% from "test_components.html" import Layout %}
        <Layout data=2>
        </Layout>
        """,
        templates={
            "test_components.html": """{% macro Layout(data) %}{{ data + 1 }}{{caller()}}{% endmacro %}""",
        },
    )

    processed = tmpl.render(something=False)
    assert processed.strip() == "3"


def test_object_attributes_get_passed_correctly(
    make_jinja_template: TemplateFactory,
) -> None:
    """A template with a 'component' using attributes works correctly."""

    tmpl = make_jinja_template(
        """
        {% from "test_components.html" import Layout %}
        <Layout data=data_obj>
        </Layout>
        """,
        templates={
            "test_components.html": """{% macro Layout(data) %}{{ data.value }}{{caller()}}{% endmacro %}""",
        },
    )

    class DataObject:
        value = 42

    processed = tmpl.render(data_obj=DataObject())
    assert processed.strip() == "42"


def test_object_attributes_get_passed_correctly_with_single_quotes(
    make_jinja_template: TemplateFactory,
) -> None:
    """A template with a 'component' using attributes works correctly."""

    tmpl = make_jinja_template(
        """
        {% from "test_components.html" import Layout %}
        <Layout data='data_obj'>
        </Layout>
        """,
        templates={
            "test_components.html": """{% macro Layout(data) %}{{ data.value }}{{caller()}}{% endmacro %}""",
        },
    )

    class DataObject:
        value = 42

    processed = tmpl.render(data_obj=DataObject())
    assert processed.strip() == "42"


def test_object_do_not_get_passed_with_double_quotes(
    make_jinja_template: TemplateFactory,
) -> None:
    """A template with a 'component' using attributes works correctly."""

    tmpl = make_jinja_template(
        """
        {% from "test_components.html" import Layout %}
        <Layout data="data_obj">
        </Layout>
        """,
        templates={
            "test_components.html": """{% macro Layout(data) %}{{ data.value }}{{caller()}}{% endmacro %}""",
        },
    )

    class DataObject:
        value = 42

    processed = tmpl.render(data_obj=DataObject())
    assert processed.strip() != "42"


def test_imported_component_gets_substituted_for_selfclosing(
    make_jinja_template: TemplateFactory,
) -> None:
    """A template with a 'component' import causes that tag to be replaced with macros for self-closing tags."""

    tmpl = make_jinja_template(
        """
        {% from "test_components.html" import Layout %}
        <Layout />
        """,
        templates={
            "test_components.html": """{% macro Layout() %} <div>hello</div> {% endmacro %}""",
        },
    )
    processed = tmpl.render(something=False)
    assert processed.strip() == "<div>hello</div>"


def test_string_attributes_get_passed_correctly_for_selfclosing(
    make_jinja_template: TemplateFactory,
) -> None:
    """A template with a 'component' using attributes works correctly."""

    tmpl = make_jinja_template(
        """
        {% from "test_components.html" import Layout %}
        <Layout data="hello" />
        """,
        templates={
            "test_components.html": """{% macro Layout(data="") %}{{ data }}{% endmacro %}""",
        },
    )

    processed = tmpl.render(something=False)
    assert processed.strip() == "hello"


def test_int_attributes_get_passed_correctly_for_selfclosing(
    make_jinja_template: TemplateFactory,
) -> None:
    """A template with a 'component' using attributes works correctly."""

    tmpl = make_jinja_template(
        """
        {% from "test_components.html" import Layout %}
        <Layout data=2 />
        """,
        templates={
            "test_components.html": """{% macro Layout(data) %}{{ data + 1 }}{% endmacro %}""",
        },
    )

    processed = tmpl.render(something=False)
    assert processed.strip() == "3"


def test_object_attributes_get_passed_correctly_for_selfclosing(
    make_jinja_template: TemplateFactory,
) -> None:
    """A template with a 'component' using attributes works correctly."""

    tmpl = make_jinja_template(
        """
        {% from "test_components.html" import Layout %}
        <Layout data=data_obj />
        """,
        templates={
            "test_components.html": """{% macro Layout(data) %}{{ data.value }}{% endmacro %}""",
        },
    )

    class DataObject:
        value = 42

    processed = tmpl.render(data_obj=DataObject())
    assert processed.strip() == "42"


def test_object_attributes_get_passed_correctly_for_selfclosing_with_single_quotes(
    make_jinja_template: TemplateFactory,
) -> None:
    """A template with a 'component' using attributes works correctly."""

    tmpl = make_jinja_template(
        """
        {% from "test_components.html" import Layout %}
        <Layout data='data_obj' />
        """,
        templates={
            "test_components.html": """{% macro Layout(data) %}{{ data.value }}{% endmacro %}""",
        },
    )

    class DataObject:
        value = 42

    processed = tmpl.render(data_obj=DataObject())
    assert processed.strip() == "42"


def test_object_do_not_get_passed_for_selfclosing_with_double_quotes(
    make_jinja_template: TemplateFactory,
) -> None:
    """A template with a 'component' using attributes works correctly."""

    tmpl = make_jinja_template(
        """
        {% from "test_components.html" import Layout %}
        <Layout data="data_obj" />
        """,
        templates={
            "test_components.html": """{% macro Layout(data) %}{{ data.value }}{% endmacro %}""",
        },
    )

    class DataObject:
        value = 42

    processed = tmpl.render(data_obj=DataObject())
    assert processed.strip() != "42"


def test_invalid_attribute_names_handled_correctly(
    make_jinja_template: TemplateFactory,
) -> None:
    """Attributes with invalid Python names should be handled properly."""

    tmpl = make_jinja_template(
        """
        {% from "test_components.html" import Component %}
        <Component valid-attr="valid" data-test="test" @event="handler" />
        """,
        templates={
            "test_components.html": """{% macro Component(valid_attr="") %}valid={{ valid_attr }}{{ kwargs|jcm_attr }}{% endmacro %}""",
        },
    )
    processed = tmpl.render()
    # valid_attr should be empty (wasn't passed as valid parameter)
    # but the invalid names should be in the _ parameter
    assert 'data-test="test"' in processed
    assert '@event="handler"' in processed
    assert 'valid-attr="valid"' in processed


def test_empty_attributes_handled_correctly(
    make_jinja_template: TemplateFactory,
) -> None:
    """Empty and None attributes should be handled properly."""

    tmpl = make_jinja_template(
        """
        {% from "test_components.html" import Component %}
        <Component empty_attr data-empty />
        """,
        templates={
            "test_components.html": """{% macro Component(empty_attr="") %}empty={{ empty_attr }}{{ kwargs|jcm_attr }}{% endmacro %}""",
        },
    )

    processed = tmpl.render()
    # Should handle valueless attributes properly
    assert 'data-empty=""' in processed
