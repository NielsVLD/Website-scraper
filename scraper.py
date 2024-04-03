import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv


def scrape_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        data_list = [
            item.text.strip()
            for item in soup.find_all(
                text=lambda text: text and os.getenv("CITY") in text and text.strip() != os.getenv("REMOVETEXT")
            )
            if len(item.text.strip()) >= 50
        ]
        return data_list
    else:
        print(f"Failed to fetch data from {url}")
        return []


def extract_text_between(text, *pairs):
    for pair in pairs:
        start, end = pair
        start_index = text.find(start)
        end_index = text.find(end, start_index)
        if start_index != -1 and end_index != -1:
            return text[start_index + len(start):end_index].strip()
    return ""


def main():
    load_dotenv()

    base_url = os.getenv("URL")
    page_param = '?p='

    # Change this var to specify how much data you want to fetch from the site. With the higher number being more pages that are scraped from on the site.
    max_pages = 10

    all_data = []

    for page_number in range(1, max_pages + 1):
        page_url = f"{base_url}{page_param}{page_number}"
        page_data = scrape_page(page_url)
        all_data.extend(page_data)

    start_string = os.getenv("FILTER_FIRST_PART")
    end_string = os.getenv("FILTER_SECOND_PART")

    pairs_bedrijfsnaam = [
        ("De besloten vennootschap", start_string),
        ("De onderneming", start_string),
        ("De vennootschap onder firma", start_string),
        ("De stichting", start_string),
        ("De vereniging", start_string)
    ]

    pairs_address = [(start_string, end_string)]

    filtered_data_bedrijfsnaam = [extract_text_between(entry, *pairs_bedrijfsnaam) for entry in all_data]
    filtered_data_address = [extract_text_between(entry, *pairs_address) for entry in all_data]

    data = {'Bedrijfsnaam': filtered_data_bedrijfsnaam, 'Address': filtered_data_address}
    df = pd.DataFrame(data)

    df = df.dropna()

    if not df.empty:
        excel_filename = 'data.xlsx'
        current_directory = os.getcwd()
        excel_filepath = os.path.join(current_directory, excel_filename)
        df.to_excel(excel_filepath, index=False)
        print(f'Data saved to {excel_filepath}')
    else:
        print("No data found.")


if __name__ == "__main__":
    main()
