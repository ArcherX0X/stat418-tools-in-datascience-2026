# GitHub Collaboration: Professional Workflows

This example demonstrates professional GitHub workflows for team collaboration, emphasizing the platform features that make modern data science development efficient.

## Setup

Open VSCode's integrated terminal and navigate to this directory:

```bash
cd week-3/examples/git-collaboration
```

## Overview

You'll learn:
- GitHub-specific collaboration features
- Pull requests and code review workflows
- GitHub Issues for project management
- GitHub Actions basics
- Forking and contributing to open source
- Building a data science portfolio on GitHub

## Template Repository

For a complete example of these concepts in action, see the **LA Crime Analysis** template:
- GitHub: https://github.com/[instructor-username]/la-crime-analysis
- Demonstrates: Pull requests, Issues, Actions, professional documentation
- Students: Fork this for your final projects

## Example 1: Feature Branch Workflow

### The Scenario

You're working on a team project. You need to add a new feature without disrupting the main codebase.

### Step-by-Step

**1. Start from a clean main branch:**
```bash
# Make sure you're on main
git checkout main

# Pull latest changes
git pull origin main

# Verify you're up to date
git status
```

**2. Create a feature branch:**
```bash
# Create and switch to new branch
git checkout -b feature/data-visualization

# Verify you're on the new branch
git branch
# * feature/data-visualization
#   main
```

**3. Make your changes:**
```bash
# Create a new file
cat > visualize.py << 'EOF'
import matplotlib.pyplot as plt
import pandas as pd

def create_scatter_plot(data, x_col, y_col):
    """Create a scatter plot from dataframe."""
    plt.figure(figsize=(10, 6))
    plt.scatter(data[x_col], data[y_col])
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title(f'{y_col} vs {x_col}')
    plt.savefig('scatter_plot.png')
    print("Plot saved to scatter_plot.png")

if __name__ == "__main__":
    # Example usage
    df = pd.DataFrame({
        'x': [1, 2, 3, 4, 5],
        'y': [2, 4, 5, 4, 6]
    })
    create_scatter_plot(df, 'x', 'y')
EOF

# Stage and commit
git add visualize.py
git commit -m "Add scatter plot visualization function"
```

**4. Push your branch to GitHub:**
```bash
# Push feature branch to remote
git push origin feature/data-visualization

# If this is the first push, Git will suggest:
git push --set-upstream origin feature/data-visualization
```

**5. Create a Pull Request on GitHub:**
- Go to your GitHub repository
- Click "Compare & pull request" button (appears after pushing)
- Fill in PR description using template:
  ```markdown
  ## What does this PR do?
  Adds scatter plot visualization function for data analysis
  
  ## Why is this change needed?
  Team needs to visualize relationships between variables
  
  ## How was it tested?
  - Unit tests added for edge cases
  - Manual testing with sample data
  - Verified plot output quality
  
  ## Screenshots
  [Attach example plot if applicable]
  ```
- Add labels (e.g., `enhancement`, `data-viz`)
- Link related Issues (e.g., "Closes #42")
- Request reviewers from your team
- Submit PR

**6. Address Review Feedback:**
```bash
# Make requested changes
nano visualize.py  # or use your editor

# Commit changes
git add visualize.py
git commit -m "Add error handling for missing columns"

# Push updates
git push origin feature/data-visualization
```

**7. After PR is Merged:**
```bash
# Switch back to main
git checkout main

# Pull the merged changes
git pull origin main

# Delete local feature branch
git branch -d feature/data-visualization

# Delete remote feature branch (optional)
git push origin --delete feature/data-visualization
```

## Example 2: Working with Forks

### The Scenario

You want to contribute to an open source project or the course repository.

### Step-by-Step

**1. Fork the repository on GitHub:**
- Go to the repository on GitHub
- Click "Fork" button in top right
- This creates your own copy

**2. Clone your fork:**
```bash
# Clone your fork (replace 'yourname' with your GitHub username)
git clone https://github.com/yourname/stat418-tools-in-datascience-2026.git
cd stat418-tools-in-datascience-2026
```

**3. Add upstream remote:**
```bash
# Add the original repo as 'upstream'
git remote add upstream https://github.com/natelangholz/stat418-tools-in-datascience-2026.git

# Verify remotes
git remote -v
# origin    https://github.com/yourname/stat418-tools-in-datascience-2026.git (your fork)
# upstream  https://github.com/natelangholz/stat418-tools-in-datascience-2026.git (original)
```

**4. Create a feature branch:**
```bash
# Always start from latest upstream
git checkout main
git fetch upstream
git merge upstream/main

# Create feature branch
git checkout -b fix/typo-in-readme
```

**5. Make your changes:**
```bash
# Edit files
nano README.md

# Commit changes
git add README.md
git commit -m "Fix typo in installation instructions"
```

**6. Push to your fork:**
```bash
# Push to your fork (origin)
git push origin fix/typo-in-readme
```

**7. Create Pull Request:**
- Go to original repository on GitHub
- Click "New pull request"
- Click "compare across forks"
- Select your fork and branch
- Create pull request

**8. Keep your fork updated:**
```bash
# Regularly sync with upstream
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
```

## Example 3: Collaborative Development

### The Scenario

Multiple team members are working on different features simultaneously.

### Team Member A: Working on Feature A

```bash
# Create feature branch
git checkout -b feature/user-authentication
# ... make changes ...
git add .
git commit -m "Add user authentication"
git push origin feature/user-authentication
# Create PR
```

### Team Member B: Working on Feature B

```bash
# Create different feature branch
git checkout -b feature/database-integration
# ... make changes ...
git add .
git commit -m "Add database connection"
git push origin feature/database-integration
# Create PR
```

### Both Features Get Merged

```bash
# Team Member A updates their local main
git checkout main
git pull origin main
# Now has both features

# Team Member B updates their local main
git checkout main
git pull origin main
# Now has both features
```

### Starting New Work

```bash
# Always start from updated main
git checkout main
git pull origin main
git checkout -b feature/new-feature
```

## Example 4: Reviewing Pull Requests

### As a Reviewer

**1. Check out the PR locally:**
```bash
# Fetch the PR branch
git fetch origin pull/123/head:pr-123
git checkout pr-123

# Or if it's from a fork
git fetch upstream pull/123/head:pr-123
git checkout pr-123
```

**2. Test the changes:**
```bash
# Run tests
python -m pytest

# Try the new feature
python new_feature.py

# Check code quality
# Review the code in your editor
```

**3. Leave feedback on GitHub:**
- Comment on specific lines
- Suggest improvements
- Approve or request changes

**4. After review:**
```bash
# Switch back to main
git checkout main

# Delete review branch
git branch -D pr-123
```

## Example 5: Handling Multiple Remotes

### The Scenario

You're working with your fork, the original repo, and maybe a team fork.

### Setup

```bash
# Your fork
git remote add origin https://github.com/yourname/repo.git

# Original repo
git remote add upstream https://github.com/original/repo.git

# Team fork
git remote add team https://github.com/team/repo.git

# List all remotes
git remote -v
```

### Fetching from Different Remotes

```bash
# Fetch from upstream
git fetch upstream

# Fetch from team
git fetch team

# Fetch from all remotes
git fetch --all
```

### Pushing to Different Remotes

```bash
# Push to your fork
git push origin feature-branch

# Push to team fork
git push team feature-branch
```

## Best Practices

### Branch Naming

```bash
# Good branch names
feature/user-login
fix/database-connection
hotfix/security-vulnerability
experiment/new-algorithm
docs/update-readme

# Bad branch names
my-branch
test
fix
new-stuff
```

### Commit Messages

```bash
# Good commit messages
git commit -m "Add user authentication with JWT tokens"
git commit -m "Fix database connection timeout issue"
git commit -m "Update README with installation instructions"

# Bad commit messages
git commit -m "fix"
git commit -m "update"
git commit -m "changes"
git commit -m "asdf"
```

### Pull Request Descriptions

**Good PR Description:**
```markdown
## What does this PR do?
Adds user authentication using JWT tokens.

## Why is this needed?
Users need to log in to access protected features.

## How was it tested?
- Unit tests for auth functions
- Manual testing of login flow
- Tested with invalid credentials

## Screenshots
[Include if UI changes]
```

**Bad PR Description:**
```markdown
updates
```

## Common Workflows

### Daily Workflow

```bash
# Morning: Start work
git checkout main
git pull origin main
git checkout -b feature/my-work

# During day: Make commits
git add .
git commit -m "Descriptive message"

# End of day: Push work
git push origin feature/my-work

# Next morning: Continue work
git checkout feature/my-work
git pull origin feature/my-work
# Continue working
```

### Before Creating PR

```bash
# Update your branch with latest main
git checkout main
git pull origin main
git checkout feature/my-work
git merge main

# Resolve any conflicts
# Test everything works
# Push updated branch
git push origin feature/my-work

# Create PR on GitHub
```

### After PR is Merged

```bash
# Update main
git checkout main
git pull origin main

# Delete feature branch
git branch -d feature/my-work
git push origin --delete feature/my-work

# Start new work
git checkout -b feature/next-task
```

## Troubleshooting

### "Your branch is behind"

```bash
# Pull latest changes
git pull origin main

# Or if you have local commits
git pull --rebase origin main
```

### "Your branch has diverged"

```bash
# If you haven't pushed yet
git pull --rebase origin main

# If you have pushed
git pull origin main
# Resolve conflicts
git push origin feature-branch
```

### "Cannot push to protected branch"

```bash
# Don't push directly to main
# Create a feature branch instead
git checkout -b feature/my-changes
git push origin feature/my-changes
# Create PR
```

### Accidentally committed to main

```bash
# Move commits to a new branch
git branch feature/my-work
git reset --hard origin/main
git checkout feature/my-work
```

## Practice Exercises

1. **Create a feature branch** and make some changes
2. **Push to GitHub** and create a pull request
3. **Fork a repository** and add the upstream remote
4. **Keep your fork updated** by fetching from upstream
5. **Review a classmate's PR** and leave constructive feedback

## GitHub-Specific Features

### GitHub Issues

**Create an Issue:**
```markdown
Title: Add data preprocessing pipeline

Description:
We need a preprocessing pipeline that:
- Handles missing values
- Normalizes numeric features
- Encodes categorical variables

Acceptance Criteria:
- [ ] Function handles all data types
- [ ] Unit tests cover edge cases
- [ ] Documentation includes examples

Labels: enhancement, data-processing
Assignee: @username
```

**Link Issues to PRs:**
```bash
# In PR description or commit message
git commit -m "Add preprocessing pipeline

Closes #42
Relates to #38"
```

### GitHub Actions (CI/CD)

**Basic workflow example** (`.github/workflows/test.yml`):
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest
```

See the LA Crime Analysis template for complete CI/CD examples.

### GitHub Projects

**Organize work:**
- Create project board
- Add Issues as cards
- Track progress: To Do → In Progress → Done
- Link PRs to Issues automatically

## Resources

- [GitHub Skills](https://skills.github.com/) - Interactive tutorials
- [GitHub Docs](https://docs.github.com/)
- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pull Request Best Practices](https://github.blog/2015-01-21-how-to-write-the-perfect-pull-request/)
- [LA Crime Analysis Template](https://github.com/[instructor-username]/la-crime-analysis) - Complete example