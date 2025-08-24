import jinja2

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("."),
    autoescape=True,
    extensions=["jinja2_component_macros.ComponentsExtension"],
)
