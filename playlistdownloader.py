import datetime
from typing import List

import bs4
import requests
import pandas as pd


class Playlistdownloader:
    """A class for downloading playlists from the Muziekweb website."""

    @staticmethod
    def create_url(date: datetime.datetime, musicstation: str = "SkyRadio") -> str:
        """Find URL containing the playlist on Muziekweb

        Parameters
        ----------
            date: datetime.datetime
                The date for which to create the URL.
            musicstation (str, optional):
                The name of the music station. Defaults to "SkyRadio".

        Returns:
        --------
            str: The URL for the given date and music station.
        """

        datestr = f"date={date.day}-{date.month}-{date.year}"
        stationstr = f"station={musicstation}"
        base_url = "https://www.muziekweb.nl/Muziekweb/Radio"
        return f"{base_url}/?{stationstr}&{datestr}&RangeStart=1&RangeEnd=500"

    @staticmethod
    def url_to_soup(url: str) -> bs4.BeautifulSoup:
        """Get the HTML from a URL as a BeautifulSoup object.

        Parameters
        ----------
            url (str):
                The URL to convert to a BeautifulSoup object.

        Returns:
            bs4.BeautifulSoup: The BeautifulSoup object for the given URL.
        """

        request = requests.get(url, timeout=10)
        return bs4.BeautifulSoup(request.text, "html5lib")

    @staticmethod
    def find_all_rows(soup: bs4.BeautifulSoup) -> List[bs4.element.Tag]:
        """Finds all rows (songs) from a Muziekweb Beautifulsoup

        Parameters
        ----------
            soup (bs4.BeautifulSoup): The BeautifulSoup object to search.

        Returns
        -------
            list[bs4.element.Tag]:
            A list of BeautifulSoup tags representing the rows in the playlist.
        """

        return soup.find("ul", attrs={"class": "radio-playlist"}).find_all(
            "li", class_=["odd", "even"]
        )

    @staticmethod
    def row_to_dct(ele: bs4.element.Tag) -> dict:
        """Extract relevant details from a row of the playlist to dictionary

        Parameters
        ----------
            ele (bs4.element.Tag):
                The BeautifulSoup tag representing the row in the playlist.

        Returns
        -------
            dict: A dictionary containing the time, title, and artist for the row.
        """
        result = {}
        result["Time"] = ele.find("div", attrs={"class": "col-time"}).text.strip()
        result["Title"] = ele.find(
            "span", class_=["cat-songtitle", "col-songtitle"]
        ).text.strip()
        result["Artist"] = ele.find(
            "div", attrs={"class": "col-performers"}
        ).text.strip()
        return result

    def get_playlist_for_date(self, date: datetime.datetime) -> pd.DataFrame:
        """Gets the playlist for the given date.

        Parameters
        ----------
            date (datetime): The date for which to get the playlist.

        Returns
        -------
            pandas.DataFrame: A Pandas DataFrame containing the playlist for the given date.
        """
        url = self.create_url(date)
        soup = self.url_to_soup(url)
        rows = self.find_all_rows(soup)
        playlist = [self.row_to_dct(row) for row in rows]
        return pd.DataFrame(playlist).assign(Date=date)

    def get_playlist_period(
        self, date_start: datetime.datetime, date_end: datetime.datetime
    ) -> pd.DataFrame:
        """Gets the playlist for the given period.

        Args:
            date_start (datetime): The start of the period for which to get the playlist.
            date_end (datetime): The end of the period for which to get the playlist.

        Returns:
            pandas.DataFrame: A Pandas DataFrame containing the playlist for the given period.
        """

        dfs = [
            self.get_playlist_for_date(d) for d in pd.date_range(date_start, date_end)
        ]
        return pd.concat(dfs, ignore_index=True)
