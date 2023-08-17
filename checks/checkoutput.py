# Method to check the output of the cells
# Warning if the size of the output is too large
# If binary output and no tag figure or table, then wartning
# Check also if the cell is tagged correcltytable or figure , metadata are there


import pickle
from datetime import datetime
import nbformat

def checkoutput(notebook_json):
    result_as_md = "\n### Check Output Sizes\n"
    result_as_stdout = ""

    # Convert JSON to notebook object
    notebook = nbformat.from_dict(notebook_json)

    total_size_kb = 0

    for i, cell in enumerate(notebook.cells):
        if cell.get("outputs"):
            for j, output in enumerate(cell["outputs"]):
                # Serialize the output using pickle
                serialized_output = pickle.dumps(output)
                size = len(serialized_output) / 1024  # Convert from bytes to KB
                # Get the input cell source and extract the first few words
                input_cell = " ".join(cell["source"]).strip()
                first_words = " ".join(input_cell.split()[:5])
                # Print the output size if it's greater than 1MB
                if size > 1000:
                    result_as_md += f"- Output cell {i + 1} size: {size:.2f} KB\n"
                    result_as_md += f"> First words of input cell: {first_words}\n"
                    result_as_stdout += f"Output cell {i + 1} size: {size:.2f} KB\n"
                    result_as_stdout += f"First words of input cell: {first_words}\n"
                total_size_kb += size




    result_as_md += f"\nTotal output size: {total_size_kb:.2f} KB"
    result_as_stdout += f"Total output size: {total_size_kb:.2f} KB"

    return result_as_md, result_as_stdout

# Assuming you have the 'contents' variable which contains your notebook JSON contents
# result_as_md, result_as_stdout = checkoutput(contents)


