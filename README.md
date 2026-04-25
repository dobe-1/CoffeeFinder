# CoffeeFinder 

CoffeeFinder is a web application that helps users find nearby coffee shops with the best quality-price ratio. It provides an interactive map and a list of coffee shops based on the user's location. It is built as an OSINT (Open Source Intelligence) project, and all the information about the coffee shops is collected from various public sources.

> [!NOTE]
> If you want to contribute to this project, please read the [CONTRIBUTING.md](./CONTRIBUTING.md) file for guidelines on how to get started and make your contributions.


## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/dobe-1/CoffeeFinder.git
   ```
2. Navigate to the project directory:
   ```bash
   cd CoffeeFinder
   ```
3. Install the required dependencies. Herefor, you can use [`uv`](https://docs.astral.sh/uv/):
   ```bash
   uv sync
   ```
   This will create a [virtual environment](https://docs.python.org/3/library/venv.html) and install all the necessary packages.
4. If not already done, activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

## Usage

Currently, the application is in the early stages of development, and there is no user interface yet. However, you can run the main script to see how it collects data about coffee shops:

```bash
python backend/src/main.py  
```