# Sound of Slience

## Table of Contents
1. [Installation](#installation)
2. [Project Structure](#project-structure)
3. [Usage](#usage)
    1. [Data Processing Procedure](#data-processing-procedure)
    2. [Running applications](#running-applications)
4. [Contributing](#contributing)
5. [License](#license)


## Installation
Make sure you have Python and Node.js installed. To download Node.js, please visit [Node.js](https://nodejs.org/en/download) official website.

1. Create a virtual environment
    ```bash
    python -m venv venv
    ```

2. Activate the virtual environment
    ```bash
    source venv/bin/activate
    ```

3. To install the dependencies required for this project, run the following command:
    ```bash
    pip install -r requirements.txt
    ```

4. Install `serve`
    ```bash
    npm install serve
    ```

## Project Structure

The project follows the following directory structure:
```bash
┌-─ assets
│   ├── css
│   │   ├── **/*.css
│   ├── favicon.ico
│   ├── images
├── data
│   ├── participant1
│   │   ├── google-takeout
│   │   │   ├── Semantic-Location-History
│   │   ├── instagram
│   │   │   ├── **
│   │   │   ├── media
│   │   │   │   ├── stories
│   │   │   │   │   ├── 20****
│   │   │   │   │   │   ├── 20****
├── README.md
├── config.py
├── requirements.txt
├── .gitignore
└── ...
```

## Setup API Key
In `config.py` file, enter your API Key for [Novita.ai](https://novita.ai/) and [AILab](https://www.ailabtools.com/)
```python
TEXT_REMOVAL_API_KEY=
BLUR_FACE_API_KEY= 
```

## Validation 

To start the validator app, you can run the following command in Terminal:

```bash
python validator.py ./data/participant1/google-takeout/Semantic-Location-History ./data/output/participant1
```
Then, a localhost url will be shown in Terminal (e.g. http://127.0.0.1:8050/). Open the url in your preferred browser. 

If you are interested, you can find the anonymized data saved under `./data/output/participant1` directory.


## Data Processing Procedure

1. process location data
    ```bash
    python main.py <path-to-Semantic-Location-History-folder> <path-to-output-folder> <path-to-stories.json-file>
    ```
    - The following questions will be prompted in Terminal:
        1. Fiter Locations?
            - Enter `true` if you want to filter locations on specific keywords; `false` otherwise
        2. Enter the list of filtering keywords separated by spaces:
            - Enter a list of keywords you want to filter on
            - If no keywords entered, the default list of keywords will be used
        3. Enter the filename for the output file (without .json extension)
            - Input a custom filename for the GeoJson file containing the points after filtering

2. Anonymize images
    ```bash
    python anonymize_image.py <path-to-Instagram-images-folder> <path-to-output-folder>
    ```
    - E.g.: 
        ```bash
        python anonymize_image.py ./data/Instagram/media/stories ./data/output
        ```

## Running applications

The project structure is expected as following (it doesn't have to be):
```bash
┌-─ ...
├── data
│   ├── anonymized_images
│   │   ├── participant1
│   │   │   ├── ***.jpg
│   │   │   ├── ...
│   │   ├── participant2
│   │   │   ├── ***.jpg
│   │   │   ├── ...
└── ...
```

1. Serving static files
    1. Navigate to a paricipant's processed images folder
        - E.g.
        ```bash
        cd ./data/anonymized_images
        ```
    2. Run the server
        ```bash
        npx serve
        ```

## Running Kepler.gl
    1. 
    ```bash
    yarn
    ```

    2. 
    ```bash
    yarn start
    ```
