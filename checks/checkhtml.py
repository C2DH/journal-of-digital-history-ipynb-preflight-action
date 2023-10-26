from html.parser import HTMLParser
import requests
import nbformat
import json

class MyHTMLParser(HTMLParser):
    verbose = False  # Define verbose as a class-level constant

    def __init__(self, cell_number):
        super().__init__()
        self.cell_number = cell_number
        self.ignore_data = False
        self.ignore_author = False
        self.ignore_div_cite = False
        self.result_md = ""
        self.result_stdout = ""

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'div':
            for attr, value in attrs:
                if attr.lower() == 'class' and 'cite2c-biblio' in value:
                    self.ignore_div_cite = True
                    break
        elif tag.lower() == 'author':
            if self.ignore_data:
                return  # If we are already ignoring data within <div class="cite2c-biblio">, skip processing <author>
            self.ignore_author = True

        # Check if '©' symbol appears in the entire text before the <author> tag
        if not self.ignore_author:
            text_before_tag = self.get_starttag_text()
            pos = text_before_tag.find('<author')
            if pos > -1:
                text_before_author = text_before_tag[:pos]
                if '©' in text_before_author:
                    self.ignore_author = True

        if not self.ignore_author and not self.ignore_div_cite and tag.lower() != 'cite':
            self.result_md += f"- Cell {self.cell_number} - Encountered a start tag: {tag}\n"
            self.result_stdout += f"Cell {self.cell_number} - Encountered a start tag: {tag}"

    def handle_endtag(self, tag):
        if tag.lower() == 'div':
            self.ignore_data = False
            self.ignore_div_cite = False
        elif tag.lower() == 'author':
            self.ignore_author = False
        elif tag.lower() != 'cite':
            self.result_md += f"- Cell {self.cell_number} - Encountered an end tag: {tag}\n"
            self.result_stdout += f"Cell {self.cell_number} - Encountered an end tag: {tag}"

    def handle_data(self, data):
        if not self.ignore_data and not self.ignore_author:
            if MyHTMLParser.verbose:  # Access the class-level verbose constant
                self.result_md += f"  Data inside tag: {data.strip()}\n"
                self.result_stdout += f"  Data inside tag: {data.strip()}\n"
            else:
                pass  # Here you can process or ignore the data within the relevant tags


def extract_html(text, cell_number):
    parser = MyHTMLParser(cell_number)
    parser.feed(text)
    return parser.result_md, parser.result_stdout

def checkhtml(contents, preview_url):
    result_as_md = "\n### Check HTML\n"
    result_as_stdout = ""

    # Convert JSON to notebook object
    json_str = json.dumps(contents)
    notebook = nbformat.reads(json_str, as_version=4)

    for i, cell in enumerate(notebook.cells):
        result_md, result_stdout = extract_html(cell.source, i + 1)
        result_as_md += result_md
        result_as_stdout += result_stdout

    return result_as_md, result_as_stdout