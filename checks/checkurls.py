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
        return response.status_code
    except requests.exceptions.RequestException:
        return None


def format_output_md(urls_dict):
    result_as_md = "\n### Check URLs\n"
    result_as_stdout = ""

    valid_count = 0
    invalid_404_count = 0
    invalid_other_count = 0

    valid_urls_md = []
    invalid_404_urls_md = []
    invalid_other_urls_md = []

    for url, status_code in urls_dict.items():
        if status_code == 404:
            invalid_404_count += 1
            invalid_404_urls_md.append(f"- {url} returned a 404 status code.")
        elif status_code == 200:
            valid_count += 1
            valid_urls_md.append(f"- {url} is valid: {status_code}")
        else:
            invalid_other_count += 1
            invalid_other_urls_md.append(f"- {url} returned an unknown status code: {status_code}")

    if invalid_404_count > 0:
        result_as_md += f"**Invalid URLs (404 - {invalid_404_count}):**\n\n"
        result_as_md += "\n".join(invalid_404_urls_md) + "\n\n"
        result_as_stdout += f"Invalid URLs (404 - {invalid_404_count}):\n"
        result_as_stdout += "\n".join(invalid_404_urls_md) + "\n"

    if invalid_other_count > 0:
        result_as_md += f"**Impossible to verify (Other - {invalid_other_count}):**\n\n"
        result_as_md += "\n".join(invalid_other_urls_md) + "\n\n"
        result_as_stdout += f"Invalid URLs (Other - {invalid_other_count}):\n"
        result_as_stdout += "\n".join(invalid_other_urls_md) + "\n"

    if valid_count > 0:
        result_as_md += f"**Valid URLs (200 - {valid_count}):**\n\n"
        result_as_md += "\n".join(valid_urls_md) + "\n\n"
        result_as_stdout += f"Valid URLs (200 - {valid_count}):\n"
        result_as_stdout += "\n".join(valid_urls_md) + "\n"

    if valid_count == 0 and invalid_404_count == 0 and invalid_other_count == 0:
        result_as_md += "No URLs found in the cells.\n"
        result_as_stdout += "No URLs found in the cells."

    return result_as_md, result_as_stdout


def checkurls(contents):
    urls_dict = {}

    # Convert JSON to notebook object
    json_str = json.dumps(contents)
    # Convert JSON string to notebook object
    notebook = nbformat.reads(json_str, as_version=4)

    for cell in notebook.cells:
        cell_urls = extract_url_md_html(cell.source)
        if cell_urls:
            for url in cell_urls:
                if url[-1] == ')' or url[-1] == ']':
                    url = url[:-1]
                status_code = is_valid_url(url)
                urls_dict[url] = status_code

    result_as_md, result_as_stdout = format_output_md(urls_dict)
    return result_as_md, result_as_stdout