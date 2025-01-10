# README: CAS Search Engine

## Table of Contents

1.  **Installation**
2.  **Indexing Data**
3.  ***Testing Indexed Data (Optional)***
4.  **Launching the Search Engine in the Browser**

------------------------------------------------------------------------

## Note: Large indices files

~~This repository uses Git Large File Storage (LFS) to manage large files such as indexes.~~ *Removed because the free bandwidth was used up.
A demo mini-index from the “Information Retrieval” module takes the place of the index, which comprised 5 CAS.* 

------------------------------------------------------------------------

## 1. Installation Libs

Make sure the following libraries are installed:

-   pip install traceback

-   pip install multiprocessing

-   pip install tqdm

-   pip install PyPDF2

-   pip install whoosh

-   pip install whoosh-reloaded

-   pip install stopwords

-   pip install tkinter

-   pip install import

-   pip install markdown2

-   pip install nbconvert

-   pip install flask

------------------------------------------------------------------------

## 2. Indexing Data from Knlowledge Base

The script `directory_indexer.py` is used to index files from various
directories and store them in a Whoosh-compatible index.

### Steps:

1.  **Run the script**:

    ``` bash
    python directory_indexer.py
    ```

2.  **Select folders**:

    -   A dialog window will appear, allowing you to select multiple
        directories.
    -   After selecting one directory, you can add more or proceed.

3.  **Set the index storage location**:

    -   Choose a target directory where the index will be stored.

### Supported File Types:

-   `.pdf`
-   `.txt`
-   `.csv`
-   `.py`
-   `.ipynb`
-   `.html`
-   `.r`
-   `.qmd`
-   `.pptx`

### Error Handling:

-   Unsupported or faulty files will be logged.
-   An error log file, `error_log.txt`, will be created in the index
    storage location.

------------------------------------------------------------------------

## *3. Testing Indexed Data (Optional)*

The script `test_whoosh.py` verifies the content of the created index.

### Steps:

1.  **Run the script**:

    ``` bash
    python test_whoosh.py
    ```

2.  **Enter the index path**:

    -   Provide the path to the created index.

3.  **Analyze the output**:

    -   Displays an overview of stored fields and a preview of the first
        five documents in the index.

------------------------------------------------------------------------

## 4. Launching the Search Engine in the Browser

The script `whoosh_search.py` starts a Flask web application that
enables searching within the index.

### Steps:

1.  **Run the script**:

    ``` bash
    python whoosh_search.py
    ```

2.  **Open the browser**:

    -   Navigate to `http://127.0.0.1:5000`.

3.  **Submit search queries**:

    -   Enter the search term(s) in the search field.
    -   Results will be displayed in the browser.

### If you not use the cloned index, create your own:

-   And then ensure the index is created and the path in the script is
    correct:

    ``` python
    index_dir = r"YOUR_INDEX_PATH"
    ```

-   Invalid or incomplete search queries are handled, and appropriate
    error messages will be displayed.

------------------------------------------------------------------------

## Contact

If you encounter any issues or have questions, please contact the
developer. Good luck using the CAS Search Engine!
