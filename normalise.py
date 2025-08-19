import re
from send import DocNode
from string import whitespace


def strip(nodes: list[DocNode]) -> list[DocNode]:
    if not nodes:
        return nodes

    while nodes:
        node = nodes[0]
        node.text = node.text.lstrip()

        if not node.text:
            nodes.pop(0)
        elif node.text[0] not in whitespace:
            break

    while nodes:
        node = nodes[-1]
        node.text = node.text.rstrip()

        if not node.text:
            nodes.pop(-1)
        elif node.text[-1] not in whitespace:
            break

    return nodes


def collapse_newlines(nodes: list[DocNode]) -> list[DocNode]:
    for node in nodes:
        node.text = re.sub(r'\n\s*\n', '\n', node.text)

    for i in range(len(nodes) - 1):
        node = nodes[i]
        next_node = nodes[i + 1]

        if not node.text or not next_node.text:
            continue

        if node.text[-1] == '\n' and next_node.text[0] == '\n':
            next_node.text = next_node.text[1:]

    return nodes


def clean(nodes: list[DocNode]) -> list[DocNode]:
    replacements: dict[str, str] = {
        '\r': '',
        '“': '"',
        '”': '"',
        '‘': '\'',
        '’': '\'',
        '–': '—',
        ' —': '—',
        '— ': '—',
        '\u00A0': ' '
    }

    for node in nodes:
        for old, new in replacements.items():
            node.text = node.text.replace(old, new)

    return nodes


def invert_quotes(nodes: list[DocNode]) -> list[DocNode]:
    def sub_quotes(match) -> str:
        text: str = match.group(1)
        nested = list(re.finditer(r'(?<!\w)\'([^\']+)\'(?!\w)', text))

        text = text.replace('"', '\'')

        for match in nested:
            start, end = match.span(1)
            pre: str = text[:start - 1]
            post: str = text[end + 1:]
            quote: str = text[start:end]
            text = f'{pre}"{quote}"{post}'

        return text

    for node in nodes:
        node.text = re.sub(r'(".*?")', sub_quotes, node.text)

    return nodes


def merge(nodes: list[DocNode]) -> list[DocNode]:
    i: int = 0

    while i < len(nodes) - 1:
        node: DocNode = nodes[i]
        next_node: DocNode = nodes[i + 1]

        if node.styles == next_node.styles:
            node.text = node.text + next_node.text
            nodes.pop(i + 1)
        else:
            i += 1

    return nodes


def remove_empty(nodes: list[DocNode]) -> list[DocNode]:
    return [node for node in nodes if node.text]


def swap(nodes: list[DocNode], old: str, new: str) -> list[DocNode]:
    for node in nodes:
        if old in node.styles:
            node.styles.remove(old)
            node.styles.add(new)

    return nodes


def invalid_elements(nodes: list[DocNode]) -> list[DocNode]:
    invalid: set[str] = {'hr'}

    return [node for node in nodes if node.styles.isdisjoint(invalid)]
