from richtext import RichTextDocument
from docx import Document
from docx.text.paragraph import Paragraph
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor
from docrun import DocRun, DocPara, adapt_into_paragraphs_from_rich_text


def is_heading(doc_para: DocPara) -> bool:
    for ps in doc_para.styles:
        if 'heading' in ps:
            return True

    return False


def get_heading_level(doc_para: DocPara) -> int:
    heading: str = ''

    for ps in doc_para.styles:
        if 'heading' not in ps:
            continue

        heading = ps
        break

    assert heading

    level = int(heading.replace('heading', ''))

    assert 0 <= level <= 9

    return level


def handle_text_alignment(paragraph: Paragraph, paragraph_styles: set[str]) -> None:
    alignment: str = ''

    for ps in paragraph_styles:
        if 'align' not in ps:
            continue

        alignment = ps
        break

    if not alignment:
        alignment = 'align-justify'

    alignment_str_to_enum_map: dict[str, WD_ALIGN_PARAGRAPH] = {
        'align-right': WD_ALIGN_PARAGRAPH.RIGHT,
        'align-centre': WD_ALIGN_PARAGRAPH.CENTER,
        'align-justify': WD_ALIGN_PARAGRAPH.JUSTIFY
    }

    paragraph.alignment = alignment_str_to_enum_map[alignment]


def handle_text_indentation(paragraph: Paragraph, paragraph_styles: set[str]) -> None:
    if 'blockquote' not in paragraph_styles:
        return

    paragraph.paragraph_format.left_indent = Pt(36)
    paragraph.paragraph_format.right_indent = Pt(36)


def make_heading(doc_para: DocPara, doc: Document) -> Paragraph:
    level: int = get_heading_level(doc_para)
    return doc.add_heading('', level)


def make_paragraph(doc_para, doc: Document) -> Paragraph:
    return doc.add_paragraph('')


def create_generic_paragraph(doc_para: DocPara, doc: Document) -> Paragraph:
    if is_heading(doc_para):
        to_call = make_heading
    else:
        to_call = make_paragraph

    paragraph: Paragraph = to_call(doc_para, doc)
    styles: set[str] = doc_para.styles

    handle_text_alignment(paragraph, styles)
    handle_text_indentation(paragraph, styles)

    return paragraph


def add_text_to_paragraph(runs: list[DocRun], paragraph: Paragraph) -> None:
    for run in runs:
        r = paragraph.add_run(run.text)

        if 'italic' in run.text_styles:
            r.italic = True

        if 'bold' in run.text_styles:
            r.bold = True


def handle_paragraphs(paragraphs: list[DocPara], doc: Document) -> None:
    for doc_para in paragraphs:
        paragraph: Paragraph = create_generic_paragraph(doc_para, doc)
        add_text_to_paragraph(doc_para.runs, paragraph)


def set_document_styles(doc: Document) -> None:
    styles = [
        doc.styles['Normal'],
        doc.styles['Heading 1'],
        doc.styles['Heading 2'],
        doc.styles['Heading 3'],
        doc.styles['Heading 4'],
        doc.styles['Heading 5'],
        doc.styles['Heading 6']
    ]

    sizes = [Pt(12), Pt(20), Pt(16), Pt(14), Pt(13), Pt(12), Pt(11)]

    for style, size in zip(styles, sizes):
        style.font.name = 'Arial'
        style.font.size = size
        style.font.color.rgb = RGBColor(0, 0, 0)


def to_docx(document: RichTextDocument, metadata: dict | None = None, **kwargs) -> None:
    title: str = metadata['title']
    publication: str = metadata['publication']
    date: str = metadata['date']

    fn: str = f'{title}.docx'
    paragraphs: list[DocPara] = adapt_into_paragraphs_from_rich_text(document)

    doc = Document()

    set_document_styles(doc)
    handle_paragraphs(paragraphs, doc)

    doc.save(fn)
