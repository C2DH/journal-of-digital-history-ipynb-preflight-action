import nbformat
import json
import re

def checktags(contents):
    tags_info = []
    result_as_md = "\n### Check Tags\n"
    result_as_stdout = ""

    # Convert JSON to notebook object
    json_str = json.dumps(contents)
    notebook = nbformat.reads(json_str, as_version=4)

    mandatory_tags = ['title', 'cover', 'contributor', 'copyright', 'keywords', 'abstract']
    optional_tags = ['hermeneutics', 'narrative', 'disclaimer','hidden']

    allowed_tag_pattern = r'(table|figure)-(\d+|[\w]+-\*)'

    for i, cell in enumerate(notebook.cells):
        if 'tags' in cell.metadata and cell.metadata['tags']:
            tags = cell.metadata['tags']
            tags_info.append((i + 1, tags))
            result_as_md += f"- Cell {i + 1}: Tags: {tags}\n"

            for tag in tags:
                if tag not in mandatory_tags and tag not in optional_tags and not re.match(allowed_tag_pattern, tag):
                    result_as_md += f"  - Invalid tag: {tag}\n"

    missing_tags = set(mandatory_tags) - set(tag for _, tags in tags_info for tag in tags)
    invalid_tags = [tag for _, tags in tags_info for tag in tags if tag not in mandatory_tags and tag not in optional_tags and not re.match(allowed_tag_pattern, tag)]

    if missing_tags or invalid_tags:
        result_as_md += "\n**WARNING: The following tags are missing or invalid:**\n"
        if missing_tags:
            result_as_md += "**Missing Tags:**\n"
            for tag in missing_tags:
                result_as_md += f"- {tag}\n"
        if invalid_tags:
            result_as_md += "**Invalid Tags:**\n"
            for tag in invalid_tags:
                result_as_md += f"- {tag}\n"
        result_as_stdout = "WARNING: The following tags are missing or invalid."
    else:
        result_as_md += "\nAll mandatory tags are present in the cells.\n"
        result_as_stdout = "All mandatory tags are present in the cells."

    return result_as_md, result_as_stdout
