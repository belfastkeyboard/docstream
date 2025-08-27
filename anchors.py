import re


def get_anchors_dict() -> dict[str, tuple[str, str]]:
    return {
        'italic': ('\uE000', '\uE001'),
        'bold': ('\uE002', '\uE003')
    }


def available_anchor_range() -> tuple[str, str]:
    return '\uE000', '\uF8FF'


def get_styles() -> list[str]:
    return list(get_anchors_dict().keys())


def get_anchor_pairs() -> list[tuple[str, str]]:
    return list(get_anchors_dict().values())


def get_style_anchors(style: str) -> tuple[str, str]:
    return get_anchors_dict()[style]


def get_open_anchor(style: str) -> str:
    return get_style_anchors(style)[0]


def get_anchors() -> str:
    return ''.join([a for v in get_anchors_dict().values() for a in v])


def get_all_anchors_pattern() -> str:
    return f'[{get_anchors()}]'


def remove_anchors(text: str) -> str:
    return re.sub(get_all_anchors_pattern(), '', text)


def has_style(text: str, style: str) -> bool:
    return get_open_anchor(style) in text


def wrap_text_in_style(text: str, style: str) -> str:
    start, end = get_style_anchors(style)
    return start + text + end


def split_on_style(text: str) -> tuple:
    match = re.search(get_all_anchors_pattern(), text)

    if not match:
        return ()

    index = match.start()

    return text[index], text[:index], text[index + 1:]


def is_open_anchor(anchor: str) -> bool:
    return anchor in {start for start, _ in get_anchor_pairs()}


def is_close_anchor(anchor: str) -> bool:
    return anchor in {end for _, end in get_anchor_pairs()}


def get_style_from_anchor(anchor: str) -> str:
    return {v: k for k, vals in get_anchors_dict().items() for v in vals}[anchor]
