import re
import base64
from urllib.parse import quote

def encode_notebook_url(url):
    # URL-encode the string
    url_encoded = quote(url, safe='')

    # Base64 encode the URL-encoded string
    base64_encoded = base64.b64encode(url_encoded.encode('utf-8')).decode('utf-8')

    # Replace '+' with '/' to match the desired result
    result = base64_encoded.replace('+', '/')

    return result

def process_github_url(value):
    github_regex = r'https?://(github\.com|raw\.githubusercontent\.com)/([A-Za-z0-9-_.]+)/([A-Za-z0-9-_.]+)/(blob/)?(.*)'
    match = re.match(github_regex, value)

    if match:
        domain, username, repo, _, filepath = match.groups()
        proxy_value = f'/proxy-githubusercontent/{username}/{repo}/{filepath}'
        result = {
            'value': value,
            'domain': domain,
            'proxyValue': proxy_value,
            'origin': 'github'
        }
    else:
        print('Origin is not fully supported, things can go wrong... value:', value)
        result = {'value': value, 'origin': 'unknown'}

    return result

def main():
    notebook_url = "https://github.com/C2DH/template_repo_JDH/blob/main/author_guideline_template.ipynb"

    result = process_github_url(notebook_url)
    encode = encode_notebook_url(result['proxyValue'])
    # Use the result as needed, for example:
    print(encode)

if __name__ == '__main__':
    main()
