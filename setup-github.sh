#!/bin/bash

# Initialize Git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit"

# Add GitHub remote (replace with your GitHub repository URL)
echo "Enter your GitHub repository URL (e.g., https://github.com/username/jira-voice-assistant.git):"
read github_url

git remote add origin $github_url

# Push to GitHub
git push -u origin main

echo "Repository has been pushed to GitHub!"
echo "Next steps:"
echo "1. Go to https://vercel.com"
echo "2. Import your GitHub repository"
echo "3. Configure environment variables"
echo "4. Deploy!" 