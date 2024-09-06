import sys
import os
import fire
import json
import importlib.util
import re
import base64
from urllib.parse import quote

BASE_URL = "https://journalofdigitalhistory.org/en/notebook-viewer/"

f = open("article-check-script/config.json")

config_file = json.load(f)

f.close()

FIRST_PARAGRAPH = config_file["first_paragraph"]


def encode_notebook_url(url):
    # URL-encode the string
    url_encoded = quote(url, safe="")
    # Base64 encode the URL-encoded string
    base64_encoded = base64.b64encode(url_encoded.encode("utf-8")).decode("utf-8")
    # Replace '+' with '/' to match the desired result
    result = base64_encoded.replace("+", "/")
    return result


def process_github_url(value):
    github_regex = r"https?://(github\.com|raw\.githubusercontent\.com)/([A-Za-z0-9-_.]+)/([A-Za-z0-9-_.]+)/(blob/)?(.*)"
    match = re.match(github_regex, value)

    if match:
        domain, username, repo, _, filepath = match.groups()
        proxy_value = f"/proxy-githubusercontent/{username}/{repo}/{filepath}"
        result = {
            "value": value,
            "domain": domain,
            "proxyValue": proxy_value,
            "origin": "github",
        }
    else:
        result = {"value": value, "origin": "unknown"}
    return result


def get_github_url(notebook_filepath):
    github_url = ""
    branch = os.getenv("GITHUB_REF_NAME", "")
    repo = os.getenv("GITHUB_REPOSITORY", "")
    if branch and repo:
        github_url = f"https://github.com/{repo}/blob/{branch}/{notebook_filepath}"
    return github_url


def get_preview_url(notebook_filepath):
    preview_url = ""
    github_url = get_github_url(notebook_filepath)
    if github_url:
        result = process_github_url(github_url)
        encode = encode_notebook_url(result["proxyValue"])
        preview_url = f"{BASE_URL}{encode}"
    return preview_url


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

    def write_result(count):
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
                output_file.write(FIRST_PARAGRAPH + "\n\n")
                output_file.write("## Cell Counts   \n")
                output_file.write(f"**all cells: {count}**  \n")
                for cell_type, count in cell_types.items():
                    output_file.write(f"{cell_type}: {count}   \n")
                # write every action_output
                output_file.write("\n## Action Outputs\n")
                for key, value in action_outputs.items():
                    output_file.write(f"{value}\n")
            output_file.close()
        except IOError:
            # bad
            write_result(count)

    write_result(count)


def main(
    notebook="notebook.ipynb",
    functions="checkmd,checkurls",
    output_md="preflight_report.md",
):
    workspace = os.getenv("GITHUB_WORKSPACE", "")
    preview_url = get_preview_url(notebook)
    print(f"::debug::workspace:{workspace}")
    notebook_filepath = os.path.join(workspace, notebook)
    print(f"::debug::notebook_filepath:{notebook_filepath}")
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
    actions_outputs = {
        "notebook_path": notebook_filepath,
        "notebook": notebook,
        "workspace": workspace,
    }
    actions_md_outputs = {"size": f"\n### Size\n**total cells: {size}**"}
    # Import the specified functions from external modules
    for func in function_names:
        module_name = f"checks.{func}"
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            print(f"Error: Cannot find module {module_name}")
            sys.exit(1)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        func_as_md, func_as_output = getattr(module, func)(
            notebook_json_contents, preview_url
        )
        actions_outputs[func] = func_as_output
        actions_md_outputs[func] = func_as_md
    # Set the GitHub Action outputs
    set_action_outputs(actions_outputs)
    # if output is provided, check output file then generate report
    generate_report(
        output_md,
        notebook,
        workspace=workspace,
        action_outputs=actions_md_outputs,
        contents=notebook_json_contents,
    )


if __name__ == "__main__":
    fire.Fire(main)


# github_url
