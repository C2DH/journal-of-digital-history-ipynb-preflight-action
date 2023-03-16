import sys
import os
import fire
import json
import importlib.util


def get_notebook_json(notebook_filepath):
    with open(notebook_filepath) as f:
        return json.load(f)


def set_action_outputs(output_pairs):
    """
    Sets the GitHub Action outputs, with backwards compatibility for
    self-hosted runners without a GITHUB_OUTPUT environment file.

    Keyword arguments:
    output_pairs - Dictionary of outputs with values
    """
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            for key, value in output_pairs.items():
                print("{0}={1}".format(key, value), file=f)
    else:
        for key, value in output_pairs.items():
            print("::set-output name={0}::{1}".format(key, value))


def generate_report(output, notebook, workspace="", action_outputs={}, contents={}):
    """
    Generate a report for the notebook

    Keyword arguments:
    output -- the output file name
    notebook -- the notebook file name
    workspace -- the workspace directory
    action_outputs -- the action outputs
    contents -- the notebook contents

    """
    print(f"::debug::generatereport output:{output} notebook:{notebook}")
    output_filepath = os.path.join(workspace, output)
    count = len(contents["cells"])
    # Open the file for writing and handle any errors
    try:
        with open(output_filepath, "w", encoding="utf-8") as output_file:
            output_file.write(
                f"# Report for {notebook} \u2764 \n\n"
            )  # Write "#Hello" with a heart utf8 character
            # count cells of each type. check for empty cells
            cell_types = {"code_empty": 0}
            for cell in contents["cells"]:
                cell_type = cell["cell_type"]
                if cell_type not in cell_types:
                    cell_types[cell_type] = 0
                cell_types[cell_type] += 1
                if cell_type == "code":
                    if len(cell["source"]) == 0:
                        cell_types["code_empty"] += 1
            # write cell counts
            output_file.write("## Cell Counts   \n")
            output_file.write(f"all cells: {count}   \n")
            for cell_type, count in cell_types.items():
                output_file.write(f"{cell_type}: {count}   \n")
            # write every action_output
            output_file.write("\n## Action Outputs\n\n")
            for key, value in action_outputs.items():
                output_file.write(f"{value}\n")
    except IOError:
        # bad
        print(f"::error::Bad things happened when open or write to {output}!")
        sys.exit(1)


def main(notebook="notebook.ipynb", functions="checkmd,checkurls", output_md=None):
    workspace = os.getenv("GITHUB_WORKSPACE", "")
    notebook_filepath = os.path.join(workspace, notebook)
    if not os.path.exists(notebook_filepath):
        print(f"::error::Path {notebook_filepath} does not exist")
        sys.exit(1)
    notebook_json_contents = get_notebook_json(notebook_filepath)
    # Split the functions argument into a list of function names
    # check if function is tuple
    function_names = (
        [a for a in functions] if isinstance(functions, tuple) else functions.split(",")
    )
    size = len(notebook_json_contents["cells"])
    actions_outputs = (
        {"size": f"\n### Size\n**total cells: {size}**"}
        if output_md
        else {"size": size}
    )
    # Import the specified functions from external modules
    for func in function_names:
        module_name = f"checks.{func}"
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            print(f"Error: Cannot find module {module_name}")
            sys.exit(1)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        actions_outputs[func] = getattr(module, func)(notebook_json_contents, output_md)
    # Set the GitHub Action outputs
    set_action_outputs(actions_outputs)
    # if output is provided, check output file then generate report
    if output_md is not None:
        generate_report(
            output_md,
            notebook,
            workspace=workspace,
            action_outputs=actions_outputs,
            contents=notebook_json_contents,
        )


if __name__ == "__main__":
    fire.Fire(main)
