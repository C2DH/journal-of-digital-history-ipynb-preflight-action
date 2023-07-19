def format_output(warnings, cell_numbers):
    result_as_md = "\n### Check JavaScript\n"
    result_as_stdout = ""

    if warnings:
        result_as_md += f"**WARNING: {len(warnings)} output cells contain JavaScript code.**\n\n"
        for cell_number in cell_numbers:
            result_as_md += f"- Cell {cell_number}\n"
        result_as_stdout = f"WARNING: {len(warnings)} output cells contain JavaScript code in cells: {cell_numbers}."
    else:
        result_as_md += "No JavaScript code found in output cells.\n"
        result_as_stdout = "No JavaScript code found in output cells."

    return result_as_md, result_as_stdout


def checkjavascript(contents):
    print("::debug::checkjavascript")
    cells = contents.get("cells", [])
    size = len(cells)
    output_cells = [cell for cell in cells if cell.get("cell_type") == "code" and cell.get("outputs")]
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
                    if "application/javascript" in html_content or "text/javascript" in html_content:
                        warnings.append(cell)
                        cell_numbers.append(cells.index(cell) + 1)
                        break

    result_as_md, result_as_stdout = format_output(warnings, cell_numbers)

    return result_as_md, result_as_stdout
