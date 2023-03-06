# Journal of Digital History Preflight action

This GitHub action performs comprehensive checks on your `.ipynb` notebook to ensure that it meets the standards required for publication on the [Journal of Digital History](https://journalofdigitalhistory.org). With systematic checks and validation, you can be confident that your notebook is publication-ready and meets the necessary requirements.

We provide a set of tools to facilitate the life of authors (and reviewers) in pull request reviews. The action contains several Python scripts that can be easily integrated into any workflow to automate repetitive tasks and improve the code review process.

## Features


## Usage

To use this action, simply include it in your GitHub Actions workflow file and configure it to run on pull request events. You can then use the outputs of the action to automate certain tasks or to provide additional context to reviewers.

```yaml
on: [pull_request, worflow_dispatch]

jobs:
  preflight:
    runs-on: ubuntu-latest
    name: Run preflight checks
    steps:
      - name: checkout repo
        uses: actions/checkout@v3
      - name: Run preflight checks
        id: preflight
        uses: c2dh/journal-of-digital-history-ipynb-preflight-action@master
        with:
          notebook: 'example/display-image.ipynb'
          functions: 'checkmd,checkurls'
      - name: Use the output, if needed
        run: echo "number of cells ${{ steps.preflight.outputs.size }}"
```
## Contributing

Contributions are welcome! If you find a bug or would like to suggest a new feature, please open an issue or submit a pull request.
To execute a new command:
- add a new file in the `checks` folder, e.g. `checkthis` only a-z characters in the name :)
- Inside the file, add a function with the same name as the file, e.g. `def checkthis(contents)`
- The function takes the JSON dict of the notebook as input and returns a simple text string if everything is ok, or it raises an exception if something is wrong.
- Handle the errors conveniently in your script.
- Add its name to the `checks` input of the action. The script will be executed in the order specified in the input.

## License

