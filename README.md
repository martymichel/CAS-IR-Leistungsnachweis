
# README: CAS Search Engine

## Table of Contents

1. **Indexing Data**
2. **Testing Indexed Data (Optional)**
3. **Launching the Search Engine in the Browser**

---

## 1. Indexing Data

The script `directory_indexer.py` is used to index files from various directories and store them in a Whoosh-compatible index.

### Steps:

1. **Run the script**:
   ```bash
   python directory_indexer.py
   ```
2. **Select folders**:
   - A dialog window will appear, allowing you to select multiple directories.
   - After selecting one directory, you can add more or proceed.
3. **Set the index storage location**:
   - Choose a target directory where the index will be stored.

### Supported File Types:

- `.pdf`
- `.txt`
- `.csv`
- `.py`
- `.ipynb`
- `.html`
- `.r`
- `.qmd`
- `.pptx`

### Error Handling:

- Unsupported or faulty files will be logged.
- An error log file, `error_log.txt`, will be created in the index storage location.

---

## 2. Testing Indexed Data (Optional)

The script `test_whoosh.py` verifies the content of the created index.

### Steps:

1. **Run the script**:
   ```bash
   python test_whoosh.py
   ```
2. **Enter the index path**:
   - Provide the path to the created index.
3. **Analyze the output**:
   - Displays an overview of stored fields and a preview of the first five documents in the index.

---

## 3. Launching the Search Engine in the Browser

The script `whoosh_search.py` starts a Flask web application that enables searching within the index.

### Steps:

1. **Run the script**:
   ```bash
   python whoosh_search.py
   ```
2. **Open the browser**:
   - Navigate to `http://127.0.0.1:5000`.
3. **Submit search queries**:
   - Enter the search term in the search field.
   - Results will be displayed in the browser.

### Notes:

- Ensure the index is created and the path in the script is correct:
  ```python
  index_dir = r"P:\PY\CAS IR Leistungsnachweis\whoosh_index"
  ```
- Invalid or incomplete search queries are handled, and appropriate error messages will be displayed.

---

## Contact

If you encounter any issues or have questions, please contact the developer. Good luck using the CAS Search Engine!
