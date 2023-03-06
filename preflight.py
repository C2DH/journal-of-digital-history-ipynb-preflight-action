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


def main(notebook='notebook.ipynb', functions='checkmd,checkurls'):
    workspace = os.getenv("GITHUB_WORKSPACE", "")
    notebook_filepath = os.path.join(workspace, notebook)
    if not os.path.exists(notebook_filepath):
        print(f"::error::Path {notebook_filepath} does not exist")
        sys.exit(1)
    notebook_json_contents = get_notebook_json(notebook_filepath)
    # Split the functions argument into a list of function names
    function_names = functions.split(',')
    actions_outputs = {
      'size': len(notebook_json_contents['cells'])
    }
    # Import the specified functions from external modules
    for func in function_names:
        module_name = f'checks.{func}'
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            print(f'Error: Cannot find module {module_name}')
            sys.exit(1)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        actions_outputs[func] = getattr(module, func)(notebook_json_contents)
    # Set the GitHub Action outputs
    set_action_outputs(actions_outputs)

if __name__ == '__main__':
    fire.Fire(main)
