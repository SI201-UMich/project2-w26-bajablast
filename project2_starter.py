# SI 201 HW4 (Library Checkout System)
# Your name:
# Your student id:
# Your email:
# Who or what you worked with on this homework (including generative AI like ChatGPT):
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
#
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity

this is a test
# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    with open(html_path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    listings = []
    seen_ids = set()

    # Look through all links and find ones that point to room pages
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        match = re.search(r"/rooms/(\d+)", href)
        if match:
            listing_id = match.group(1)

            # Try to get the title from link text first
            title = a.get_text(" ", strip=True)

            # Fallbacks if text is empty
            if not title:
                title = a.get("aria-label", "").strip()
            if not title:
                title = a.get("title", "").strip()

            if listing_id not in seen_ids and title:
                listings.append((title, listing_id))
                seen_ids.add(listing_id)

    return listings
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    base_dir = os.path.abspath(os.path.dirname(__file__))
    listing_path = os.path.join(base_dir, "html_files", f"listing_{listing_id}.html")

    with open(listing_path, "r", encoding="utf-8-sig") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    page_text = soup.get_text(" ", strip=True)

    # policy number
    policy_number = ""
    policy_match = re.search(r"(STR-\d{7}|Pending|Exempt)", page_text, re.IGNORECASE)
    if policy_match:
        policy_number = policy_match.group(1)
        if policy_number.lower() == "pending":
            policy_number = "Pending"
        elif policy_number.lower() == "exempt":
            policy_number = "Exempt"

    # host type
    host_type = "Not Superhost"
    if re.search(r"Superhost", page_text, re.IGNORECASE):
        host_type = "Superhost"

    # host name
    host_name = ""
    host_match = re.search(r"Hosted by\s+([A-Za-z]+)", page_text, re.IGNORECASE)
    if host_match:
        host_name = host_match.group(1)
    else:
        alt_host_match = re.search(r"hosted by\s+([A-Za-z]+)", page_text, re.IGNORECASE)
        if alt_host_match:
            host_name = alt_host_match.group(1)

    # room type
    room_type = ""
    room_type_match = re.search(
        r"(Entire room|Private room|Shared room|Hotel room|Entire place|Private room in|Shared room in|Room in)",
        page_text,
        re.IGNORECASE
    )

    if room_type_match:
        found = room_type_match.group(1).lower()
        if "entire" in found:
            room_type = "Entire Room"
        elif "private" in found:
            room_type = "Private Room"
        elif "shared" in found:
            room_type = "Shared Room"
        elif "hotel" in found:
            room_type = "Hotel Room"

    # location rating
    location_rating = 0.0
    location_match = re.search(r"Location\s*([0-9]\.[0-9])", page_text, re.IGNORECASE)
    if not location_match:
        location_match = re.search(r"Location rating\s*([0-9]\.[0-9])", page_text, re.IGNORECASE)
    if not location_match:
        location_match = re.search(r"([0-9]\.[0-9])\s*Location", page_text, re.IGNORECASE)

    if location_match:
        location_rating = float(location_match.group(1))

    return {
        listing_id: {
            "policy_number": policy_number,
            "host_type": host_type,
            "host_name": host_name,
            "room_type": room_type,
            "location_rating": location_rating
        }
    }
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    listings = load_listing_results(html_path)
    database = []

    for title, listing_id in listings:
        details = get_listing_details(listing_id)[listing_id]
        database.append((
            title,
            listing_id,
            details["policy_number"],
            details["host_type"],
            details["host_name"],
            details["room_type"],
            details["location_rating"]
        ))

    return database
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    data.sort(key=lambda x: x[6], reverse=True)

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        writer.writerow([
            "Listing Title",
            "Listing ID",
            "Policy Number",
            "Host Type",
            "Host Name",
            "Room Type",
            "Location Rating"
        ])

        for row in data:
            writer.writerow(row)
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    totals = {}
    counts = {}

    for row in data:
        room = row[5]
        rating = row[6]

        if rating != 0.0:
            if room not in totals:
                totals[room] = 0
                counts[room] = 0

            totals[room] += rating
            counts[room] += 1

    averages = {}
    for room in totals:
        averages[room] = totals[room] / counts[room]

    return averages
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    invalid = []

    for row in data:
        listing_id = row[1]
        policy = row[2]

        if policy != "Pending" and policy != "Exempt":
            if not re.fullmatch(r"20\d{2}-00\d{4}STR", policy) and not re.fullmatch(r"STR-\d{7}", policy):
                invalid.append(listing_id)

    return invalid
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # TODO: Check that the number of listings extracted is 18.
        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        pass

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # TODO: Call get_listing_details() on each listing id above and save results in a list.

        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        # 3) Check that listing 1944564 has the correct location rating 4.9.
        pass

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)

        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        pass

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        # TODO: Read the CSV back in and store rows in a list.
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].

        os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.
        pass

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        pass


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)