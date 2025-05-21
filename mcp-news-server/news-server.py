import argparse
from mcp.server.fastmcp import FastMCP
import sys
import requests
from bs4 import BeautifulSoup
import signal


mcp = FastMCP('news-demo')

def signal_handler(sig, frame):
    print("Shutting down Wikipedia Summary Agent...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

@mcp.tool()
def get_latest_news(source: str = "npr") -> str:
    """
    Fetches the latest news headlines from a supported static news source.

    This tool currently supports the following sources:
    - 'npr'     → National Public Radio
    - 'bbc'     → BBC News
    Args:
        source (str): The news source to fetch headlines from. Must be one of:
                    'npr', 'bbc', or 'reuters'. Case-insensitive.

    Returns:
        str: A plain text string with the top 10 headlines from the selected source,
            separated by newlines. If the source is unsupported or an error occurs,
            a corresponding message is returned.

    Example:
        >>> get_latest_news("bbc")
    """
    try:
        source = source.lower()
        headlines = []

        if source == "npr":
            url = "https://www.npr.org/sections/news/"
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            articles = soup.find_all('h2', class_='title')[:10]
            headlines = [a.get_text(strip=True) for a in articles]

        elif source == "bbc":
            url = "https://www.bbc.com/news"
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            articles = soup.select("h2")[:10]
            headlines = [a.get_text(strip=True) for a in articles]
        else:
            return "Unsupported news source."

        return "\n".join([f"- {h}" for h in headlines])

    except Exception as e:
        return f"Error while fetching news: {e}"
    

@mcp.tool()
def get_wikipedia_summary(topic: str) -> str:
    """
    Fetches the first paragraph summary of a given topic from Wikipedia.

    Parameters:
        topic (str): The topic to search for (e.g., "machine learning").

    Returns:
        str: The summary paragraph from the topic's Wikipedia page,
             or an error message if not found.

    Example:
        >>> get_wikipedia_summary("Python (programming language)")
    """
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic.replace(' ', '_')}"
        headers = {'User-Agent': 'WikiSummaryAgent/1.0'}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data.get("extract", "No summary available.")
        elif response.status_code == 404:
            return "Topic not found on Wikipedia."
        else:
            return f"Unexpected response from Wikipedia: {response.status_code}"
    except Exception as e:
        return f"Error fetching summary: {e}"


@mcp.tool()
def get_stock_news(ticker: str) -> str:
    """
    This function scrapes the latest news headlines (up to 5) from the Finviz stock quote page
    and returns them in a human-readable format, each with a timestamp, headline, and URL.

    Parameters:
        ticker (str): The stock ticker symbol (e.g., "AAPL" for Apple Inc.).

    Returns:
        str: A newline-separated string of the latest headlines in the format:
             "Timestamp - Headline (URL)".
             If an error occurs during the scraping process, returns an error message.

    Raises:
        This function handles its own exceptions and returns an error message as a string
        instead of propagating exceptions.

    Example:
        >>> get_stock_news("GOOGL")
    """
    try:
        url = f"https://finviz.com/quote.ashx?t={ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        news_table = soup.find('table', class_='fullview-news-outer')
        rows = news_table.find_all('tr')

        news = []
        for row in rows[:5]:  # Only grab latest 5 headlines
            time_tag = row.td.text.strip()
            headline = row.a.text.strip()
            link = row.a['href']
            news.append(f"{time_tag} - {headline} ({link})")

        return "\n".join(news)

    except Exception as e:
        return f"Error fetching news: {e}"


if __name__ == "__main__":
    # Start the server
    print("🚀Starting server... ")

    # Debug Mode
    #  uv run mcp dev server.py

    # Production Mode
    # uv run server.py --server_type=sse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_type", type=str, default="sse", choices=["sse", "stdio"]
    )

    args = parser.parse_args()
    mcp.run(args.server_type)

