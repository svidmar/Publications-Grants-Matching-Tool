import streamlit as st
import pandas as pd
import requests
import time

def fetch_funders_for_grant(grant_id):
    """Fetch list of funders for a specific Grant ID from OpenAlex."""
    url = f"https://api.openalex.org/works?filter=grants.award_id:{grant_id}"
    response = requests.get(url)
    
    if response.status_code != 200:
        st.error(f"Failed to fetch funders for Grant ID {grant_id} from OpenAlex.")
        return []
    
    try:
        data = response.json()
        works = data.get("results", [])
        funders = set()
        
        for work in works:
            for grant in work.get("grants", []):
                if grant.get("award_id") == grant_id and grant.get("funder_display_name"):
                    funders.add((grant["funder_display_name"], grant["funder"]))
        
        return list(funders)
    except Exception as e:
        st.error(f"Error processing OpenAlex response: {e}")
        return []

def query_openalex(grant_id, funder_id, funder_name):
    """Query OpenAlex API for publications related to a specific grant ID and funder."""
    url = f"https://api.openalex.org/works?filter=grants.award_id:{grant_id},grants.funder:{funder_id}"
    response = requests.get(url)
    
    if response.status_code != 200:
        st.error(f"Failed to fetch publications for Grant ID {grant_id} and Funder {funder_name} from OpenAlex.")
        return []
    
    try:
        publications = response.json().get("results", [])
        
        return [
            {
                "doi": pub.get("doi", "N/A"),
                "title": pub.get("title", "Unknown Title"),
                "authors": ", ".join([auth.get("author", {}).get("display_name", "Unknown") for auth in pub.get("authorships", [])]),
                "funder_display_name": funder_name,
                "publication_year": pub.get("publication_year", "Unknown"),
                "institutions": ", ".join(set(inst.get("display_name", "Unknown") for auth in pub.get("authorships", []) for inst in auth.get("institutions", [])))
            }
            for pub in publications
        ]
    except Exception as e:
        st.error(f"Error processing OpenAlex response: {e}")
        return []

def process_uploaded_file(uploaded_file):
    """Read the uploaded Excel file and process project details while limiting GrantIDs to 100."""
    df = pd.read_excel(uploaded_file)
    
    if 'GrantID' not in df.columns:
        st.error("Uploaded file must contain a column named 'GrantID'.")
        return None
    
    # Flattening multiple Grant IDs per row and counting unique ones
    df['GrantID'] = df['GrantID'].astype(str).apply(lambda x: x.split(','))
    unique_grant_ids = set(grant_id.strip() for ids in df['GrantID'] for grant_id in ids)
    
    # Enforce a limit of 100 unique Grant IDs
    if len(unique_grant_ids) > 100:
        st.error(f"Too many unique Grant IDs! The limit is 100, but {len(unique_grant_ids)} were found.")
        return None
    
    return df

def main():
    st.title("Publications-Grants Matching Tool")
    st.write("""
    ### About This Tool
    This simple tool helps identify research publications linked to specific research project grants by using grant IDs.  
    It queries [OpenAlex](https://openalex.org) to retrieve publications associated with grants and funders, helping enrich local datasets, identify output related to a specific grant and potentially establish connections between research outputs, projects, and funding sources in other systems.  


    ### How to Use:
    - **Upload an Excel file** containing a column labeled "GrantID" to process multiple grant IDs at once, **OR**
    - **Manually enter a Grant ID** to search for related publications to a single grant ID.  
    - Select the appropriate funder if multiple funders use the same grant ID.  
    - Export matched results as a CSV file for further analysis.  
    
    ### **Limitations:** 
    - The accuracy of results depends on OpenAlex’s data coverage and quality.  
    - Not all research publications explicitly reference a grant ID, so some relevant outputs may be missing.  
    - Grant IDs **are not unique**—multiple funders may use the same ID. The tool provides a list of funders associated with the entered grant ID to ensure correct selection.  
    - Data on grants and publications is still an evolving area in schloarly publishing, so mismatches or missing records may occur.  
    - Automating the process of linking publications to grants in local systems would obviously be useful, but approach this with caution—funding information data quality can still be inconsistent. It’s advisable to have a quality check in place.
    - Excel uploads are limited to 100 Grant IDs to prevent timeouts and excessive load on the OpenAlex API. For larger datasets, fetch the data directly from OpenAlex 🙂 

    ### **License:** MIT License

    ### **Creator:** 
    **Søren Vidmar**
    - https://orcid.org/0000-0003-3055-6053  
    - 🏫 Aalborg University
    - 📧 Email: [sv@aub.aau.dk](mailto:sv@aub.aau.dk)  
    - 🏗 GitHub: [github.com/svidmar](https://github.com/svidmar)

    """)
    
    option = st.radio("Choose Input Method:", ("Upload Excel File", "Enter Grant ID Manually"))
    
    publication_results = []
    
    if option == "Upload Excel File":
        uploaded_file = st.file_uploader("Upload Excel file with at least a 'GrantID' column", type=["xls", "xlsx"])
        
        if uploaded_file is not None:
            df = process_uploaded_file(uploaded_file)
            if df is not None:
                st.write("### Processed Grants:")
                st.dataframe(df)
                
                if st.button("Fetch Publications from OpenAlex"):
                    progress_bar = st.progress(0)
                    total_grants = sum(len(row['GrantID']) for _, row in df.iterrows())
                    completed = 0
                    
                    for _, row in df.iterrows():
                        for grant_id in row['GrantID']:
                            funders = fetch_funders_for_grant(grant_id.strip())
                            for funder_name, funder_id in funders:
                                publications = query_openalex(grant_id.strip(), funder_id, funder_name)
                                
                                if publications:
                                    publication_results.append({
                                        "Grant ID": grant_id,
                                        "Funder": funder_name,
                                        "Publications": publications
                                    })
                                
                                completed += 1
                                progress_bar.progress(min(completed / total_grants, 1.0))
                                time.sleep(1 / 10)
                    
                    progress_bar.empty()
    
    elif option == "Enter Grant ID Manually":
        grant_id_input = st.text_input("Enter Grant ID")
        funders = fetch_funders_for_grant(grant_id_input.strip()) if grant_id_input else []
        
        if funders:
            funder_selection = st.radio("Select Funder", [name for name, _ in funders])
            funder_id = next(fid for fname, fid in funders if fname == funder_selection)
            
            if st.button("Fetch Publications"):
                publications = query_openalex(grant_id_input.strip(), funder_id, funder_selection)
                if publications:
                    publication_results.append({
                        "Grant ID": grant_id_input,
                        "Funder": funder_selection,
                        "Publications": publications
                    })
    
    if publication_results:
        results_df = []
        for result in publication_results:
            for pub in result['Publications']:
                results_df.append(pub)
        
        if results_df:
            results_df = pd.DataFrame(results_df)
            csv = results_df.to_csv(index=False).encode('utf-8')

            # Move the download button to the top
            st.download_button("Download Results as CSV", csv, "publications.csv", "text/csv")

        st.write("### Publications Found:")
        
        for result in publication_results:
            st.subheader(f"Grant ID: {result['Grant ID']} (Funder: {result['Funder']})")
            for pub in result['Publications']:
                with st.expander(f"{pub['title']} ({pub['publication_year']})"):
                    doi_link = f"[https://doi.org/{pub['doi'].replace('https://doi.org/', '')}](https://doi.org/{pub['doi'].replace('https://doi.org/', '')})"
                    st.markdown(f"**DOI:** {doi_link}")
                    st.write(f"**Authors:** {pub['authors']}")
                    st.write(f"**Institutions:** {pub['institutions']}")
                    st.write(f"**Funder:** {pub['funder_display_name']}")

if __name__ == "__main__":
    main()
