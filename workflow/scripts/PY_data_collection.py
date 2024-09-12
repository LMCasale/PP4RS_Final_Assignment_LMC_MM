# Import necessary modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
import os
import time 


# Configure Chrome options to disable the search engine choice screen
chrome_options = Options()
chrome_options.add_argument("--disable-search-engine-choice-screen")
driver = webdriver.Chrome(options=chrome_options)

base_dir = os.path.dirname(os.path.realpath(__file__))
print(base_dir)

for congr in range(112, 117):
    # Define the base URL for searching congressional bills on congress.gov
    base_url = f"https://www.congress.gov/search?s=9&q=%7B%22source%22%3A%22legislation%22%2C%22type%22%3A%22bills%22%2C%22congress%22%3A%5B%22{congr}%22%5D%2C%22chamber%22%3A%22House%22%7D"
    output_file = os.path.abspath(os.path.join(base_dir, "../data", f"bills_data_{congr}.csv"))

    # Check if the file already exists, and if it does, load it
    if os.path.exists(output_file):
        existing_data = pd.read_csv(output_file)
        existing_bills = set(existing_data['bill_href'].tolist())
        page_counts = existing_data['page'].value_counts().to_dict()  # Get the counts of bills per page
    else:
        existing_data = pd.DataFrame()
        existing_bills = set()
        page_counts = {}

    driver.get(base_url)

    # Wait until the pagination element is present and extract the total number of pages
    pagination_text = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'pagination'))
    ).text
    total_pages = int(re.search(r'of (\d+)', pagination_text).group(1))  # Extract total number of pages from the text

    # Loop through all pages using tqdm for progress tracking
    for page in tqdm(range(1, total_pages + 1), desc=f"Congress {congr}, Processing Pages"):
        # If the page already has 100 entries, skip it
        if page_counts.get(page, 0) == 100:
            tqdm.write(f"\nPage {page} already has 100 bills. Skipping...")
            continue
        else:
            existing_bills_count = page_counts.get(page, 0)
            tqdm.write(f"\nPage {page} currently has {existing_bills_count} bills.")

        url = f"{base_url}&page={page}"  # Construct the URL for the current page
        driver.get(url)
        try:
            # Wait until the list items containing bill details are loaded
            items = WebDriverWait(driver, 60).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.expanded"))
            )
    
            # Loop through each item on the page
            for item in items:
                signal = 0
                # Initialize an empty list to store the new data for this page
                new_data = []
                # Extract the bill's hyperlink
                bill_href = item.find_element(By.CSS_SELECTOR, "span.result-heading a").get_attribute("href")
                bill_id = item.find_element(By.CSS_SELECTOR, "span.result-heading a").get_attribute("text").split(".")[2]
                # Skip this bill if it's already in the existing data
                if bill_href in existing_bills:
                    continue
    
                # Extract the congress ID from the hyperlink
                congress_id = re.search(r'/(\d+)', bill_href).group(1)
                # Extract the title of the bill
                title = item.find_element(By.CSS_SELECTOR, "span.result-title").text.strip()
    
                # Extract sponsor details (first sponsor in the list)
                sponsor_section = item.find_elements(By.CSS_SELECTOR, "span.result-item")[0]
                sponsor_raw = sponsor_section.find_element(By.TAG_NAME, "a").text.strip()
                # Use regular expressions to extract sponsor's name, title, party, state, and district
                sponsor_parts = re.search(r'(.+?),\s+(.+?)\s+\[(.+?)-([A-Za-z]+)-([A-Z]{2})-([0-9]+|At Large)\]', sponsor_raw)
                sponsor_last_name = sponsor_parts.group(1)
                sponsor_first_name = sponsor_parts.group(2)
                sponsor_title = sponsor_parts.group(3)
                sponsor_party = sponsor_parts.group(4)
                sponsor_state = sponsor_parts.group(5)
                sponsor_district = sponsor_parts.group(6)
    
                # Extract the number of cosponsors
                n_cosponsor = int(re.search(r'Cosponsors:\s*\((\d+)\)', sponsor_section.text.strip()).group(1))
                same_party, same_state, same_party_state = 0, 0, 0  # Initialize counts for cosponsors of the same party and/or state
        
                # If there are cosponsors, navigate to the cosponsor page and extract details
                if n_cosponsor > 0:
                    cosponsor_element = sponsor_section.find_elements(By.XPATH, ".//strong[contains(text(), 'Cosponsors:')]/following-sibling::a")[0]
                    cosponsor_url = cosponsor_element.get_attribute("href")
    
                    # Open cosponsor page in a new tab
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[1])
                    driver.get(cosponsor_url)
                    try:
    
                        # Wait for the cosponsors to load and extract details
                        cosponsors = WebDriverWait(driver, 60).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr"))
                        )
                        
                        time.sleep(1)
                        
                        for cosponsor in cosponsors:
                            # Extract cosponsor party, state, and district information using regex
                            party_state_district = re.search(r'\[([A-Z])\-([A-Z]{2})\-(\d+|At Large)\]', cosponsor.text.strip())
        
                            if party_state_district:
                                cosponsor_party = party_state_district.group(1)
                                cosponsor_state = party_state_district.group(2)
                                cosponsor_district = party_state_district.group(3)
        
                                # Increment counters based on party and state matches
                                if cosponsor_party == sponsor_party:
                                    same_party += 1
                                if cosponsor_state == sponsor_state:
                                    same_state += 1
                                if cosponsor_party == sponsor_party and cosponsor_state == sponsor_state:
                                    same_party_state += 1
        
                        # Close the cosponsor tab and switch back to the main tab
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    except:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        signal = 1
                        pass
        
                # Extract the committee information
                committee_section = item.find_elements(By.CSS_SELECTOR, "span.result-item")[1]
                committee = committee_section.text.strip().replace("Committees:", "").strip()
        
                # Extract the bill's status
                status_section = item.find_element(By.CSS_SELECTOR, "span.result-item.result-tracker")
                status = status_section.find_element(By.CSS_SELECTOR, "p.hide_fromsighted").text.strip().replace("This bill has the status ", "").strip()
                    
                if signal == 0:
                # Append the extracted information to the new_data list
                    new_data.append({
                        "congress_id": congress_id,
                        "page": page,
                        "bill_id": bill_id,
                        "bill_href": bill_href,
                        "title": title,
                        "sponsor": sponsor_last_name + ", " + sponsor_first_name,
                        "sponsor_party": sponsor_party,
                        "sponsor_state": sponsor_state,
                        "sponsor_district": sponsor_district,
                        "n_cosponsor": n_cosponsor,
                        "same_party": same_party,
                        "same_state": same_state,
                        "same_party_state": same_party_state,
                        "committee": committee,
                        "status": status
                        })
                    
                    # Convert new data to a DataFrame and append it to the CSV
                    if new_data:
                        new_df = pd.DataFrame(new_data)
                        
                        # Append to existing data
                        existing_data = pd.concat([existing_data, new_df], ignore_index=True)
                            
                        existing_data['congress_id'] = existing_data['congress_id'].astype(str)
                        existing_data['page'] = existing_data['page'].astype(str)
                        existing_data['bill_id'] = existing_data['bill_id'].astype(str)
                    
                        # Remove duplicates across entire rows
                        existing_data = existing_data.drop_duplicates()
                    
                        # Sort the new data by congress_id, page, and bill_id in decreasing order
                        existing_data = existing_data.sort_values(by=['congress_id', 'page', 'bill_id'], ascending=[False, True, False])
                    
                        # Append the cleaned data to the CSV
                        existing_data.to_csv(output_file, index=False)
                    
                        # Update the set of existing bills and page counts
                        existing_bills.update(existing_data['bill_href'].tolist())
                        page_counts[page] = page_counts.get(page, 0) + len(existing_data)

                else:
                    pass
        except:
            pass
# Quit the browser once the process is complete
driver.quit()

data_dir = os.path.abspath(os.path.join(base_dir, "../data"))

print(snakemake.output[0])

# Create an empty DataFrame to store the combined data
combined_df = pd.DataFrame()

# List all CSV files in the directory, sort them alphabetically
csv_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.csv')])

# Iterate over the sorted CSV files and append their data
for csv_file in csv_files:
    file_path = os.path.join(data_dir, csv_file)
    df = pd.read_csv(file_path)
    combined_df = pd.concat([combined_df, df], ignore_index=True)

# Save the combined DataFrame as a new CSV file
combined_df.to_csv(snakemake.output[0], index=False)
