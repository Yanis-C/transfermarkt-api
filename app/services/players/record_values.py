from dataclasses import dataclass
from datetime import datetime
from xml.etree import ElementTree

from app.services.base import TransfermarktBase
from app.utils.regex import REGEX_CHART_CLUB_ID
from app.utils.utils import extract_from_url, safe_regex, trim
from app.utils.xpath import Players


@dataclass
class TransfermarktPlayerRecordValues(TransfermarktBase):
    """
    A class for football players with record market values on Transfermarkt.

    Args:
        URL (str): The URL template for the search query.
        page_number (int): The page number of search results (default is 1).
    """

    URL: str = (
        "https://www.transfermarkt.com/spieler-statistik/rekordmarktwerte/marktwertetop?page={page_number}"
    )
    page_number: int = 1

    def __post_init__(self) -> None:
        """Initialize the TransfermarktPlayerRecordValues class."""
        self.URL = self.URL.format(page_number=self.page_number)
        self.page = self.request_url_page()
        self.raise_exception_if_not_found(xpath=Players.RecordValues.FOUND)

    def __parse_search_results(self) -> list:
        """
        Parse and return a list of player search results. Each result includes player information such as their unique
        identifier, name, position, club (including ID and name), age, nationality, and market value.

        Returns:
            list: A list of dictionaries, with each dictionary representing a player search result.
        """

        search_results: list[ElementTree] = self.page.xpath(Players.RecordValues.RESULTS)
        results = []

        for result in search_results:
            rank = trim(result.xpath(Players.RecordValues.RANK))
            idx = extract_from_url(result.xpath(Players.Search.ID))
            name = trim(result.xpath(Players.Search.NAME))
            club_name = trim(result.xpath(Players.RecordValues.CLUB_NAME))
            club_id = safe_regex(result.xpath(Players.RecordValues.CLUB_IMAGE), REGEX_CHART_CLUB_ID, "club_id")
            date_record = trim(result.xpath(Players.RecordValues.DATE_RECORD))
            nationalities = result.xpath(Players.Search.NATIONALITIES)
            market_value = trim(result.xpath(Players.RecordValues.MARKET_VALUE))

            results.append(
                {
                    "rank": rank,
                    "id": idx,
                    "name": name,
                    "club": {
                        "name": club_name,
                        "id": club_id,
                    },
                    "date_record": date_record,
                    "nationalities": nationalities,
                    "marketValue": market_value,
                },
            )

        return results

    def search_players(self) -> dict:
        """
        Retrieve and parse the search results for most valuable players. The results
            include player information such as their name, position, club, age, nationality, and market value.

        Returns:
            dict: A dictionary containing the page number, last page number, search
                results, and the timestamp of when the data was last updated.
        """
        self.response["pageNumber"] = self.page_number
        self.response["lastPageNumber"] = self.get_last_page_number(Players.RecordValues.BASE)
        self.response["results"] = self.__parse_search_results()
        self.response["updatedAt"] = datetime.now()

        return self.response
