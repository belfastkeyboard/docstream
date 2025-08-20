from bs4 import Comment, Tag
from bs4.element import AttributeValueList
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


def make_style_wordpress_compliant(tree: Tag, **kwargs) -> None:
    table: dict[str, str] = get_style_table(**kwargs)
    name_translation: dict[str, str] = get_name_translator()
    tags = tree.find_all(class_=table.keys())

    for tag in tags:
        if not isinstance(tag, Tag):
            continue

        keys = [k for k in tag['class'] if k in table]
        values = [table[k] for k in tag['class'] if k in table]
        name: str = name_translation[tag.name]

        pre = Comment(f'<!-- wp:{name} {{{",".join(values)}}} -->')
        post = Comment(f'<!-- /wp:{name} -->')

        tag.insert_before(pre)
        tag.insert_after(post)

        update = set(tag['class']).difference(set(keys))
        tag['class'] = AttributeValueList(update)

        if not update:
            del tag['class']
