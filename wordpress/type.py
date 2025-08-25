from bs4 import Tag
from bs4.element import PageElement


class WPNode:
    block_map: dict[str, str] = {
        'p': 'paragraph',
        'h1': 'heading',
        'h2': 'heading',
        'h3': 'heading',
        'h4': 'heading',
        'h5': 'heading',
        'h6': 'heading',
        'blockquote': 'quote',
        'hr': 'separator',
        # 'ul': 'list {"ordered":false}',
        # 'ol': 'list {"ordered":true}',
        # 'li': 'list-item',
        # 'pre': 'code',
        # 'code': 'code',
        # 'img': 'image',
        # 'table': 'table'
    }

    attr_map: dict[str, str] = {
        'h1': ' {"level":1}',
        'h2': ' {"level":2}',
        'h3': ' {"level":3}',
        'h4': ' {"level":4}',
        'h5': ' {"level":5}',
        'h6': ' {"level":6}',
    }

    wrapper_blocks: dict[str] = {'blockquote': ['wp-block-quote']}

    def __init__(self, tag: PageElement, indent: int = 0):
        assert isinstance(tag, Tag)

        tag_name = tag.name
        block_name: str = WPNode.block_map[tag_name]
        block_attr: str = WPNode.attr_map.get(tag_name, '')

        if tag_name in WPNode.wrapper_blocks:
            copy = tag.copy_self()
            copy['class'] = WPNode.wrapper_blocks[tag_name]
            copy.string = '|||'
            open_tag, close_tag = str(copy).split('|||')
            children = [WPNode(child, indent + 1) for child in tag.contents]
            string: str = '\n\n'.join([str(child) for child in children])
            content: str = f'{open_tag}\n{string}\n{close_tag}'
        else:
            content = str(tag)

        block_pre: str = f'<!-- wp:{block_name}{block_attr} -->'
        block_post: str = f'<!-- /wp:{block_name} -->'
        indentation: str = '\t' * indent
        separator: str = '\n' + indentation

        self.string: str = indentation + separator.join([block_pre, content, block_post])

    def __str__(self):
        return self.string

