import helper


def marxists_style() -> dict[str, str]:
    return {
        'author': '"align":"right"'
    }


def get_style_table(transform: str = '', **kwargs) -> dict[str, str]:
    if not transform:
        return {}

    transform = helper.source(transform)

    if transform == 'marxists':
        return marxists_style()

    raise ValueError(f'{transform} not recognised')


def get_name_translator() -> dict[str, str]:
    return {
        'p': 'paragraph',
        'h1': 'heading',
        'h2': 'heading',
        'h3': 'heading',
        'h4': 'heading',
        'h5': 'heading',
        'h6': 'heading',
        'ul': 'list',
        'ol': 'list',
        'blockquote': 'quote',
        'pre': 'code',
        'table': 'table',
        'hr': 'separator',
    }
