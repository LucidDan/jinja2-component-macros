# jinja2-component-macros

A package to bring component-oriented HTML to Jinja templates, powered by Jinja macros.

![PyPI version](https://img.shields.io/pypi/v/jinja2-component-macros)
![Python versions](https://img.shields.io/pyversions/jinja2-component-macros)
![License](https://img.shields.io/github/license/luciddan/jinja2-component-macros)

## Overview

This package provides a Jinja extension that preprocesses Jinja templates, replacing html 'component' tags with corresponding macro calls.
Tags eligible for replacement are selected based on the "import" statements at the start of the template.

I like this approach because HTML tags are easier to read than 'macro' and 'endmacro' statements, and work well with IDEs even without Jinja-specific support.

### With traditional Jinja macros

```jinja
{% from "components/cards.html" import Card, CardHeader %}
{% from "components/buttons.html" import Button %}

{% call Card(class="bg-blue") %}
  {% call CardHeader() %}Welcome to my card{% endcall %}
  {{ Button(text="Click me", url=ctx_url, variant="primary") }}
{% endcall %}
```

### Using jinja2-component-macros

```jinja
{% from "components/cards.html" import Card, CardHeader %}
{% from "components/buttons.html" import Button %}

<Card class="bg-blue">
  <CardHeader>Welcome to my card</CardHeader>
  <Button text="Click me" url='ctx_url' variant="primary" />
</Card>
```

## Installation

```bash
pip install jinja2-component-macros
```

## Usage

### Basic Setup

```python
from jinja2 import Environment
from jinja2_component_macros import ComponentsExtension

env = Environment(extensions=[ComponentsExtension])
```

### Creating Components

Create your components as regular Jinja macros, with whatever parameters you'd like to use.
A very simple example of a self-closing component:
```jinja
{# components.html #}
{% macro Header(text, class="") %}<h1 class="{{ class }}" {{ kwargs|jcm_attr }}>{{ text }}</h1>{% endmacro %}
```

Note the above does not use 'caller()', so it will only work as a self-closing component, like `<Header text="First Header"/>`.
A second version that also allows `<Header>First Header</Header>` might look like:

```jinja
{# components.html #}
{% macro Header(text="", class="") %}<h1 class="{{ class }}" {{ kwargs|jcm_attr }}>{{ caller() if caller else text }}</h1>{% endmacro %}
```

These examples also use a filter called `jcm_attr`, which is a specialized version of `xmlattr` that can expand the kwargs parameters,
but with some extra support for special characters that aren't valid in macro parameter names, for example AlpineJS "@click" and "x-on:load".
Meaning you can do things like: `<Header @click="open-page=true">First Header</Header>` and the '@click' attribute will be passed through to 
the component properly.
The way this is handled "under the hood" is that any special character parameters are passed as a dict to the '_' parameter. When jcm_attr expands
the kwargs, it looks for a "_" key and expands the value of that as additional kwargs parameters.

### Using Components

`jinja2-component-macros` only replaces HTML tags that are listed in `import` statements at the top of a template.

Import your components first, then use them in HTML:

```jinja
{% from "components.html" import Button, Card %}

{# Self-closing components #}
<Button text="Save" variant="primary" />

{# Container components #}
<Card title="User Profile" class="bg-light">
  <p>User information goes here</p>
  <OtherComponent>This does not get replaced by a macro call because OtherComponent wasn't imported</OtherComponent>
  <Button text="Edit Profile" variant="secondary" />
</Card>
```

## How It Works

Under the hood, the extension preprocesses the templates, makes a mapping of macro names to convert based on import statements,
then scans and converts any matching HTML tags into the appropriate Jinja macro calls:

- **Self-closing tags** (`<Component />`) become `{{ ComponentName() }}`
- **Container tags** (`<Component>...</Component>`) become `{% call ComponentName() %}...{% endcall %}`
- **Attributes** are passed as macro parameters
- **Attributes with invalid characters** (containing `-`, `:`, `@`, `.`) are collected as a dictionary and passed as a special `_` parameter

## Attribute Handling

Attributes are parsed in different ways depending on the type of quotes used - this is distinct from how HTML works, so it should be paid special attention.

- **Double quotes** (`"value"`) are passed as string literal values to macro parameters
- **Single quotes or unquoted** (`'value'` or `value`) are treated as Jinja Expressions, and are passed unquoted to macro parameters

As an example:

```jinja
{# Double quoted attributes... #}
<Button text="Click me" class="btn-primary" is_active="false" />
{# ...become... #}
{{ Button(text="Click me", class="btn-primary", is_active="false") }}

{# Single quoted or unquoted attributes... #}
{% set button_text="some text" %}
<Button text='button_text' is_active=false is_valid='false' count=42 />
{# ...become... #}
{{ Button(text=button_text, is_active=false, is_valid=false, count=42) }}
```

Especially note the different behaviour of "false" versus false or 'false'. 
The former is passed as a string, the latter as the actual boolean value for false. 

### Invalid Parameter Names

Attributes with invalid Python parameter names are collected in a special `_` parameter:

```jinja
<Button x-on:load=123 @click="handleClick" />
{# ...become... #}
{{ Button(_={"x-on:load": 123, "@click": "handleClick"}) }}
```

Note the same rules for quoting apply, so the unquoted 123 is treated as an expression (an integer), not as a string.

Access these in your macro using the `jcm_attr` helper filter:

```jinja
{% macro Button(text) %}
<button{{ kwargs|jcm_attr(autospace=true) }}>{{ text }}</button>
{% endmacro %}
```


## Helper Functions

The extension provides two helpful global functions:

### `jcm_attr(autospace=False)`

Converts a dictionary to HTML attribute string:

```jinja
{% macro Button() %}
<button {{ kwargs|jcm_attr }}>Click me</button>
{% endmacro %}

{# Usage: <Button data-id="123" class="btn" /> #}
{# Output: <button data-id="123" class="btn">Click me</button> #}
```

As with xmlattr, you can use autospace=True to make it add a space only when it returns text - if not, then it returns an empty string.

```jinja
{% macro Button() %}
<button{{ kwargs|jcm_attr(autospace=True) }}>Click me</button>
{% endmacro %}

{# Usage: <Button /> #}
{# Output: <button>Click me</button> #}
```


### `classx(*args)`

Conditionally joins CSS classes (similar to JavaScript's `clsx`):

```jinja
{% set button_classes = classx(
  "btn",
  {"btn-primary": variant == "primary"},
  {"btn-large": size == "lg"},
  extra_classes
) %}
<button class="{{ button_classes }}">{{ text }}</button>
```

## Known Issues

There are plenty of things to improve on this, but a couple of significant potential gotchas:
- There is currently no handling to ignore comment blocks e.g. `{# #}` - HTML tag substitution will be applied even inside a comment.

## Performance

An area to improve is benchmarking and performance, to look at performance comparisons between this, native macro usage, and other methods of components.
However, because this package does almost all its work in pre-processing, it is expected that it should perform almost the same as using macros directly.

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and [just](https://github.com/casey/just)
for task running.

```bash
# Setup development environment
just bootstrap

# Install dependencies
just install

# Run tests using tox
just test

# Run (roughly) the same checks that are run when checking a PR
just pr-checks
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.