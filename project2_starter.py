# SI 201 HW4 (Library Checkout System)
# Your name: Devin Benson & Alyssa Davis
# Your student id:80095600 & 80936839
# Your email:devinben@umich.edu & aljdavis@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT): Devin Benson, Alyssa Davis, and Chatgpt
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
# Used ChatGPT for debugging help, understanding errors, and improving code structure
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#Yes,  used it  for guidance and learning rather than copying full solutions
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


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

    title_divs = soup.find_all(id=re.compile(r"^title_\d+$"))

    for div in title_divs:
        listing_title = div.get_text(strip=True)
        listing_id = div["id"].replace("title_", "")
        listings.append((listing_title, listing_id))

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
    policy_match = re.search(r"Policy number:\s*(20\d{2}-00\d{4}STR|STR-\d{7}|\d+)", page_text)

    if policy_match:
        raw_policy = policy_match.group(1)

        if re.fullmatch(r"20\d{2}-00\d{4}STR", raw_policy) or re.fullmatch(r"STR-\d{7}", raw_policy):
            policy_number = raw_policy
        else:
            policy_number = raw_policy
    elif re.search(r"Pending", page_text, re.IGNORECASE):
        policy_number = "Pending"
    elif re.search(r"Exempt", page_text, re.IGNORECASE):
        policy_number = "Exempt"

    # host type
    host_type = "regular"
    if "Superhost" in page_text:
        host_type = "Superhost"

    # host name
    host_name = ""
    host_match = re.search(r"hosted by\s+([A-Za-z]+(?:\s+(?:And|and)\s+[A-Za-z]+)?)", page_text)

    if host_match:
        host_name = host_match.group(1).replace("\xa0", " ")

    # room type
    room_type = ""
    subtitle_match = re.search(r"(Entire|Private|Shared)[^\.]*?(?=hosted by)", page_text, re.IGNORECASE)

    if subtitle_match:
        subtitle = subtitle_match.group(0)

        if "Private" in subtitle:
            room_type = "Private Room"
        elif "Shared" in subtitle:
            room_type = "Shared Room"
        else:
            room_type = "Entire Room"

    # location rating
    location_rating = 0.0
    location_match = re.search(r"Location\s+([0-9]\.[0-9])", page_text)

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
    url = "https://scholar.google.com/scholar"

    params = {
        "q": query
    }

    response = requests.get(url, params=params)

    soup = BeautifulSoup(response.text, "html.parser")

    titles = []

    results = soup.find_all("h3")

    for result in results:
        title = result.get_text(strip=True)

        if title:
            titles.append(title)

    return titles
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
        self.assertEqual(len(self.listings), 18)
        self.assertEqual(self.listings[0], ("Loft in Mission District", "1944564"))


    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]
        results = []

        for listing_id in html_list:
            results.append(get_listing_details(listing_id))

        self.assertEqual(results[0]["467507"]["policy_number"], "STR-0005349")
        self.assertEqual(results[2]["1944564"]["host_type"], "Superhost")
        self.assertEqual(results[2]["1944564"]["room_type"], "Entire Room")
        self.assertEqual(results[2]["1944564"]["location_rating"], 4.9)


    def test_create_listing_database(self):
        for row in self.detailed_data:
            self.assertEqual(len(row), 7)

        self.assertEqual(
            self.detailed_data[-1],
            ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8)
        )


    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        output_csv(self.detailed_data, out_path)

        rows = []
        with open(out_path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(row)

        self.assertEqual(
            rows[1],
            ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"]
        )

        os.remove(out_path)


    def test_avg_location_rating_by_room_type(self):
        result = avg_location_rating_by_room_type(self.detailed_data)
        self.assertEqual(result["Private Room"], 4.9)


    def test_validate_policy_numbers(self):
        invalid_listings = validate_policy_numbers(self.detailed_data)
        self.assertEqual(invalid_listings, ["16204265"])


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)