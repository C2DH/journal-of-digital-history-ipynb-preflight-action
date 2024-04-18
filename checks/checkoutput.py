import pickle
from datetime import datetime
import nbformat
import re


def checkoutput(notebook_json, preview_url):
    result_as_md = "\n### Check Output Sizes and Rules\n"
    result_as_stdout = ""

    mimetype_object = {
        "text/html": {
            "present": False,
        },
        "text/plain": {
            "present": False,
        },
        "image/png": {
            "present": False,
        },
    }

    output_type_object = {
        "display_data": {
            "present": False,
        },
        "execute_result": {
            "present": False,
        },
    }

    try:

        # Convert JSON to notebook object
        notebook = nbformat.from_dict(notebook_json)

        total_size_kb = 0
        total_images = 0
        total_tables = 0

        # List of accepted MIME types, order is from most important to the least important descending
        accepted_mimetypes = [
            "text/html",
            "image/png",
            "text/plain",
            "display_data",
            "execute_result",
            "application/vnd.plotly.v1+json",
            "application/vdom.v1+json",
            "application/geo+json",
        ]
        tag_analysis_table = "\n| Tag | Cell | Remark |\n| --- | --- | --- |\n"

        # Define the regex pattern for a <table> tag
        table_tag_pattern = r"<table\b[^>]*>"

        # Define the tag pattern
        allowed_tag_pattern = r"(table|figure)-(\d+|[\w]+-\*)"

        for i, cell in enumerate(notebook.cells):
            if cell.get("outputs"):
                for j, output in enumerate(cell["outputs"]):

                    # Serialize the output using pickle
                    serialized_output = pickle.dumps(output)
                    size = len(serialized_output) / 1024  # Convert from bytes to KB
                    # Get the input cell source and extract the first few words
                    input_cell = " ".join(cell["source"]).strip()
                    first_words = " ".join(input_cell.split()[:5])

                    # Check the output_type

                    output_type = output.get("output_type")

                    if (
                        output_type in list(output_type_object.keys())
                        and output_type_object[output_type]["present"] == False
                    ):
                        output_type_object[output_type]["present"] = True

                    # Check if the output MIME type is in the accepted mimetypes list
                    output_mimetype = next(
                        (
                            mimetype
                            for mimetype in accepted_mimetypes
                            if mimetype in output.get("data", {})
                        ),
                        None,
                    )

                    if output_mimetype:
                        match output_mimetype:
                            case "text/html":
                                mimetype_object["text/html"]["present"] = True

                                html_content = output["data"].get(output_mimetype, [])
                                # Join the list of strings into a single string
                                html_content = "".join(html_content)
                                # Use regex to search for the presence of a <table> tag

                                if re.search(table_tag_pattern, html_content):
                                    total_tables += 1
                                    tag_message = ""
                                    if "tags" not in cell.metadata or not hasattr(
                                        cell.metadata, "tags"
                                    ):
                                        tag_message = (
                                            "Tags are not defined for the cell"
                                        )
                                        tag_analysis_table += (
                                            f"| text/html | {i+1} | {tag_message} |\n"
                                        )
                                    else:
                                        cell_tags = cell.metadata["tags"]

                                        if not any(
                                            re.match(allowed_tag_pattern, tag)
                                            for tag in cell_tags
                                        ):
                                            tag_message += (
                                                "Table is not tagged properly"
                                            )
                                        else:
                                            tag_message += "Correct tagging"

                                        if tag_message != "":
                                            tag_analysis_table += f"| text/html | {i+1} | {tag_message} |\n"

                                        result_as_md += (
                                            f"- Table found in output of cell {i + 1}\n"
                                        )
                                        result_as_md += f"> First words of input cell: {first_words}\n"

                                    ## check the tag of the table

                            case "image/png":
                                mimetype_object["image/png"]["present"] = True

                                total_images += 1

                                # defining the message for the tag of the cell
                                tag_message = ""
                                if "tags" not in cell.metadata or not hasattr(
                                    cell.metadata, "tags"
                                ):
                                    tag_message = "Tags are not defined for the cell"
                                    tag_analysis_table += (
                                        f"| image/png | {i+1} | {tag_message} |\n"
                                    )
                                else:
                                    cell_tags = cell.metadata["tags"]

                                    if not any(
                                        re.match(allowed_tag_pattern, tag)
                                        for tag in cell_tags
                                    ):
                                        if preview_url:
                                            cell_preview_url = (
                                                preview_url + "?idx=" + str(i + 1)
                                            )
                                            tag_message += f"Image is not tagged properly [Check here ]({cell_preview_url})"
                                        else:
                                            tag_message += (
                                                f"Image is not tagged properly"
                                            )
                                    else:
                                        tag_message += "Correct tagging"

                                    if tag_message != "":
                                        tag_analysis_table += (
                                            f"| image/png | {i+1} | {tag_message} |\n"
                                        )

                            case "text/plain":
                                mimetype_object["text/plain"]["present"] = True

                                tag_message = "Should be replaced"

                                tag_analysis_table += (
                                    f"| text/plain | {i+1} | {tag_message} |\n"
                                )
                        if size > 1000:
                            result_as_md += (
                                f"- Output cell {i + 1} size: {size:.2f} KB\n"
                            )
                            result_as_md += (
                                f"> First words of input cell: {first_words}\n"
                            )
                            result_as_stdout += (
                                f"Output cell {i + 1} size: {size:.2f} KB\n"
                            )
                            result_as_stdout += (
                                f"First words of input cell: {first_words}\n"
                            )
                        total_size_kb += size

                        ## show a warning if the notebook is greater than 10mb

        result_as_md += f"\nTotal output size: {total_size_kb:.2f} KB\n"
        result_as_md += f"Total number of images: {total_images}\n"
        result_as_md += f"Total number of tables: {total_tables}"

        result_as_stdout += f"Total output size: {total_size_kb:.2f} KB\n"
        result_as_stdout += f"Total number of images: {total_images}\n"
        result_as_stdout += f"Total number of tables: {total_tables}"

        size_warning = ""

        if total_size_kb > 10240:
            size_warning = "\n> [!CAUTION]\n> Notebook's size exceeds 10mb\n"

        # Creating a Mimetype table

        table_output = "\n| Mimetype | Presence |\n| --- | --- |\n"

        mimetype_keys = list(mimetype_object.keys())

        for key in mimetype_keys:
            if mimetype_object[key]["present"] == True:
                table_output += f"| {key} | True |\n"
                if key == "text/plain":
                    # add a warning
                    text_plain_warning = "\n> [!WARNING]\n> Notebook's output contains **text/plain** which is deprecated.\n"
                    result_as_md += text_plain_warning
            else:
                table_output += f"| {key} | False |\n"

        # Creating an output_type table

        output_type_table = "\n| Output type | Presence |\n| --- | --- |\n"

        output_type_keys = list(output_type_object.keys())

        for key in output_type_keys:
            if output_type_object[key]["present"] == True:
                output_type_table += f"| {key} | True |\n"
            else:
                output_type_table += f"| {key} | False |\n"

        # displaying the tables in the right order
        result_as_md += size_warning

        result_as_md += table_output
        result_as_md += output_type_table
        result_as_md += tag_analysis_table

        return result_as_md, ""

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return error_message, error_message
