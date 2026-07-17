from django import template
from django.template import Node, TemplateSyntaxError
from django.urls import translate_url
from django.utils.safestring import mark_safe

from core.static_content import get_static_content_value


register = template.Library()


def _language_code_from_context(context):
    request = context.get('request')
    if request and getattr(request, 'LANGUAGE_CODE', None):
        return request.LANGUAGE_CODE
    return context.get('LANGUAGE_CODE', 'en')


@register.simple_tag(takes_context=True)
def copy_text(context, key, default=''):
    return get_static_content_value(key, _language_code_from_context(context), default)


@register.simple_tag(takes_context=True)
def copy_html(context, key, default=''):
    return mark_safe(get_static_content_value(key, _language_code_from_context(context), default))


@register.simple_tag(takes_context=True)
def switch_language_url(context, language_code):
    request = context.get('request')
    if not request:
        return '/'
    return translate_url(request.get_full_path(), language_code)


class StaticCopyNode(Node):
    def __init__(self, key, nodelist, variable_name=None, render_safe=False):
        self.key = key
        self.nodelist = nodelist
        self.variable_name = variable_name
        self.render_safe = render_safe

    def render(self, context):
        default = self.nodelist.render(context).strip()
        key = self.key.resolve(context)
        content = get_static_content_value(key, _language_code_from_context(context), default)
        if self.variable_name:
            context[self.variable_name] = content
            return ''
        if self.render_safe:
            return mark_safe(content)
        return content


def _parse_static_copy(parser, token, render_safe):
    bits = token.split_contents()
    if len(bits) not in {2, 4}:
        raise TemplateSyntaxError(
            f"{bits[0]} requires a key and optionally 'as variable_name'."
        )

    variable_name = None
    if len(bits) == 4:
        if bits[2] != 'as':
            raise TemplateSyntaxError(
                f"{bits[0]} only supports the syntax '{{% {bits[0]} \"page.block\" as variable_name %}}'."
            )
        variable_name = bits[3]

    key = parser.compile_filter(bits[1])
    nodelist = parser.parse((f'end{bits[0]}',))
    parser.delete_first_token()
    return StaticCopyNode(key, nodelist, variable_name=variable_name, render_safe=render_safe)


@register.tag(name='static_copy')
def do_static_copy(parser, token):
    return _parse_static_copy(parser, token, render_safe=False)


@register.tag(name='static_copy_html')
def do_static_copy_html(parser, token):
    return _parse_static_copy(parser, token, render_safe=True)
