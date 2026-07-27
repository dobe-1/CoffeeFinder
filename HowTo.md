# How to Use the Coffee Finder

1. Checkout to my branch `db/interactive-map` 
2. In the first terminal window run the backend server: 
    ```sh 
    uv run uvicorn backend.main:app --port 8080 --reload
    ```
2. In the second terminal window run the frontend server. To do so, navigate to the `frontend` directory: 
    ```sh
    cd frontend
    ```
    It is necessary to install the dependencies first by running 
    ```sh
    npm install
    ```
    After that, run the following command:
    ```sh
    ng serve
    ```
3. Open your browser and navigate to `http://localhost:4200`. You should see a map centered on Bochum, Germany, with markers indicating the locations of coffee shops. Click on the markers to see the name and website of each coffee shop.