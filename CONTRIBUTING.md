# Contribution Guidelines

1. Create a new branch with your initials (nameSurname) and a descriptive name:
   ```bash
   git checkout -b ns/your-feature-name
   ```

> [!NOTE]
> When using VS Code, you should install the [recommended extions](./.vscode/extensions.json) to ensure a consistent development environment. This includes tools for code formatting, linting, and other helpful features that will make your contribution process smoother. 
> - [Ruff](https://docs.astral.sh/ruff/) for python linting and code formatting.
> - Python Extension Pack for Python development, including features like IntelliSense, debugging, and more.
> - [Prettier](https://prettier.io/) for formatting other code and other files.
> - GitGraph for visualizing the git history and branches.


2. Make your changes.
3. Commit them with a descriptive message (see [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)).
4. Push your branch to the remote repository:
   ```bash
   git push origin ns/your-feature-name
   ```
5. Create a [pull request on GitHub](https://github.com/dobe-1/CoffeeFinder/pulls) and describe your changes in detail.

## Strucure of the Repository
- `backend/`: Contains the backend code for the CoffeeFinder application, including data collection and processing scripts.
- `frontend/`: Contains the frontend code for the CoffeeFinder application, including the user interface and related assets.

You can write your logic code in the `backend/` directory. There you can create a new component for your feature either for scraping, data processing, or any other logic. Your could component should be work on its own and should also be importable in other components. 


## Useful Commands

- To check the status of your branch:
  ```bash
  git status
  ```
- To create and switch to a new branch:
  ```bash
  git checkout -b ns/your-feature-name
  ```
- To switch back to the main branch:
  ```bash
  git checkout main
  ```
- To add changes to the staging area:
  ```bash
  git add .
  ```
- To commit changes with a message:
  ```bash
  git commit -m "feat: add new feature" 
    ```
- To commit changes and add message interactively:
  ```bash
  git commit
  ```
- To add your changes to the previous commit (if you forgot to add something):
  ```bash
  git add .
  git commit --amend
  ```
- To push your branch to the remote repository:
  ```bash
  git push origin ns/your-feature-name
  ```