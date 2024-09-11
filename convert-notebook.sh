# to use it: ./convert-notebook.sh <pid_of_the_article>
#!/bin/bash

# Check if a parameter is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <pid_of_the_article>"
  exit 1
fi

# Assign the parameter to a variable
PID=$1

# FIRST STEP: Get the ipynb from the server
echo "Fetching notebook from server..."
scp c2dhadmin@10.240.4.179:/opt/journal-digital-history-docker-stack/data/outputs/${PID}.ipynb .

# Check if the scp command was successful
if [ $? -ne 0 ]; then
  echo "Failed to fetch notebook from server."
  exit 1
fi

# SECOND STEP: Transform in latex
echo "Converting notebook to LaTeX..."
jupyter nbconvert --to latex ${PID}.ipynb

# Check if the nbconvert command was successful
if [ $? -ne 0 ]; then
  echo "Failed to convert notebook to LaTeX."
  exit 1
fi

# THIRD STEP: include images in the latex file
echo "Adjusting image inclusion in LaTeX file..."
sed -i '' 's/\\adjustimage{max size={0.9\\linewidth}{0.9\\paperheight}}{\([^}]*\)}/\\includegraphics[width=0.9\\linewidth, height=0.9\\paperheight, keepaspectratio]{\1}/g' ${PID}.tex

# Check if the sed command was successful
if [ $? -ne 0 ]; then
  echo "Failed to adjust image inclusion in LaTeX file."
  exit 1
fi

# FOR STEP: Transform in docx
echo "Converting LaTeX to DOCX..."
pandoc ${PID}.tex -s -o ${PID}.docx --resource-path=.

# Check if the pandoc command was successful
if [ $? -ne 0 ]; then
  echo "Failed to convert LaTeX to DOCX."
  exit 1
fi

echo "Conversion completed successfully."