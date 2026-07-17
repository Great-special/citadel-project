from functools import lru_cache


def normalize_language_code(language_code):
    return (language_code or 'en').split('-', 1)[0]


def parse_content_key(key):
    page, separator, block = (key or '').partition('.')
    if not separator or not page or not block:
        raise ValueError(f"Static content key '{key}' must use the format 'page.block'")
    return page, block


@lru_cache(maxsize=512)
def _get_content_values(page, block):
    from .models import StaticContentBlock

    try:
        content_block = StaticContentBlock.objects.only(
            'content_en',
            'content_de',
            'is_rich_text',
        ).get(page=page, block=block)
    except StaticContentBlock.DoesNotExist:
        return None

    return {
        'content_en': content_block.content_en,
        'content_de': content_block.content_de,
        'is_rich_text': content_block.is_rich_text,
    }


def clear_static_content_cache():
    _get_content_values.cache_clear()


def get_static_content_value(key, language_code, default=''):
    try:
        page, block = parse_content_key(key)
    except ValueError:
        return default

    content_values = _get_content_values(page, block)
    if not content_values:
        return default

    language = normalize_language_code(language_code)
    if language == 'de' and content_values['content_de'].strip():
        return content_values['content_de']
    if content_values['content_en'].strip():
        return content_values['content_en']
    return default
