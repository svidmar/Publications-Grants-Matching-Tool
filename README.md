# Publications-Grants Matching Tool

This tool helps match research publications with research projects based on grant IDs. It queries OpenAlex to fetch publications associated with specific grants and funders, which can help in enriching local data and linking publications to projects and grants.

## Features

- Fetches research publications linked to a given **Grant ID** from OpenAlex.
- Allows **manual entry of a Grant ID** or **batch processing via an Excel file**.
- Retrieves publication details including:
  - **Title**
  - **DOI (clickable link)**
  - **Authors**
  - **Affiliated Institutions**
  - **Publication Year**
  - **Funder Name**
- Provides an **export feature** to download results as a CSV file.

## How to Use

### Option 1: Enter Grant ID Manually

1. Open the tool and select **Enter Grant ID Manually**.
2. Type in the Grant ID and press enter.
3. Select the appropriate **funder** (if multiple funders exist for the Grant ID).
4. Click **Fetch Publications** to retrieve results.

### Option 2: Upload an Excel File

1. Prepare an Excel file with a **GrantID** column (other columns are optional).
2. Upload the file using the file uploader.
3. Click **Fetch Publications from OpenAlex**.
4. Wait for the progress bar to complete.
5. View the retrieved publications and download them as a CSV file.

## Limitations

- **Data Quality**: Results depend on OpenAlex’s data coverage and accuracy.
- **Missing Links**: Not all publications explicitly reference a grant ID.
- **Grant ID Uniqueness**: The same Grant ID can be used by multiple funders, so the tool allows selection of a funder when conflicts arise.
- **Limited upload**: Excel uploads are limited to 100 Grant IDs to prevent timeouts and excessive load on the OpenAlex API. For larger datasets, fetch the data directly from OpenAlex 🙂 


## License

This project is licensed under the **MIT License**. See `LICENSE` for details.


---

🔗 Data retrieved from **[OpenAlex](https://openalex.org/)**  
📄 Project licensed under **MIT License**  
