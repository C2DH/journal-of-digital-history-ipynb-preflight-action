import json
import os


def format_output(warnings, preview_url, cell_numbers):
    result_as_md = "\n### Check JavaScript\n"
    result_as_stdout = ""

    if warnings:
        result_as_md += (
            f"**WARNING: {len(warnings)} output cells contain JavaScript code.**\n\n"
        )
        for cell_number in cell_numbers:
            if preview_url:
                cell_preview_url = preview_url + "?idx=" + str(cell_number)
                result_as_md += f"-  [Check here ]({cell_preview_url})\n"
            else:
                result_as_md += f"- Cell {cell_number}\n"
        result_as_stdout = f"WARNING: {len(warnings)} output cells contain JavaScript code in cells: {cell_numbers}."
    else:
        result_as_md += "No JavaScript code found in output cells.\n"
        result_as_stdout = "No JavaScript code found in output cells."

    return result_as_md, result_as_stdout


def checkplotlyconfig(outputs_value):
    plotly_code_mandatory = [
        'require.undef("plotly")',
        "* plotly.js",
    ]
    checks_results = [
        False,
        False,
    ]  # first for require.undef, second for plotly.version

    for j in range(0, len(outputs_value), 1):
        checks_limit = 10
        m = "text/html" in outputs_value[j]["data"]

        if m == False:
            continue

        if len(outputs_value[j]["data"]["text/html"]) < 10:
            checks_limit = len(outputs_value[j]["data"]["text/html"])

        for i in range(0, checks_limit, 1):
            current_line = str(outputs_value[j]["data"]["text/html"][i].strip())
            if plotly_code_mandatory[0] in current_line:
                checks_results[0] = True
            elif plotly_code_mandatory[1] in current_line:
                checks_results[1] = True

    return checks_results


def checkjavascript(contents, preview_url):
    print("::debug::checkjavascript")
    cells = contents.get("cells", [])
    size = len(cells)
    output_cells = [
        cell
        for cell in cells
        if cell.get("cell_type") == "code" and cell.get("outputs")
    ]
    print(f"::debug::found {len(output_cells)} output cells out of {size} cells")

    warnings = []
    cell_numbers = []
    for cell in output_cells:
        for output in cell.get("outputs", []):
            if output.get("output_type") == "display_data":
                data = output.get("data", {})
                if "text/html" in data:
                    html_content = data["text/html"]
                    if isinstance(html_content, list):
                        html_content = "\n".join(html_content)
                    if (
                        "application/javascript" in html_content
                        or "text/javascript" in html_content
                    ):
                        warnings.append(cell)
                        cell_numbers.append(cells.index(cell) + 1)
                        break

    result_as_md, result_as_stdout = format_output(warnings, preview_url, cell_numbers)

    # plotly check begins from here
    # check if language is R
    metadata = contents.get("metadata", [])
    kernel = metadata.get("language_info", [])
    # converting to JSON
    kernelJSON = json.loads(json.dumps(kernel))
    if kernelJSON["name"] == "R":
        result_as_md += "> [!NOTE] \n"
        result_as_md += f"> **plotly** is not being checked, as programming language used is **R ({kernelJSON['version']})**\n"
        return result_as_md, result_as_stdout
    result_as_md += "### Check JavaScript (plotly)\n"

    requirementsFileExists = os.path.isfile("./requirements.txt")

    if requirementsFileExists == False:

        result_as_md += f"> [!CAUTION]\n"
        result_as_md += f"> Error: **requirements.txt** is missing\n"
        return result_as_md, result_as_stdout

    requirements_txt = open("./requirements.txt", "r")

    # read the file
    read_content = requirements_txt.read()
    if "plotly" not in read_content:
        result_as_md += "**plotly** library is not present in **requirements.txt**\n"
        return result_as_md, result_as_stdout

    outputs = json.loads(json.dumps(contents))
    # text_html_outputs = outputs["cells"][0]["outputs"][0]["data"]["text/html"]
    text_html_outputs = outputs["cells"]
    code_cells_list = [
        element for element in text_html_outputs if element["cell_type"] == "code"
    ]

    checks_results = {
        "require.undef": {
            "found": False,
            "not_found_message": '**require.undef("plotly")** is missing\n',
            "found_message": '**require.undef("plotly")** is present\n',
        },
        "plotly.version": {
            "found": False,
            "not_found_message": "\n**\\* plotly.js** is missing\n",
            "found_message": "\n**\\* plotly.js** is present\n",
        },
    }

    for cell in code_cells_list:
        if len(cell["outputs"]) != 0:
            checks_output = checkplotlyconfig(cell["outputs"])
            if checks_output[0] == True:
                checks_results["require.undef"]["found"] = True
            if checks_output[1] == True:
                checks_results["plotly.version"]["found"] = True

    if checks_results["require.undef"]["found"] == False:
        result_as_md += checks_results["require.undef"]["not_found_message"]
    elif checks_results["require.undef"]["found"] == True:
        result_as_md += checks_results["require.undef"]["found_message"]

    if checks_results["plotly.version"]["found"] == False:
        result_as_md += checks_results["plotly.version"]["not_found_message"]
    elif checks_results["plotly.version"]["found"] == True:
        result_as_md += checks_results["plotly.version"]["found_message"]

    return result_as_md, result_as_stdout
