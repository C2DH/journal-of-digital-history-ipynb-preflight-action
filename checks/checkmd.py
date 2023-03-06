import re
import sys

rx_h1 = re.compile(r"^# ", re.MULTILINE)
rx_h2 = re.compile(r"^## ", re.MULTILINE)
rx_h3 = re.compile(r"^### ", re.MULTILINE)


def checkmd(contents):
    print('::debug::checkmd')
    cells = contents.get("cells", [])
    size = len(cells)
    # get only cells containing markdown
    markdown_cells = [cell for cell in cells if cell.get("cell_type") == "markdown"]
    print(f"::debug::found {len(markdown_cells)} markdown cells out of {size} cells")
    # it should contain only one makrdown cell starting with a level 1 header
    # all other should be level 2
    headers = []
    errors = []
    for i in range(size):
        cell = cells[i]
        source = cell.get("source", [])
        source_md = '\n'.join(source)
        for ln, line in enumerate(source):
            if ln == 0:
                continue
            if line.startswith('#'):
                errors.append({ 'message': f'Markdown heading found in the middle of cell {i} at line {ln + 1}', "idx": i, "source": source })

        # use regular expression to match level 1 header
        if rx_h1.match(source_md):
            headers.append({"level": 1, "idx": i, "source": source})
        elif rx_h2.match(source_md):
            headers.append({"level": 2, "idx": i, "source": source})
        elif rx_h3.match(source_md):
            headers.append({"level": 3, "idx": i, "source": source})

    # print out all headers 
    for h in headers:
        print(f"::debug::header {h.get('level')} at cell {h.get('idx')} - {h.get('source', '')}")

    if len(headers) == 0:
        errors.append({ 'message': 'There should be at least one header' })
    else:
        h1_headers = [h for h in headers if h.get("level") == 1]
        if len(h1_headers) != 1:
            errors.append({ 'message': 'There should be only one level 1 header' })
    if len(errors) > 0:
        print(f"::error::Found {len(errors)} errors")
        for error in errors:
            print(f"::error:: {error.get('message')} at cell {error.get('idx')} - {error.get('source', '')}")
        sys.exit(1)
    else:
        print(f"::debug::Found {len(headers)} headers")
        print(f"::debug::Found {len(errors)} errors")


        