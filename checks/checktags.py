import nbformat
import json
import re


def checktags(contents, preview_url):
    tags_info = []
    result_as_md = "\n### Check Tags\n"
    result_as_stdout = ""

    # Convert JSON to notebook object
    json_str = json.dumps(contents)
    notebook = nbformat.reads(json_str, as_version=4)

    mandatory_tags = [
        "title",
        "cover",
        "contributor",
        "copyright",
        "keywords",
        "abstract",
    ]
    optional_tags = ["hermeneutics", "narrative", "disclaimer", "hidden", "data-table"]

    allowed_tag_pattern = r"^(table|figure|video|sound|dialog)-(?:\d+|[\w]+)-\*$"

    for i, cell in enumerate(notebook.cells):
        if "tags" in cell.metadata and cell.metadata["tags"]:
            tags = cell.metadata["tags"]
            tags_info.append((i + 1, tags))
            result_as_md += f"- Cell {i + 1}: Tags: {tags}\n"

            for tag in tags:
                if (
                    tag not in mandatory_tags
                    and tag not in optional_tags
                    and not re.match(allowed_tag_pattern, tag)
                ):
                    result_as_md += f"  - Invalid tag: {tag}\n"

    missing_tags = set(mandatory_tags) - set(
        tag for _, tags in tags_info for tag in tags
    )
    invalid_tags = [
        tag
        for _, tags in tags_info
        for tag in tags
        if tag not in mandatory_tags
        and tag not in optional_tags
        and not re.match(allowed_tag_pattern, tag)
    ]

    if missing_tags or invalid_tags:
        result_as_md += "> [!WARNING]\n"
        result_as_md += "> The following tags are missing or invalid\n"
        if missing_tags:
            result_as_md += "\n#### Missing Tags:\n"
            for tag in missing_tags:
                result_as_md += f"- {tag}\n"
            
            if "copyright" in missing_tags:
                result_as_md +=f">[!CAUTION]\n> **copyright** tag is missing. Make sure to fill this template document [license_to_publish_JDH.dotx](https://github.com/C2DH/journal-of-digital-history-ipynb-preflight-action/blob/master/license_to_publish_JDH.dotx) and send it to jdh.admin@uni.lu\n"
                result_as_md+=f"\n\n**Add ONE of the following codeblocks depending on which licence you want to use and be sure the cell is tagged as copyright.**\n\n"
                result_as_md+="### CC-BY license:\n\n```\n[![cc-by](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)\n©<AUTHOR or ORGANIZATION / FUNDER>. Published by De Gruyter in cooperation with the University of Luxembourg Centre for Contemporary and Digital History. This is an Open Access article distributed under the terms of the [Creative Commons Attribution License CC-BY](https://creativecommons.org/licenses/by/4.0/)\n```\n\n"
                result_as_md+="### CC-BY-NC-ND license:\n\n```\n[![cc-by-nc-nd](https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png)](https://creativecommons.org/licenses/by-nc-nd/4.0/)\n©<AUTHOR or ORGANIZATION / FUNDER>. Published by De Gruyter in cooperation with the University of Luxembourg Centre for Contemporary and Digital History. This is an Open Access article distributed under the terms of the [Creative Commons Attribution License CC-BY-NC-ND](https://creativecommons.org/licenses/by-nc-nd/4.0/)\n```\n\n"
                
        if invalid_tags:
            result_as_md += "\n#### Invalid Tags:\n"
            for tag in invalid_tags:
                result_as_md += f"- {tag}\n"
        result_as_stdout = "WARNING: The following tags are missing or invalid."
    else:
        result_as_md += "\nAll mandatory tags are present in the cells.\n"
        result_as_stdout = "All mandatory tags are present in the cells."
    
    if "copyright" not in missing_tags:
        result_as_md+="> Make sure to fill this template document [license_to_publish_JDH.dotx](https://github.com/C2DH/journal-of-digital-history-ipynb-preflight-action/blob/master/license_to_publish_JDH.dotx) and send it to jdh.admin@uni.lu\n"

    return result_as_md, result_as_stdout
 
