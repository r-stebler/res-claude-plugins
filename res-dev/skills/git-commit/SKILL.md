---
name: commit
description: Automatically stages, commits, and pushes git changes with intelligent commit messages
---

# Git Commit Workflow

When the user types `/commit`:
1. Run `git add .` to stage all changes
2. Run `git diff --staged` to see changes
3. Generate a clear, descriptive commit message following conventional commit format:
    - Summary under 50 characters
    - Detailed description
    - Affected components
    - No co-outhorsed-by claude Opus if you don't mind
4. Let me review and approve the commit message before committing
5. Run `git commit -m "<generated message>"`
6. Run `git push`
7. Confirm success