import re
import requests
import nbformat
import json


def find_urls(text):
    # Regex pattern to match URLs, avoiding capture of markdown URL delimiters like ')' and ']'
    url_pattern = r"https?://[^\s)\]]+"
    # Finding all occurrences of pattern
    urls = re.findall(url_pattern, text)
    return urls


def extract_url_md_html(text):
    urls = []
    pattern = re.compile(
        r"(?P<url>https?://[^\s]+)|\[(?P<label>[^\]]+)\]\((?P<url2>https?://[^\s]+)\)"
    )
    for match in pattern.finditer(text):
        if match.group("url2"):
            urls.append(match.group("url2"))
        elif match.group("url2"):
            urls.append(match.group("url2"))
    return urls


def is_valid_url(url):
    try:
        print("trying " + url)
        response = requests.head(url)
        print(response.status_code)
        return response.status_code
    except requests.exceptions.RequestException:
        print("exception")
        return None


def format_output_md(urls_dict):
    result_as_md = "\n### Check URLs\n\n"
    result_as_stdout = "Check URLs"

    valid_count = 0
    invalid_404_count = 0
    invalid_other_count = 0

    urls_md = []

    for url, status_code in urls_dict.items():
        if status_code == 404:
            invalid_404_count += 1
            urls_md.append(f"Invalid URL (404): {url}")
        elif status_code == 200:
            valid_count += 1
            urls_md.append(f"Valid URL (200): {url}")
        else:
            invalid_other_count += 1
            urls_md.append(f"Invalid URL (Other - {status_code}): {url}")

    if invalid_404_count > 0:
        result_as_md += "\n> [!CAUTION]\n> **Invalid URLs are present, please review your linked urls.**\n\n"
        result_as_md += f"**Invalid URLs (404 - {invalid_404_count}):**\n\n"
        for url in urls_md:
            if "Invalid URL (404):" in url:
                # put the url without the "Invalid URL 404" part
                result_as_md += f"\n> [!WARNING]\n> **Invalid URL (404):** {url[19:]}\n"
        # result_as_md += (
        #     "\n".join([url for url in urls_md if "Invalid URL (404):" in url]) + "\n\n"
        # )

    if invalid_other_count > 0:
        result_as_md += f"\n**Impossible to verify (non-404 error code - {invalid_other_count}):**\n\n"
        result_as_md += (
            "\n".join([url for url in urls_md if "Invalid URL (Other" in url]) + "\n\n"
        )
        result_as_md += "> [!TIP]\n> Even if some of the urls listed above don't seem to be broken, try to replace them with the valid ones as they might become unavailable soon.\n\n"

    if valid_count > 0:
        result_as_md += f"**Valid URLs (200 - {valid_count}):**\n\n"
        result_as_md += (
            "\n".join([url for url in urls_md if "Valid URL (200):" in url]) + "\n\n"
        )

    if valid_count == 0 and invalid_404_count == 0 and invalid_other_count == 0:
        result_as_md += "No URLs found in the cells.\n"

    return result_as_md, result_as_stdout


def checkurls(contents, preview_url):
    urls_dict = {}

    # Convert JSON to notebook object
    json_str = json.dumps(contents)
    # Convert JSON string to notebook object
    notebook = nbformat.reads(json_str, as_version=4)

    for cell in notebook.cells:
        cell_urls = find_urls(cell.source)
        if cell_urls:
            for url in cell_urls:
                if url[-1] == ")" or url[-1] == "]":
                    url = url[:-1]
                status_code = is_valid_url(url)
                urls_dict[url] = status_code

    result_as_md, result_as_stdout = format_output_md(urls_dict)
    return result_as_md, result_as_stdout
