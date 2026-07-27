# CoffeeFinder 

CoffeeFinder is a study project which aims to create a CoffeeIndex, similar to the [BigMacIndex](https://en.wikipedia.org/wiki/Big_Mac_Index), but for coffee and for Germany. It provides an interactive map and a list of coffee shops based on the user's selected location. It is built as an OSINT (Open Source Intelligence) project, and all the information about the coffee shops is collected from various public sources. 

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

   Image OCR uses `pytesseract`, which also requires the native Tesseract binary. On Ubuntu/Debian:
   ```bash
   sudo apt install tesseract-ocr tesseract-ocr-deu
   ```
4. If not already done, activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

## Usage

### Backend

You can use the fastapi backend by running the following command in the terminal:

```bash
uvicorn backend.main:app --port 8080 
```

Then open your web browser and navigate to http://localhost:8080/docs to access the API documentation and test the endpoints. There is currently one enddpoint available:
- `GET /coffee-shops`: This endpoint retrieves a list of coffee shops based on the city provided as a query parameter.


### Frontend

To run the frontend, navigate to the `frontend` directory and start the development server:

```bash
cd frontend
ng serve
```

More information about the frontend can be found in the [frontend/README.md](./frontend/README.md) file.

## License

Code and data in this repository are licensed separately:

- **Source code** — [GPL-3.0](./LICENSE)
- **Datasets** (`store/`, `frontend/public/data/`, `test_sets/`) — see [LICENSE.md](./store/LICENSE)

Café locations are derived from [OpenStreetMap](https://www.openstreetmap.org/),
© OpenStreetMap contributors, available under the
[Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
Menu and price information was collected from publicly accessible café websites
and is provided for academic research only, without warranty.
