from richtext import RichTextDocument
from zipfile import ZipFile
from pathlib import Path
import shutil
from lxml import etree
from lxml.etree import Element, SubElement
import zipfile
import os
from .date import Date, get_formatted_date
from docrun import DocPara, adapt_into_paragraphs_from_rich_text
import re


IDML_DIR = Path('output', 'idml')
WORK_DIR = Path(IDML_DIR, 'working_dir')


def repack_idml(title: str) -> None:
    folder_path = WORK_DIR
    output_file = Path(f'{title}.idml')

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, folder_path)
                zf.write(full_path, rel_path)


def extract_idml() -> Path:
    work_dir: Path = WORK_DIR

    if work_dir.exists():
        shutil.rmtree(work_dir)

    work_dir.mkdir()

    idml_template = Path(IDML_DIR, 'template.idml')

    if not idml_template.exists():
        raise FileNotFoundError

    with ZipFile(idml_template, 'r') as z:
        z.extractall(work_dir)

    return work_dir


def read_xml(file: Path) -> etree:
    parser = etree.XMLParser(remove_blank_text=True)
    return etree.parse(file, parser)


def write_xml(file: Path, tree) -> None:
    tree.write(file,
               encoding="utf-8",
               xml_declaration=True,
               pretty_print=True)


def write_title(title: str) -> None:
    file = Path(WORK_DIR, 'Stories', 'Story_title.xml')
    tree = read_xml(file)
    root = tree.getroot()

    title_node = root.find('.//Content')
    title_node.text = title

    write_xml(file, tree)


def clear_body() -> None:
    file = Path(WORK_DIR, 'Stories', 'Story_body.xml')
    tree = read_xml(file)
    root = tree.getroot()

    for para in root.findall('.//ParagraphStyleRange'):
        parent = para.getparent()
        parent.remove(para)

    write_xml(file, tree)


def make_paragraph(parent, **kwargs) -> Element:
    paragraph = Element('ParagraphStyleRange',
                        **kwargs)

    parent.append(paragraph)

    return paragraph


def get_text_styles(styles: set[str]) -> dict[str, str]:
    text_styles_dict: dict[str, dict[str, str]] = {
        'italic': {'FontStyle': 'Italic'},
        'bold': {'AppliedFont': 'EB Garamond Bold'}
    }

    return {k2: v2 for k, v in text_styles_dict.items() if k in styles for k2, v2 in v.items()}


def get_paragraph_style(styles: set[str]) -> dict[str, str]:
    paragraph_styles_dict: dict[str, dict[str, str]] = {
        'blockquote': {'AppliedParagraphStyle': 'ParagraphStyle/Block Quote'},
        'align-right': {'AppliedParagraphStyle': 'ParagraphStyle/Byline'},
        'heading1': {'AppliedParagraphStyle': 'ParagraphStyle/Subtitle'},
        'heading2': {'AppliedParagraphStyle': 'ParagraphStyle/Subtitle'},
        'heading3': {'AppliedParagraphStyle': 'ParagraphStyle/Subtitle'},
        'heading4': {'AppliedParagraphStyle': 'ParagraphStyle/Subtitle'},
        'heading5': {'AppliedParagraphStyle': 'ParagraphStyle/Subtitle'},
        'heading6': {'AppliedParagraphStyle': 'ParagraphStyle/Subtitle'},
    }

    for style in styles:
        if style in paragraph_styles_dict:
            return paragraph_styles_dict[style]

    return {'AppliedParagraphStyle': 'ParagraphStyle/Body Text'}


def handle_quotes(text: str) -> str:
    # Leading apostrophe contractions e.g. ['tis] -> [’tis]
    text = re.sub(r"(?<![a-zA-Z])'(?=" + '|'.join(['tis', 'twas', 'twere', 'em', 'cause']) + r")", '’', text)

    # Contractions and singular possessives e.g [isn't] -> [isn’t]
    text = re.sub(r"(?<=\w)'(?=\w)", "’", text)

    # Apostrophes before numbers ['98] -> [’98]
    text = re.sub(r"'(?=\d)", "’", text)

    # Opening single quotes e.g. ['quote] -> [‘quote]
    text = re.sub(r"(^|[\s(\[{])'(?=\w)", r"\1‘", text)

    # Closing single quotes and plural possessives e.g. [plurals'] -> [plurals’]
    text = text.replace("'", "’")

    # Opening double quotes e.g. ["quote] -> [“quote]
    text = re.sub(r'(^|[\s(\[{])"(?=\S)', r'\1“', text)

    # Closing double quotes e.g. [quote"] -> [quote”]
    text = text.replace('"', '”')

    return text


def write_run(paragraph, text: str, **kwargs) -> None:
    char_style = SubElement(paragraph,
                            "CharacterStyleRange",
                            AppliedCharacterStyle="CharacterStyle/$ID/[No character style]",
                            **kwargs)

    content = SubElement(char_style, 'Content')

    if '"' in text or "'" in text:
        text = handle_quotes(text)

    content.text = text


def write_break(paragraph) -> None:
    SubElement(paragraph, 'Br')


def write_info(publication: str, date: str) -> None:
    file = Path(WORK_DIR, 'Stories', 'Story_body.xml')
    tree = read_xml(file)
    root = tree.getroot()

    date: Date = get_formatted_date(date)

    story = root.find('Story')
    paragraph = make_paragraph(story,
                               AppliedParagraphStyle='ParagraphStyle/Body Text',
                               FirstLineIndent='0',
                               Justification='CenterJustified')

    write_run(paragraph, publication, FontStyle='Italic', Tracking="25")
    write_run(paragraph, '—', Tracking="25")

    if date.day:
        write_run(paragraph, str(date.day), Tracking="25")
        write_run(paragraph, date.suffix, Position='Superscript', Tracking="25")
        write_run(paragraph, ' ', Tracking="25")

    write_run(paragraph, date.month, FontStyle='Italic', Tracking="25")
    write_run(paragraph, f', {date.year}.', Tracking="25")

    write_break(paragraph)
    write_break(paragraph)

    write_xml(file, tree)


def write_paragraph(story, doc_para: DocPara) -> None:
    style: dict[str, str] = get_paragraph_style(doc_para.styles)
    paragraph: Element = make_paragraph(story, **style)

    for run in doc_para.runs:
        styles: dict[str, str] = get_text_styles(run.text_styles)
        write_run(paragraph, run.text, **styles)

    write_break(paragraph)


def write_document(paragraphs: list[DocPara]) -> None:
    file = Path(WORK_DIR, 'Stories', 'Story_body.xml')
    tree = read_xml(file)
    root = tree.getroot()
    story = root.find('Story')

    for doc_para in paragraphs:
        write_paragraph(story, doc_para)

    write_xml(file, tree)


def to_idml(document: RichTextDocument, metadata: dict | None = None, **kwargs) -> None:
    extract_idml()

    title: str = metadata.get('title', '')
    publication: str = metadata.get('publication', '')
    date: str = metadata.get('date', '')

    paragraphs: list[DocPara] = adapt_into_paragraphs_from_rich_text(document)

    clear_body()
    write_title(title)
    write_info(publication, date)

    write_document(paragraphs)

    repack_idml(title)
