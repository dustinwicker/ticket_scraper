# Ticket Scraper

Web scraper that searches multiple ticket resale sites to find and compare concert ticket prices.

## Overview

This project automates the process of finding concert tickets by:

1. Searching Google for ticket listings
2. Scraping multiple ticket resale sites (VividSeats, Ticketmaster, SeatGeek, etc.)
3. Extracting ticket prices, sections, and seat information
4. Compiling results for price comparison

## Features

- **Multi-Site Scraping** - Scrapes VividSeats, Ticketmaster, SeatGeek, and more
- **Google Search Integration** - Starts from Google search to find all ticket sources
- **Price Extraction** - Extracts ticket prices, fees, and total costs
- **Seat Information** - Captures section, row, and seat details
- **Headless Browser** - Runs in background without visible browser window

## Supported Sites

- VividSeats
- Ticketmaster
- SeatGeek
- TicketNetwork
- TicketCity
- And more from Google search results

## Data Collected

| Field | Description |
|-------|-------------|
| Site | Ticket resale website |
| Price | Ticket price |
| Section | Venue section |
| Row | Row number |
| Quantity | Available tickets |
| Event | Concert/event name |
| Date | Event date |

## Setup

### Prerequisites

- Python 3.x
- Chrome browser

### Installation

```bash
pip install pandas selenium
```

## Usage

```python
from selenium import webdriver

# Search for tickets
driver = webdriver.Chrome()
driver.get("https://www.google.com/")
search = driver.find_element_by_name('q')
search.send_keys("lord huron tickets")
search.submit()

# Script then extracts links and scrapes each site
```

## Output

Creates a CSV file with ticket information from all scraped sites:

```
vividseats_ticket_info_take_one.csv
```

## Notes

- Some sites may block automated access (e.g., StubHub)
- Prices and availability change frequently
- Use responsibly and respect site terms of service

## License

MIT
