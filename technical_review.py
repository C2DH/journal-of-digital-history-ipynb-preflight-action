# parse the cells tag and add "-*" at the end of a tag beginning with "figure"
import os
import re
import sys
import nbformat
from os.path import basename, splitext
from datetime import datetime
import requests
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

#call a .sh script
def call_script(script_name):
    os.system("sh {}".format(script_name))


def extract_html(text):
    pattern = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    urls = pattern.findall(text)
    return urls


def extract_url_md_html(text):
    pattern = re.compile(r'(?P<url>https?://[^\s]+)|\[(?P<label>[^\]]+)\]\((?P<url2>https?://[^\s]+)\)')
    urls = []
    for match in pattern.finditer(text):
        if match.group('url2'):
            urls.append(match.group('url2'))
        elif match.group('url2'):
            urls.append(match.group('url2'))
    return urls



def is_valid_url(url):
    """
    Checks if a URL is valid by sending a HEAD request to the URL and checking the response status code.

    Args:
        url (str): The URL to check.

    Returns:
        True if the URL is valid (i.e. returns a 2xx or 3xx status code), False otherwise.
    """
    try:
        response = requests.head(url)
        return response.status_code in range(200, 400)
    except requests.exceptions.RequestException:
        return False



def check_urls(notebook):
    for cell in notebook.cells:
        urls = extract_url_md_html(cell.source)
        if urls:
            for url in urls:
                # Remove a closing parentheses or square bracket from the end of the URL, if present
                if url[-1] == ')' or url[-1] == ']':
                    url = url[:-1]
                valid = is_valid_url(url)
                print("URL: {} is valid: {}".format(url, valid))



def check_ressource_in_dir_exclude(notebook, dir_path):
    """
    Recursively gets all files in a directory tree, excluding files in the `.git` and `.ipynb_checkpoints` directories.
    Look for if it's mentionned in the notebook
    Args:
        dir_path (str): Path to the directory to search.
    """

    for root, subdirs, filenames in os.walk(dir_path):
        # Exclude files in the `.git` directory
        if '.git' in root.split(os.sep):
            continue
        # Exclude files in the `.ipynb_checkpoints` directory
        if '.ipynb_checkpoints' in root.split(os.sep):
            continue
        for filename in filenames:
            file_path = os.path.join(root, filename)
            nbfind = 0
            for cell in notebook.cells:
                # if not in the cell.source, print the file name
                if file_path  in cell.source:
                    nbfind += 1
            if  nbfind==0:
                    # write in the log file
                    print(" file {} is not called".format(file_path))



def check_notebook_executed(nb):
    # Create an ExecutePreprocessor to execute the notebook cells
    ep = ExecutePreprocessor(timeout=None)

    # Iterate over the cells in the notebook
    for cell in nb.cells:
        # Only check code cells
        if cell.cell_type == 'code':
            # Execute the cell using the ExecutePreprocessor
            try:
                ep.preprocess_cell(cell, {'metadata': {'path': '.'}})
            except Exception as e:
                print(f"Error executing cell {cell.execution_count}: {e}")
                return False

            # Check if the cell has output
            if len(cell.outputs) == 0:
                print(f"Cell {cell.execution_count} has no output")
                return False

    # If all cells were executed and had output, return True
    return True

def extract_html(text):
    html_pattern = r'<(?!\/?(cite|\/cite|cite\s)).*?>'
    matches = re.findall(html_pattern, text)
    if len(matches) > 0:
        print("found in the cell: {}".format(text))
        #for i, match in enumerate(matches):
        #    print(f'Match {i+1}:\n{match}')



def check_html(notebook):
    for cell in notebook.cells:
        urls = extract_html(cell.source)
        if urls:
            for url in urls:
                # Remove a closing parentheses or square bracket from the end of the URL, if present
                if url[-1] == ')' or url[-1] == ']':
                    url = url[:-1]
                valid = is_valid_url(url)
                print("URL: {} is valid: {}".format(url, valid))

def add_figure_tag(notebook):
    for cell in notebook.cells:
        tags = cell.get("metadata", {}).get("tags", [])
        if tags:
            for tag in tags:
                if tag.startswith("figure"):
                    print("add -* to the tag: {}".format(tag))
                    tags.append(tag + "-*")
                    tags.remove(tag)
                    break
    return notebook



# main function
def main():
    call_script("generate_requirements.sh")
    # take the first argument passed to the script
    notebook_path = sys.argv[1]
    # logFile based output_timestamp.txt
    logFile = "output_{}.txt".format(str(datetime.now()))
    # create a log file
    sys.stdout = open(logFile, "w")
    #write in the log file
    sys.stdout.write("notebook_path: {}\n".format(notebook_path))
    # open the notebook
    notebook = nbformat.read(notebook_path, as_version=4)
    #get the list of the folder of the repository
    folder_list = os.listdir()
    #for each folder in the list
    sys.stdout.write("CHECK RESSOURCES\n")
    for folder in folder_list:
            #call the check_ressources method
            check_ressource_in_dir_exclude(notebook,folder)
    sys.stdout.write("CHECK URL\n")
    check_urls(notebook)
    sys.stdout.write("CHECK HTML\n")
    check_html(notebook)


    #sys.stdout.write("CHECK EXECUTED CELL\n")
    #check_notebook_executed(notebook)
    #close the log file
    sys.stdout.close()


#call the main function
if __name__ == '__main__':
    main()

#call the script from the terminal
#!python technical_review.py paper.ipynb

#call the script from the notebook
#%run technical_review.py paper.ipynb