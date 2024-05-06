import os
import json


def checkkernel(contents, output=None):
    std_output = ""
    md_output = "## Kernel Checks: \n\n"

    print("::debug::checkkernel")

    ## check if language is R
    metadata = contents.get("metadata", [])
    kernel = metadata.get("language_info", [])
    # converting to JSON
    kernelJSON = json.loads(json.dumps(kernel))

    if kernelJSON["name"] == "R":
        md_output += f"Programming language is **R ({kernelJSON['version']})**\n"
        # std_output+="Language is R\n"

    ## if language is not R
    else:
        # std_output+="Language is NOT R"

        # check if runtime.txt exists
        runtimeFileExists = os.path.isfile("./runtime.txt")

        if runtimeFileExists == False:
            # std_output+="runtime.txt file is missing\n"
            md_output += f"> [!CAUTION]\n"
            md_output += f"> Error: **runtime.txt** is missing\n"
            return [md_output, std_output]

        # if runtime.txt exists, then check if the language from notebook matches the one in runtime.txt

        notebook_language = kernelJSON["name"] + "-" + kernelJSON["version"]

        runtime_txt = open("./runtime.txt", "r")

        # read the file
        read_content = runtime_txt.read()
        if read_content == notebook_language:

            # std_output+="Python versions match\n"
            md_output += f"Python versions match :white_check_mark:\n"
        else:
            # std_output+="Python versions dont match"
            md_output += f"> [!CAUTION]\n > Error: Python versions don't match. The notebook is using **{notebook_language}**, when **{read_content}** is required.\n\n"

            md_output += (
                "> [!TIP]\n > Try changing **runtime.txt** to resolve the error above."
            )

    # std_output+=f"end of kernel checks"
    return md_output, std_output
