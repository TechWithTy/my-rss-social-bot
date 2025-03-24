#!/bin/bash

# Activate pipenv environment
pipenv shell

# Run tests with pytest
echo "Running tests..."
pipenv run pytest --maxfail=1 --disable-warnings -q

# Check if tests passed (exit code 0)
if [ $? -eq 0 ]; then
  echo "All tests passed!"

  # Prompt user for commit message
  read -p "Enter commit message: " COMMIT_MSG

  # Add changes to git
  git add .

  # Commit changes with the provided message
  git commit -m "$COMMIT_MSG"

  # Push changes to GitHub
  git push origin main

  echo "Changes have been pushed to GitHub."
else
  echo "Tests failed. No changes were committed or pushed."
fi
