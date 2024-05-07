from datetime import datetime


from app.services.players.most_valuable import TransfermarktPlayerMostValuable
import pytest
from schema import And, Schema


def test_players_search_empty(len_greater_than_0):
    tfmkt = TransfermarktPlayerMostValuable()
    result = tfmkt.search_players()

    expected_schema = Schema(
        {
            "pageNumber": 1,
            "lastPageNumber": And(int, lambda x: x > 1),
            "results": And(list, len_greater_than_0),
            "updatedAt": datetime,
        },
    )

    assert expected_schema.validate(result)


@pytest.mark.parametrize("page_number", [(1), (3)])
def test_players_search(page_number, len_greater_than_0, regex_integer, regex_market_value):
    tfmkt = TransfermarktPlayerMostValuable(page_number=page_number)
    result = tfmkt.search_players()

    expected_schema = Schema(
        {
            "pageNumber": page_number,
            "lastPageNumber": And(int, lambda x: x > 1),
            "results": [
                {
                    "rank": And(str, len_greater_than_0, regex_integer),
                    "id": And(str, len_greater_than_0, regex_integer),
                    "name": And(str, len_greater_than_0),
                    "club": {
                        "id": And(str, len_greater_than_0, regex_integer),
                        "name": And(str, len_greater_than_0),
                    },
                    "age": And(str, len_greater_than_0, regex_integer),
                    "nationalities": And(list, len_greater_than_0),
                    "marketValue": And(str, len_greater_than_0, regex_market_value),
                },
            ],
            "updatedAt": datetime,
        },
    )

    assert expected_schema.validate(result)
