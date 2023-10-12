import pickle
from datetime import datetime
import nbformat
import re

def checkoutput(notebook_json,preview_url):
    result_as_md = "\n### Check Output Sizes and Rules\n"
    result_as_stdout = ""

    try:

        # Convert JSON to notebook object
        notebook = nbformat.from_dict(notebook_json)

        total_size_kb = 0
        total_images = 0
        total_tables = 0

        # List of desired MIME types
        desired_mimetypes = ['text/html', 'image/png', 'application/vnd.plotly.v1+json', 'application/vdom.v1+json', 'application/geo+json']

        # Define the regex pattern for a <table> tag
        table_tag_pattern = r'<table\b[^>]*>'

        # Define the tag pattern
        allowed_tag_pattern = r'(table|figure)-(\d+|[\w]+-\*)'

        for i, cell in enumerate(notebook.cells):
            if cell.get("outputs"):
                for j, output in enumerate(cell["outputs"]):
                    # Serialize the output using pickle
                    serialized_output = pickle.dumps(output)
                    size = len(serialized_output) / 1024  # Convert from bytes to KB
                    # Get the input cell source and extract the first few words
                    input_cell = " ".join(cell["source"]).strip()
                    first_words = " ".join(input_cell.split()[:5])
                    # Check if the output MIME type is in the desired list
                    output_mimetype = next((mimetype for mimetype in desired_mimetypes if mimetype in output.get("data", {})), None)

                    if output_mimetype:
                        if output_mimetype == 'text/html':
                            html_content = output["data"].get(output_mimetype, [])
                            # Join the list of strings into a single string
                            html_content = "".join(html_content)
                            # Use regex to search for the presence of a <table> tag
                            if re.search(table_tag_pattern, html_content):
                                total_tables += 1
                                result_as_md += f"- Table found in output of cell {i + 1}\n"
                                result_as_md += f"> First words of input cell: {first_words}\n"
                        elif output_mimetype == 'image/png':
                            total_images += 1
                            if 'tags' in cell.metadata and cell.metadata['tags']:
                                cell_tags = cell.metadata['tags']
                                for tag in cell_tags:
                                    if re.match(allowed_tag_pattern, tag):
                                        result_as_md += f"  - Valid tag: {tag} for image output in cell {i + 1}\n"
                                if not any(re.match(allowed_tag_pattern, tag) for tag in cell_tags):
                                    if preview_url:
                                        cell_preview_url=preview_url + "?idx=" + str(i + 1)
                                        result_as_md += f"  - No valid tags found for image output  [Check here ]({cell_preview_url})"
                                    else:
                                        result_as_md += f"  - No valid tags found for image output in cell {i + 1}\n"
                            else:
                                result_as_md += f"  - No tags found for image output in cell {i + 1}\n"

                        # Print the output size if it's greater than 1MB
                        if size > 1000:
                            result_as_md += f"- Output cell {i + 1} size: {size:.2f} KB\n"
                            result_as_md += f"> First words of input cell: {first_words}\n"
                            result_as_stdout += f"Output cell {i + 1} size: {size:.2f} KB\n"
                            result_as_stdout += f"First words of input cell: {first_words}\n"
                        total_size_kb += size

        result_as_md += f"\nTotal output size: {total_size_kb:.2f} KB\n"
        result_as_md += f"Total number of images: {total_images}\n"
        result_as_md += f"Total number of tables: {total_tables}"

        result_as_stdout += f"Total output size: {total_size_kb:.2f} KB\n"
        result_as_stdout += f"Total number of images: {total_images}\n"
        result_as_stdout += f"Total number of tables: {total_tables}"

        return result_as_md, ""

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return error_message, error_message
