import re
import requests
import nbformat
import json



def extract_url_md_html(text):
    urls = []
    pattern = re.compile(r'(?P<url>https?://[^\s]+)|\[(?P<label>[^\]]+)\]\((?P<url2>https?://[^\s]+)\)')
    for match in pattern.finditer(text):
        if match.group('url2'):
            urls.append(match.group('url2'))
        elif match.group('url2'):
            urls.append(match.group('url2'))
    return urls




def is_valid_url(url):
    try:
        response = requests.head(url)
        return response.status_code in range(200, 400)
    except requests.exceptions.RequestException:
        return False


def format_output_md(urls, valid_urls):
    result_as_md = "\n### Check URLs\n"
    result_as_stdout = ""

    if urls:
        result_as_md += f"**WARNING: {len(urls)} cells contain URLs.**\n\n"
        for i, url in enumerate(urls):
            result_as_md += f"- {url} is valid: {valid_urls[i]}\n"
        result_as_stdout = f"WARNING: {len(urls)} cells contain URLs."
    else:
        result_as_md += "No URLs found in the cells.\n"
        result_as_stdout = "No URLs found in the cells."

    return result_as_md, result_as_stdout


def checkurls(contents):
    urls = []
    valid_urls = []
    # Convert JSON to notebook object
     # Convert dictionary to JSON string
    json_str = json.dumps(contents)
    # Convert JSON string to notebook object
    notebook = nbformat.reads(json_str, as_version=4)
    for cell in notebook.cells:
        cell_urls = extract_url_md_html(cell.source)
        if cell_urls:
            for url in cell_urls:
                if url[-1] == ')' or url[-1] == ']':
                    url = url[:-1]
                valid = is_valid_url(url)
                urls.append(url)
                valid_urls.append(valid)

    result_as_md, result_as_stdout = format_output_md(urls, valid_urls)

    return result_as_md, result_as_stdout
