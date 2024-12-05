import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# The base URL of the directory.
# Update this to match the current URL for the year's census. It will likely be the same, but with a different year.
# By default, this is set to grab all relevant data from the 2020 census.
# If you are using a different year's data, make sure to update the URL below accordingly.
base_url = "https://www2.census.gov/geo/maps/DC2020/PL20/"

# Create a directory to save the files
# This directory will hold all the downloaded .txt files containing "CT2MS".
os.makedirs('census_files', exist_ok=True)

def downloadCt2msFiles(url, save_dir):
    """
    Downloads all .txt files containing "CT2MS" from the given URL and saves them to the specified directory.
    
    Args:
        url (str): The URL to scrape for files.
        save_dir (str): The directory where the downloaded files should be saved.
    """
    # Get the HTML content of the directory page
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve contents from {url}. HTTP Status Code: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all links on the page
    for link in soup.find_all('a'):
        file_name = link.get('href')

        # Check if file_name is not None and it's a .txt file containing "CT2MS"
        if file_name and "CT2MS" in file_name and file_name.endswith('.txt'):
            file_url = urljoin(url, file_name)
            print(f"Downloading {file_name} from {file_url}...")
            response = requests.get(file_url)
            if response.status_code == 200:
                with open(os.path.join(save_dir, file_name), 'wb') as f:
                    f.write(response.content)
            else:
                print(f"Failed to download {file_name} from {file_url}. HTTP Status Code: {response.status_code}")

def traverseDirectories(base_url, save_dir):
    """
    Traverses through the base directory URL to find and download CT2MS .txt files from all valid state directories.
    
    Args:
        base_url (str): The base URL containing state directories.
        save_dir (str): The base directory to save the downloaded files.
    """
    # Get the HTML content of the base directory page
    response = requests.get(base_url)
    if response.status_code != 200:
        print(f"Failed to retrieve contents from {base_url}. HTTP Status Code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all directories starting with "st" and within the range "st01" to "st56"
    # Each folder will have the same number as a state's GEOID. For example, Texas will be 48.
    # NOTE: This will also download files with data for U.S. Territories such as Guam and the Virgin Islands.
    for link in soup.find_all('a'):
        dir_name = link.get('href')
        # If a directory's name starts with 'st'
        if dir_name and dir_name.startswith('st'):
            # Extract the numeric part and check if it's within the desired range
            num_part = ''.join(filter(str.isdigit, dir_name))
            if num_part and 1 <= int(num_part) <= 56:
                # Navigate to the censustract_maps directory within the valid stXX directory
                st_dir_url = urljoin(base_url, dir_name.strip('/'))  # Strip trailing slashes to avoid issues
                censustract_maps_url = urljoin(st_dir_url + '/', 'censustract_maps/')
                
                # Get the HTML content of the censustract_maps directory
                response = requests.get(censustract_maps_url)
                if response.status_code != 200:
                    print(f"Failed to retrieve contents from {censustract_maps_url}. HTTP Status Code: {response.status_code}")
                    continue

                soup = BeautifulSoup(response.text, 'html.parser') # Parse the HTML content of the directory

                # Loop through all subdirectories within censustract_maps
                for subdir_link in soup.find_all('a'):
                    subdir_name = subdir_link.get('href')
                    if subdir_name and subdir_name.endswith('/'):
                        final_dir_url = urljoin(censustract_maps_url, subdir_name)
                        # Clean the directory name to avoid any unwanted characters
                        valid_dir_name = os.path.basename(os.path.normpath(subdir_name.strip('/')))
                        final_save_dir = os.path.join(save_dir, dir_name.strip('/'), valid_dir_name)
                        os.makedirs(final_save_dir, exist_ok=True)

                        # Download the CT2MS .txt files in this final directory
                        downloadCt2msFiles(final_dir_url, final_save_dir)

# Start the traversal and download process
# This function will go through the provided base_url and download all matching files.
# NOTE: By default, this will create a new folder called 'census_files' if one does not exist. If you would
# like to change the name of this folder, simply change the name in the function below.
traverseDirectories(base_url, 'census_files')