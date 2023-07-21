# Method to check the citation in the article
# <cite data-cite="9139636/BVE4ATFK"></cite>
# identify <cite data-cite="undefined"></cite>
# display the key to replace from the metadata information
# identify if bibliography is generated : <div class=\"cite2c-biblio\"></div>


import nbformat
import json
import re

def get_citation_info(citation_id, general_metadata):
    citation_info = general_metadata.get('cite2c', {}).get('citations', {}).get(citation_id)

    if not citation_info:
        return "Citation ID not found.", "Citation ID not found."

    result_as_md = f"\n#### Citation Information for ID: {citation_id}\n"
    result_as_md += "- Title: {}\n".format(citation_info.get('title', 'N/A'))
    result_as_md += "- Type: {}\n".format(citation_info.get('type', 'N/A'))
    result_as_md += "- URL: {}\n".format(citation_info.get('URL', 'N/A'))

    author_info = citation_info.get('author')
    if author_info:
        authors = ", ".join([f"{author['given']} {author['family']}" for author in author_info])
        result_as_md += f"- Author(s): {authors}\n"

    issued_info = citation_info.get('issued')
    if issued_info:
        year = issued_info.get('year', 'N/A')
        result_as_md += f"- Year: {year}\n"

    publisher = citation_info.get('publisher', 'N/A')
    result_as_md += f"- Publisher: {publisher}\n"

    event_place = citation_info.get('event-place', 'N/A')
    result_as_md += f"- Event Place: {event_place}\n"

    publisher_place = citation_info.get('publisher-place', 'N/A')
    result_as_md += f"- Publisher Place: {publisher_place}\n"

    result_as_md += "- Accessed Date: {}/{}/{}\n".format(
        citation_info.get('accessed', {}).get('day', 'N/A'),
        citation_info.get('accessed', {}).get('month', 'N/A'),
        citation_info.get('accessed', {}).get('year', 'N/A')
    )

    result_as_stdout = "Citation information found for ID: {}.".format(citation_id)

    return result_as_md, result_as_stdout


def checkcitation(contents):
    citations = set()

    # Convert JSON to notebook object
    json_str = json.dumps(contents)
    notebook = nbformat.reads(json_str, as_version=4)

    # Regular expression pattern to find the <cite> tags
    cite_pattern = r'<cite data-cite="([^"]+)"></cite>'

    for cell in notebook.cells:
        if cell.cell_type == 'markdown':
            # Search for <cite> tags in the markdown cell's source
            matches = re.findall(cite_pattern, cell.source)
            if matches:
                citations.update(matches)

    if citations:
        # Extract general metadata
        general_metadata = notebook.metadata
        result_as_md = "\n### Citations Found with problem:\n"
        for citation in citations:
            if citation == "undefined":
                result_as_md += f"- {citation}\n"
                result_as_md_citation, result_as_stdout_citation  = get_citation_info(citation, general_metadata)
                result_as_md += result_as_md_citation
        result_as_stdout = "Citations found in the notebook."
    else:
        result_as_md = "\n### Citations Not Found\n"
        result_as_stdout = "No citations found in the notebook."
    return result_as_md, result_as_stdout
