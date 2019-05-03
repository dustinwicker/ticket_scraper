# import matplotlib
# matplotlib.use('QT4Agg')
# import matplotlib.pyplot as plt

from __future__ import print_function
import os
import pandas as pd
import re
from collections import OrderedDict
from itertools import repeat
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from datetime import datetime as dt

# Get webdriver to work in the background (without popping up)
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument("javascript.enabled")

print('libraries and modules loaded in.')

### Set all actions at same time
# Increase maximum width in characters of columns - will put all columns in same line in console readout
pd.set_option('expand_frame_repr', False)
# Be able to read entire value in each column (no longer truncating values)
pd.set_option('display.max_colwidth', -1)
# Increase number of rows printed out in console
pd.options.display.max_rows = 200

# Change to appropriate directory
os.chdir('/Users/dustinwicker/PyCharmProjects/ticketscraper')
print('appropriate directory has been changed to.')

print("Begin process...")

# Define Chrome webdriver
driver = webdriver.Chrome()
# Supply url
driver.get(url="https://www.google.com/")
# Find google search bar by name
search = driver.find_element_by_name('q')
# Value to search
value = "lord huron tickets"
# Send search result
search.send_keys(value)
# Submit search result
search.submit()

# Get URL of search
search_url = driver.current_url
# Return back to original search results
# driver.get(url=search_url)

### Obtain all links ###

### Cycle through ads at top of page

# See urls for current ads
# Append results this empty list
link_urls = []
ad_urls = []
print("Current ads:")
for i in range(0, len(driver.find_elements_by_xpath('//cite[@class="UdQCqe"]'))):
    ad_urls.append(driver.find_elements_by_xpath('//cite[@class="UdQCqe"]')[i].text)
    link_urls.append(driver.find_elements_by_xpath('//cite[@class="UdQCqe"]')[i].text)
    print(str(driver.find_elements_by_xpath('//cite[@class="UdQCqe"]')[i].text))

# Obtain remaining URLs
for i in range(0, len(driver.find_elements_by_xpath('//cite[@class="iUh30"]'))):
    link_urls.append(driver.find_elements_by_xpath('//cite[@class="iUh30"]')[i].text)

for i in range(0, len(driver.find_elements_by_xpath('//cite[@class="iUh30 bc"]'))):
    # Split on '›' - make sure returned text contains it
    if driver.find_elements_by_xpath('//cite[@class="iUh30 bc"]')[i].text.find('›') > 1:
        link_urls.append(driver.find_elements_by_xpath('//cite[@class="iUh30 bc"]')[i].text.split('›')[0].strip())

# Stubhub currently blocked me - need to remove
for index, ad in enumerate(link_urls):
    if 'stubhub' in ad:
        print('stubhub is one of the links. Needs to be removed since I have been blocked.')
        del link_urls[index]
        print('stubhub url has been removed from list.')
# Print out links in readable format
print("Current links as of update:")
for link in link_urls:
    print(link)

### Cycle through links ###
sitename_link_urls = []
for link in link_urls:
    website = re.search('www\.(.*)\.com', link)
    # Example find: www.vividseats.com/, https://www.ticketmaster.com
    if website is not None:
        sitename_link_urls.append(website.group(1))
    # website = re.search('www\.(.*)\.com/', link)
    # if website is not None:
    #     print(website.group(1))

    website = re.search('https://(.*)\.com', link)
    # Example find: https://seatgeek.com
    if website is not None and 'www' not in website.group(1):
        sitename_link_urls.append(website.group(1))

# Make sure sitenames retrieved is same length as the link urls (i.e., we got all of them)
if len(sitename_link_urls) == len(link_urls):
    print("All sitenames have been retrieved. Okay to proceed. Length: " + str(len(sitename_link_urls)))

# Remove duplicates from sitename_link_urls list - preserve order and return list
sitename_link_urls = list(OrderedDict(zip(sitename_link_urls, repeat(None))))
print("Duplicates removed from sitename_link_urls, new length: " + str(len(sitename_link_urls)))
print("Remaining sitenames:\n")
for sitename in sitename_link_urls:
    print(sitename)

#driver.find_elements_by_partial_link_text('lord')[0].text

###################
### Vivid Seats ###
###################
driver.find_element_by_partial_link_text('vividseats').click()

if driver.current_url.find('vividseats.com/') > 1:
    #print("Currently openings: " + ad_urls[0])
    # Use to create column below
    retailer_url = driver.current_url
    retailer = driver.current_url
    retailer = re.search('https://www\.(.*)\.com/c', retailer)
    retailer = retailer.group(1)

# Prints out all concert dates on page (possible multiple pages)
#print(driver.find_elements_by_xpath('//table[@id="productionsTable"]')[0].text)

# Get top concert
event_information = driver.find_elements_by_xpath('//table[@id="productionsTable"]//tr[@class="vdp-event-row odd"]')[0].text.split('\n')

# Get current time
time_of_search = dt.now().strftime("%Y-%m-%d %H:%M")

# Empty list to append results to
event_information_list = []
for index, value in enumerate(event_information):
    # Check in day in information
    if value in ["Mon", "Tue", "Wed", "Thurs", "Fri", "Sat", "Sun"]:
        day_index = index
        if day_index == 0:
            day_of_week = [event_information[0]]
            month_day = [event_information[1]]
            clock_time = [event_information[2]]
            artist = [event_information[3]]
            event = [[event_information[4]][0].split('–')[0].strip()]
            city_state = [[event_information[4]][0].split('–')[1].strip()]
# Create DataFrame
event_information_df = pd.DataFrame(data=[day_of_week, month_day, clock_time, artist, event, city_state]).transpose().\
     rename(columns={0:'day', 1:'date', 2:'time', 3:'artist', 4:'event', 5:'location'})


my_href = driver.find_elements_by_xpath('//table[@id="productionsTable"]//tr[@class="vdp-event-row odd"]')[0].get_attribute(name='data-href')

driver.execute_script("window.open('" + my_href +"');")

# Obtain position of current window handle in window handles list
current_window_handle_index = driver.window_handles.index(driver.current_window_handle)
# Obtain position of newly opened tab
new_window_handle_index = current_window_handle_index + 1
driver.switch_to.window(driver.window_handles[new_window_handle_index])

try:
    wait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="production-wrapper"]//'
                                                                     'aside[@class="vdp-modal "][@id="ticketQuantityModal"][@data-state="opened"]')))
    print("Pop-up has been loaded.")
except NoSuchElementException:
    print("No pop-up appeared")


if driver.find_elements_by_xpath('//div[@class="vdp-modal__container"]//div[@class="vdp-modal__header"]//'
                                 'h5[@class="vdp-type-headline5"]')[0].text == "HOW MANY TICKETS?":
    print("Asking for how many tickets I would like.")
    # Click skip - do not select number of seats wanted
    driver.find_element_by_css_selector("button[class='vdp-button--text modal-dismiss']").click()
    print("Asking for how many tickets pop-up has been clicked off.")
    #print(driver.find_elements_by_xpath('//div[@id="rowContainer"]//ul[@class="ticket-rows"]')[0].text)
    try:
        wait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="production-wrapper"]//'
                                                                         'aside[@class="vdp-modal "][@id="ticketQuantityModal"][@data-state="closed"]')))
        print("Pop-up has been cleared.")
    except TimeoutException:
        print('Time-out error')
else:
    print("No pop-up appeared")
    #print(driver.find_elements_by_xpath('//div[@id="rowContainer"]//ul[@class="ticket-rows"]')[0].text)

# Str of all prices for particular artist/event
vividseats_prices = driver.find_elements_by_xpath('//div[@id="rowContainer"]')[0].text
vividseats_prices = vividseats_prices.split('\nRow')

vividseats_individual_options_info = []
amount_position_index = []
for index, value in enumerate(vividseats_prices):
    if len(vividseats_prices[index].split('\n')) > 1:
        max_index = index
        vividseats_prices_split = vividseats_prices[index].split('\n')
        print(vividseats_prices_split)
        for index, value in enumerate(vividseats_prices_split):
            if '$' in value:
                amount_position_index.extend([index])
                if len(amount_position_index) == max_index:
                    amount_position = index
                    if amount_position == 3:
                        vividseats_individual_options_info.append([vividseats_prices_split[0], vividseats_prices_split[1],
                                     vividseats_prices_split[3]])
                    if amount_position == 1:
                        vividseats_individual_options_info.append([vividseats_prices_split[0], vividseats_prices_split[1].split(' $')[0],
                                     vividseats_prices_split[1].split(' $')[1]])
# Create DataFrame
vividseats_individual_options_info_df = pd.DataFrame(data=vividseats_individual_options_info, columns=['row', 'ticket_info', 'price'])

# Make length same as vividseats_individual_options_info_df
if len(vividseats_individual_options_info_df) > 1:
    vividseats_individual_options_info_df_len = len(vividseats_individual_options_info_df)-1
    event_information_df_expanded = event_information_df.append([event_information_df]*vividseats_individual_options_info_df_len,
                                                            ignore_index=True)
    # Merge DataFrames on index
    vividseats_ticket_info = pd.merge(event_information_df_expanded, vividseats_individual_options_info_df, left_index=True, right_index=True)
else:
    # Merge DataFrames on index
    vividseats_ticket_info = pd.merge(event_information_df_expanded, vividseats_individual_options_info_df, left_index=True, right_index=True)

# Remove $ from price and convert to int
vividseats_ticket_info['price'] = vividseats_ticket_info['price'].astype(str).str.replace('$','').astype(int)

# Add columns - retailer info
vividseats_ticket_info.loc[:,'retailer'] = retailer
# time of search
vividseats_ticket_info.loc[:,'time_of_search'] = time_of_search

### Return back to main vivid seats site that lists all concert dates
# Close window of specific concert/event which has been scraped
driver.close()
driver.switch_to.window(driver.window_handles[0])

# Get second concert
event_information = driver.find_elements_by_xpath('//table[@id="productionsTable"]//tr[@class="vdp-event-row even"]')[0].text.split('\n')

# Get current time
time_of_search = dt.now().strftime("%Y-%m-%d %H:%M")

# Empty list to append results to
event_information_list = []
for index, value in enumerate(event_information):
    # Check in day in information
    if value in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        day_index = index
        if day_index == 0:
            day_of_week = [event_information[0]]
            month_day = [event_information[1]]
            clock_time = [event_information[2]]
            artist = [event_information[3]]
            event = [[event_information[4]][0].split('–')[0].strip()]
            city_state = [[event_information[4]][0].split('–')[1].strip()]
# Create DataFrame
event_information_df = pd.DataFrame(data=[day_of_week, month_day, clock_time, artist, event, city_state]).transpose().\
     rename(columns={0:'day', 1:'date', 2:'time', 3:'artist', 4:'event', 5:'location'})

my_href = driver.find_elements_by_xpath('//table[@id="productionsTable"]//tr[@class="vdp-event-row even"]')[0].get_attribute(name='data-href')

driver.execute_script("window.open('" + my_href +"');")

# Obtain position of current window handle in window handles list
current_window_handle_index = driver.window_handles.index(driver.current_window_handle)
# Obtain position of newly opened tab
new_window_handle_index = current_window_handle_index + 1
driver.switch_to.window(driver.window_handles[new_window_handle_index])

try:
    wait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="production-wrapper"]//'
                                                                     'aside[@class="vdp-modal "][@id="ticketQuantityModal"][@data-state="opened"]')))
    print("Pop-up has been loaded.")
except NoSuchElementException:
    print("No pop-up appeared")


if driver.find_elements_by_xpath('//div[@class="vdp-modal__container"]//div[@class="vdp-modal__header"]//'
                                 'h5[@class="vdp-type-headline5"]')[0].text == "HOW MANY TICKETS?":
    print("Asking for how many tickets I would like.")
    # Click skip - do not select number of seats wanted
    driver.find_element_by_css_selector("button[class='vdp-button--text modal-dismiss']").click()
    print("Asking for how many tickets pop-up has been clicked off.")
    #print(driver.find_elements_by_xpath('//div[@id="rowContainer"]//ul[@class="ticket-rows"]')[0].text)
    try:
        wait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="production-wrapper"]//'
                                                                         'aside[@class="vdp-modal "][@id="ticketQuantityModal"][@data-state="closed"]')))
        print("Pop-up has been cleared.")
    except TimeoutException:
        print('Time-out error')
else:
    print("No pop-up appeared")
    #print(driver.find_elements_by_xpath('//div[@id="rowContainer"]//ul[@class="ticket-rows"]')[0].text)

# Str of all prices for particular artist/event
vividseats_prices = driver.find_elements_by_xpath('//div[@id="rowContainer"]')[0].text
vividseats_prices = vividseats_prices.split('\nRow')

vividseats_individual_options_info = []
amount_position_index = []
for index, value in enumerate(vividseats_prices):
    if len(vividseats_prices[index].split('\n')) > 1:
        max_index = index
        vividseats_prices_split = vividseats_prices[index].split('\n')
        print(vividseats_prices_split)
        for index, value in enumerate(vividseats_prices_split):
            if '$' in value:
                amount_position_index.extend([index])
                if len(amount_position_index) == max_index:
                    amount_position = index
                    if amount_position == 3:
                        vividseats_individual_options_info.append([vividseats_prices_split[0], vividseats_prices_split[1],
                                     vividseats_prices_split[3]])
                    if amount_position == 1:
                        vividseats_individual_options_info.append([vividseats_prices_split[0], vividseats_prices_split[1].split(' $')[0],
                                     vividseats_prices_split[1].split(' $')[1]])
# Create DataFrame
vividseats_individual_options_info_df = pd.DataFrame(data=vividseats_individual_options_info, columns=['row', 'ticket_info', 'price'])

# Make length same as vividseats_individual_options_info_df
if len(vividseats_individual_options_info_df) > 1:
    vividseats_individual_options_info_df_len = len(vividseats_individual_options_info_df)-1
    event_information_df_expanded = event_information_df.append([event_information_df]*vividseats_individual_options_info_df_len,
                                                            ignore_index=True)
    # Merge DataFrames on index
    vividseats_ticket_info = pd.merge(event_information_df_expanded, vividseats_individual_options_info_df, left_index=True, right_index=True)
else:
    # Merge DataFrames on index
    individual_ticket_info = pd.merge(event_information_df, vividseats_individual_options_info_df, left_index=True, right_index=True)

    # Remove $ from price and convert to int
    individual_ticket_info['price'] = individual_ticket_info['price'].astype(str).str.replace('$','').astype(int)
    # Add columns - retailer info
    individual_ticket_info.loc[:,'retailer'] = retailer
    # time of search
    individual_ticket_info.loc[:,'time_of_search'] = time_of_search

    if vividseats_ticket_info is not None:
        print("vividseats_ticket_info exists. Append individual_ticket_info.")
        vividseats_ticket_info = vividseats_ticket_info.append(individual_ticket_info).reset_index(drop=True)

### Return back to main vivid seats site that lists all concert dates
# Close window of specific concert/event which has been scraped
driver.close()
driver.switch_to.window(driver.window_handles[0])


# Get third concert
event_information = driver.find_elements_by_xpath('//table[@id="productionsTable"]//tr[@class="vdp-event-row odd"]')[1].text.split('\n')

# Get current time
time_of_search = dt.now().strftime("%Y-%m-%d %H:%M")

# Empty list to append results to
event_information_list = []
for index, value in enumerate(event_information):
    # Check in day in information
    if value in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        day_index = index
        if day_index == 0:
            day_of_week = [event_information[0]]
            month_day = [event_information[1]]
            clock_time = [event_information[2]]
            artist = [event_information[3]]
            event = [[event_information[4]][0].split('–')[0].strip()]
            city_state = [[event_information[4]][0].split('–')[1].strip()]
# Create DataFrame
event_information_df = pd.DataFrame(data=[day_of_week, month_day, clock_time, artist, event, city_state]).transpose().\
     rename(columns={0:'day', 1:'date', 2:'time', 3:'artist', 4:'event', 5:'location'})

my_href = driver.find_elements_by_xpath('//table[@id="productionsTable"]//tr[@class="vdp-event-row odd"]')[1].get_attribute(name='data-href')

driver.execute_script("window.open('" + my_href +"');")

# Obtain position of current window handle in window handles list
current_window_handle_index = driver.window_handles.index(driver.current_window_handle)
# Obtain position of newly opened tab
new_window_handle_index = current_window_handle_index + 1
driver.switch_to.window(driver.window_handles[new_window_handle_index])

try:
    wait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="production-wrapper"]//'
                                                                     'aside[@class="vdp-modal "][@id="ticketQuantityModal"][@data-state="opened"]')))
    print("Pop-up has been loaded.")
except NoSuchElementException:
    print("No pop-up appeared")


if driver.find_elements_by_xpath('//div[@class="vdp-modal__container"]//div[@class="vdp-modal__header"]//'
                                 'h5[@class="vdp-type-headline5"]')[0].text == "HOW MANY TICKETS?":
    print("Asking for how many tickets I would like.")
    # Click skip - do not select number of seats wanted
    driver.find_element_by_css_selector("button[class='vdp-button--text modal-dismiss']").click()
    print("Asking for how many tickets pop-up has been clicked off.")
    #print(driver.find_elements_by_xpath('//div[@id="rowContainer"]//ul[@class="ticket-rows"]')[0].text)
    try:
        wait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="production-wrapper"]//'
                                                                         'aside[@class="vdp-modal "][@id="ticketQuantityModal"][@data-state="closed"]')))
        print("Pop-up has been cleared.")
    except TimeoutException:
        print('Time-out error')
else:
    print("No pop-up appeared")
    #print(driver.find_elements_by_xpath('//div[@id="rowContainer"]//ul[@class="ticket-rows"]')[0].text)

# Str of all prices for particular artist/event
vividseats_prices = driver.find_elements_by_xpath('//div[@id="rowContainer"]')[0].text
vividseats_prices = vividseats_prices.split('\nRow')

if "No results" in vividseats_prices[0]:
    print("No tickets available for particular event.")
    vividseats_individual_options_info_df = pd.DataFrame(data=[["NA"] * 3], columns=['row', 'ticket_info', 'price'])
    #individual_ticket_info = event_information_df['artist'].values[0].lower().replace(" ", "_") + "_" + event_information_df['location'].values[0].lower().replace(", ", "_") + "_ticket_info"

    individual_ticket_info = pd.merge(event_information_df, vividseats_individual_options_info_df, left_index=True, right_index=True)

    # Add columns - retailer info
    individual_ticket_info.loc[:, 'retailer'] = retailer
    # time of search
    individual_ticket_info.loc[:, 'time_of_search'] = time_of_search
else:
    vividseats_individual_options_info = []
    amount_position_index = []
    for index, value in enumerate(vividseats_prices):
        if len(vividseats_prices[index].split('\n')) > 1:
            max_index = index
            vividseats_prices_split = vividseats_prices[index].split('\n')
            print(vividseats_prices_split)
            for index, value in enumerate(vividseats_prices_split):
                if '$' in value:
                    amount_position_index.extend([index])
                    if len(amount_position_index) == max_index:
                        amount_position = index
                        if amount_position == 3:
                            vividseats_individual_options_info.append([vividseats_prices_split[0], vividseats_prices_split[1],
                                         vividseats_prices_split[3]])
                        if amount_position == 1:
                            vividseats_individual_options_info.append([vividseats_prices_split[0], vividseats_prices_split[1].split(' $')[0],
                                         vividseats_prices_split[1].split(' $')[1]])
    # Create DataFrame
    vividseats_individual_options_info_df = pd.DataFrame(data=vividseats_individual_options_info, columns=['row', 'ticket_info', 'price'])

    # Make length same as vividseats_individual_options_info_df
    if len(vividseats_individual_options_info_df) > 1:
        vividseats_individual_options_info_df_len = len(vividseats_individual_options_info_df)-1
        event_information_df_expanded = event_information_df.append([event_information_df]*vividseats_individual_options_info_df_len,
                                                                ignore_index=True)
        # Merge DataFrames on index
        vividseats_ticket_info = pd.merge(event_information_df_expanded, vividseats_individual_options_info_df, left_index=True, right_index=True)
    else:
        print("One ticket option is available.")
        # Merge DataFrames on index
        individual_ticket_info = pd.merge(event_information_df, vividseats_individual_options_info_df, left_index=True, right_index=True)

        # Remove $ from price and convert to int
        individual_ticket_info['price'] = individual_ticket_info['price'].astype(str).str.replace('$','').astype(int)
        # Add columns - retailer info
        individual_ticket_info.loc[:,'retailer'] = retailer
        # time of search
        individual_ticket_info.loc[:,'time_of_search'] = time_of_search

        if vividseats_ticket_info is not None:
            print("vividseats_ticket_info exists. Append individual_ticket_info.")
            vividseats_ticket_info = vividseats_ticket_info.append(individual_ticket_info).reset_index(drop=True)
            print("New length of vividseats_ticket_info after appending is: " + str(len(vividseats_ticket_info))+ "." + "\n")
            print("The contents of vividseats_ticket_info are below:")
            print(vividseats_ticket_info)

# # Remove $ from price and convert to int
# vividseats_ticket_info['price'] = vividseats_ticket_info['price'].astype(str).str.replace('$','').astype(int)
#
# # Add columns - retailer info
# vividseats_ticket_info.loc[:,'retailer'] = retailer
# # time of search
# vividseats_ticket_info.loc[:,'time_of_search'] = time_of_search

### Return back to main vivid seats site that lists all concert dates
# Close window of specific concert/event which has been scraped
driver.close()
driver.switch_to.window(driver.window_handles[0])


# Get fourth concert
event_information = driver.find_elements_by_xpath('//table[@id="productionsTable"]//tr[@class="vdp-event-row even"]')[1].text.split('\n')

# Get current time
time_of_search = dt.now().strftime("%Y-%m-%d %H:%M")

# Empty list to append results to
event_information_list = []
for index, value in enumerate(event_information):
    # Check in day in information
    if value in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        day_index = index
        if day_index == 0:
            day_of_week = [event_information[0]]
            month_day = [event_information[1]]
            clock_time = [event_information[2]]
            artist = [event_information[3]]
            event = [[event_information[4]][0].split('–')[0].strip()]
            city_state = [[event_information[4]][0].split('–')[1].strip()]
# Create DataFrame
event_information_df = pd.DataFrame(data=[day_of_week, month_day, clock_time, artist, event, city_state]).transpose().\
     rename(columns={0:'day', 1:'date', 2:'time', 3:'artist', 4:'event', 5:'location'})

my_href = driver.find_elements_by_xpath('//table[@id="productionsTable"]//tr[@class="vdp-event-row even"]')[1].get_attribute(name='data-href')

driver.execute_script("window.open('" + my_href +"');")

# Obtain position of current window handle in window handles list
current_window_handle_index = driver.window_handles.index(driver.current_window_handle)
# Obtain position of newly opened tab
new_window_handle_index = current_window_handle_index + 1
driver.switch_to.window(driver.window_handles[new_window_handle_index])

try:
    wait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="production-wrapper"]//'
                                                                     'aside[@class="vdp-modal "][@id="ticketQuantityModal"][@data-state="opened"]')))
    print("Pop-up has been loaded.")
except NoSuchElementException:
    print("No pop-up appeared")


if driver.find_elements_by_xpath('//div[@class="vdp-modal__container"]//div[@class="vdp-modal__header"]//'
                                 'h5[@class="vdp-type-headline5"]')[0].text == "HOW MANY TICKETS?":
    print("Asking for how many tickets I would like.")
    # Click skip - do not select number of seats wanted
    driver.find_element_by_css_selector("button[class='vdp-button--text modal-dismiss']").click()
    print("Asking for how many tickets pop-up has been clicked off.")
    #print(driver.find_elements_by_xpath('//div[@id="rowContainer"]//ul[@class="ticket-rows"]')[0].text)
    try:
        wait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="production-wrapper"]//'
                                                                         'aside[@class="vdp-modal "][@id="ticketQuantityModal"][@data-state="closed"]')))
        print("Pop-up has been cleared.")
    except TimeoutException:
        print('Time-out error')
else:
    print("No pop-up appeared")
    #print(driver.find_elements_by_xpath('//div[@id="rowContainer"]//ul[@class="ticket-rows"]')[0].text)

# Str of all prices for particular artist/event
vividseats_prices = driver.find_elements_by_xpath('//div[@id="rowContainer"]')[0].text
vividseats_prices = vividseats_prices.split('\nRow')

if "No results" in vividseats_prices[0]:
    print("No tickets available for particular event.")
    vividseats_individual_options_info_df = pd.DataFrame(data=[["NA"] * 3], columns=['row', 'ticket_info', 'price'])
    #individual_ticket_info = event_information_df['artist'].values[0].lower().replace(" ", "_") + "_" + event_information_df['location'].values[0].lower().replace(", ", "_") + "_ticket_info"

    individual_ticket_info = pd.merge(event_information_df, vividseats_individual_options_info_df, left_index=True, right_index=True)

    # Add columns - retailer info
    individual_ticket_info.loc[:, 'retailer'] = retailer
    # time of search
    individual_ticket_info.loc[:, 'time_of_search'] = time_of_search
else:
    print("Tickets are available for particular event.")
    vividseats_individual_options_info = []
    amount_position_index = []
    for index, value in enumerate(vividseats_prices):
        if len(vividseats_prices[index].split('\n')) > 1:
            max_index = index
            vividseats_prices_split = vividseats_prices[index].split('\n')
            print(vividseats_prices_split)
            for index, value in enumerate(vividseats_prices_split):
                if '$' in value:
                    amount_position_index.extend([index])
                    if len(amount_position_index) == max_index:
                        amount_position = index
                        if amount_position == 3:
                            vividseats_individual_options_info.append([vividseats_prices_split[0], vividseats_prices_split[1],
                                         vividseats_prices_split[3]])
                        if amount_position == 1:
                            vividseats_individual_options_info.append([vividseats_prices_split[0], vividseats_prices_split[1].split(' $')[0],
                                         vividseats_prices_split[1].split(' $')[1]])
    # Create DataFrame
    vividseats_individual_options_info_df = pd.DataFrame(data=vividseats_individual_options_info, columns=['row', 'ticket_info', 'price'])

    # Make length same as vividseats_individual_options_info_df
    if len(vividseats_individual_options_info_df) > 1:
        print(str(len(vividseats_individual_options_info_df)) + " ticket options are available.")
        vividseats_individual_options_info_df_len = len(vividseats_individual_options_info_df)-1
        event_information_df_expanded = event_information_df.append([event_information_df]*vividseats_individual_options_info_df_len,
                                                                ignore_index=True)
        # Merge DataFrames on index
        individual_ticket_info = pd.merge(event_information_df_expanded, vividseats_individual_options_info_df, left_index=True, right_index=True)

        # Remove $ from price and convert to int
        individual_ticket_info['price'] = individual_ticket_info['price'].astype(str).str.replace('$', '').astype(int)
        # Add columns - retailer info
        individual_ticket_info.loc[:, 'retailer'] = retailer
        # time of search
        individual_ticket_info.loc[:, 'time_of_search'] = time_of_search
    else:
        print("One ticket option is available.")
        # Merge DataFrames on index
        individual_ticket_info = pd.merge(event_information_df, vividseats_individual_options_info_df, left_index=True, right_index=True)

        # Remove $ from price and convert to int
        individual_ticket_info['price'] = individual_ticket_info['price'].astype(str).str.replace('$','').astype(int)
        # Add columns - retailer info
        individual_ticket_info.loc[:,'retailer'] = retailer
        # time of search
        individual_ticket_info.loc[:,'time_of_search'] = time_of_search

if vividseats_ticket_info is not None:
    print("vividseats_ticket_info exists. Append individual_ticket_info.")
    vividseats_ticket_info = vividseats_ticket_info.append(individual_ticket_info).reset_index(drop=True)
    print("New length of vividseats_ticket_info after appending is: " + str(len(vividseats_ticket_info))+ "." + "\n")
    print("The contents of vividseats_ticket_info are below:")
    print(vividseats_ticket_info)
else:
    vividseats_ticket_info = individual_ticket_info
    print("vividseats_ticket_info has been created.")

### Return back to main vivid seats site that lists all concert dates
# Close window of specific concert/event which has been scraped
driver.close()
driver.switch_to.window(driver.window_handles[0])




# Get fifth concert
event_information = driver.find_elements_by_xpath('//table[@id="productionsTable"]//tr[@class="vdp-event-row odd"]')[2].text.split('\n')

# Get current time
time_of_search = dt.now().strftime("%Y-%m-%d %H:%M")

# Empty list to append results to
event_information_list = []
for index, value in enumerate(event_information):
    # Check in day in information
    if value in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        day_index = index
        if day_index == 0:
            day_of_week = [event_information[0]]
            month_day = [event_information[1]]
            clock_time = [event_information[2]]
            artist = [event_information[3]]
            event = [[event_information[4]][0].split('–')[0].strip()]
            city_state = [[event_information[4]][0].split('–')[1].strip()]
# Create DataFrame
event_information_df = pd.DataFrame(data=[day_of_week, month_day, clock_time, artist, event, city_state]).transpose().\
     rename(columns={0:'day', 1:'date', 2:'time', 3:'artist', 4:'event', 5:'location'})

my_href = driver.find_elements_by_xpath('//table[@id="productionsTable"]//tr[@class="vdp-event-row odd"]')[2].get_attribute(name='data-href')

driver.execute_script("window.open('" + my_href +"');")

# Obtain position of current window handle in window handles list
current_window_handle_index = driver.window_handles.index(driver.current_window_handle)
# Obtain position of newly opened tab
new_window_handle_index = current_window_handle_index + 1
driver.switch_to.window(driver.window_handles[new_window_handle_index])

try:
    wait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="production-wrapper"]//'
                                                                     'aside[@class="vdp-modal "][@id="ticketQuantityModal"][@data-state="opened"]')))
    print("Pop-up has been loaded.")
except NoSuchElementException:
    print("No pop-up appeared")


if driver.find_elements_by_xpath('//div[@class="vdp-modal__container"]//div[@class="vdp-modal__header"]//'
                                 'h5[@class="vdp-type-headline5"]')[0].text == "HOW MANY TICKETS?":
    print("Asking for how many tickets I would like.")
    # Click skip - do not select number of seats wanted
    driver.find_element_by_css_selector("button[class='vdp-button--text modal-dismiss']").click()
    print("Asking for how many tickets pop-up has been clicked off.")
    #print(driver.find_elements_by_xpath('//div[@id="rowContainer"]//ul[@class="ticket-rows"]')[0].text)
    try:
        wait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="production-wrapper"]//'
                                                                         'aside[@class="vdp-modal "][@id="ticketQuantityModal"][@data-state="closed"]')))
        print("Pop-up has been cleared.")
    except TimeoutException:
        print('Time-out error')
else:
    print("No pop-up appeared")
    #print(driver.find_elements_by_xpath('//div[@id="rowContainer"]//ul[@class="ticket-rows"]')[0].text)

# Str of all prices for particular artist/event
vividseats_prices = driver.find_elements_by_xpath('//div[@id="rowContainer"]')[0].text
vividseats_prices = vividseats_prices.split('\nRow')

if "No results" in vividseats_prices[0]:
    print("No tickets available for particular event.")
    vividseats_individual_options_info_df = pd.DataFrame(data=[["NA"] * 3], columns=['row', 'ticket_info', 'price'])
    #individual_ticket_info = event_information_df['artist'].values[0].lower().replace(" ", "_") + "_" + event_information_df['location'].values[0].lower().replace(", ", "_") + "_ticket_info"

    individual_ticket_info = pd.merge(event_information_df, vividseats_individual_options_info_df, left_index=True, right_index=True)

    # Add columns - retailer info
    individual_ticket_info.loc[:, 'retailer'] = retailer
    # time of search
    individual_ticket_info.loc[:, 'time_of_search'] = time_of_search
else:
    print("Tickets are available for particular event.")
    vividseats_individual_options_info = []
    amount_position_index = []
    for index, value in enumerate(vividseats_prices):
        if len(vividseats_prices[index].split('\n')) > 1:
            max_index = index
            vividseats_prices_split = vividseats_prices[index].split('\n')
            print(vividseats_prices_split)
            for index, value in enumerate(vividseats_prices_split):
                if '$' in value:
                    amount_position_index.extend([index])
                    if len(amount_position_index) == max_index:
                        amount_position = index
                        if amount_position == 3:
                            vividseats_individual_options_info.append([vividseats_prices_split[0], vividseats_prices_split[1],
                                         vividseats_prices_split[3]])
                        if amount_position == 1:
                            vividseats_individual_options_info.append([vividseats_prices_split[0], vividseats_prices_split[1].split(' $')[0],
                                         vividseats_prices_split[1].split(' $')[1]])
    # Create DataFrame
    vividseats_individual_options_info_df = pd.DataFrame(data=vividseats_individual_options_info, columns=['row', 'ticket_info', 'price'])

    # Make length same as vividseats_individual_options_info_df
    if len(vividseats_individual_options_info_df) > 1:
        print(str(len(vividseats_individual_options_info_df)) + " ticket options are available.")
        vividseats_individual_options_info_df_len = len(vividseats_individual_options_info_df)-1
        event_information_df_expanded = event_information_df.append([event_information_df]*vividseats_individual_options_info_df_len,
                                                                ignore_index=True)
        # Merge DataFrames on index
        individual_ticket_info = pd.merge(event_information_df_expanded, vividseats_individual_options_info_df, left_index=True, right_index=True)

        # Remove $ from price and convert to int
        individual_ticket_info['price'] = individual_ticket_info['price'].astype(str).str.replace('$', '').astype(int)
        # Add columns - retailer info
        individual_ticket_info.loc[:, 'retailer'] = retailer
        # time of search
        individual_ticket_info.loc[:, 'time_of_search'] = time_of_search
    else:
        print("One ticket option is available.")
        # Merge DataFrames on index
        individual_ticket_info = pd.merge(event_information_df, vividseats_individual_options_info_df, left_index=True, right_index=True)

        # Remove $ from price and convert to int
        individual_ticket_info['price'] = individual_ticket_info['price'].astype(str).str.replace('$','').astype(int)
        # Add columns - retailer info
        individual_ticket_info.loc[:,'retailer'] = retailer
        # time of search
        individual_ticket_info.loc[:,'time_of_search'] = time_of_search

if vividseats_ticket_info is not None:
    print("vividseats_ticket_info exists. Append individual_ticket_info.")
    vividseats_ticket_info = vividseats_ticket_info.append(individual_ticket_info).reset_index(drop=True)
    print("New length of vividseats_ticket_info after appending is: " + str(len(vividseats_ticket_info))+ "." + "\n")
    print("The contents of vividseats_ticket_info are below:")
    print(vividseats_ticket_info)
else:
    vividseats_ticket_info = individual_ticket_info
    print("vividseats_ticket_info has been created.")

### Return back to main vivid seats site that lists all concert dates
# Close window of specific concert/event which has been scraped
driver.close()
driver.switch_to.window(driver.window_handles[0])



# Get sixth concert
event_information = driver.find_elements_by_xpath('//table[@id="productionsTable"]//tr[@class="vdp-event-row even"]')[2].text.split('\n')

# Get current time
time_of_search = dt.now().strftime("%Y-%m-%d %H:%M")

# Empty list to append results to
event_information_list = []
for index, value in enumerate(event_information):
    # Check in day in information
    if value in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        day_index = index
        if day_index == 0:
            day_of_week = [event_information[0]]
            month_day = [event_information[1]]
            clock_time = [event_information[2]]
            artist = [event_information[3]]
            event = [[event_information[4]][0].split('–')[0].strip()]
            city_state = [[event_information[4]][0].split('–')[1].strip()]
# Create DataFrame
event_information_df = pd.DataFrame(data=[day_of_week, month_day, clock_time, artist, event, city_state]).transpose().\
     rename(columns={0:'day', 1:'date', 2:'time', 3:'artist', 4:'event', 5:'location'})

my_href = driver.find_elements_by_xpath('//table[@id="productionsTable"]//tr[@class="vdp-event-row even"]')[2].get_attribute(name='data-href')

driver.execute_script("window.open('" + my_href +"');")

# Obtain position of current window handle in window handles list
current_window_handle_index = driver.window_handles.index(driver.current_window_handle)
# Obtain position of newly opened tab
new_window_handle_index = current_window_handle_index + 1
driver.switch_to.window(driver.window_handles[new_window_handle_index])

try:
    wait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="production-wrapper"]//'
                                                                     'aside[@class="vdp-modal "][@id="ticketQuantityModal"][@data-state="opened"]')))
    print("Pop-up has been loaded.")
except NoSuchElementException:
    print("No pop-up appeared")


if driver.find_elements_by_xpath('//div[@class="vdp-modal__container"]//div[@class="vdp-modal__header"]//'
                                 'h5[@class="vdp-type-headline5"]')[0].text == "HOW MANY TICKETS?":
    print("Asking for how many tickets I would like.")
    # Click skip - do not select number of seats wanted
    driver.find_element_by_css_selector("button[class='vdp-button--text modal-dismiss']").click()
    print("Asking for how many tickets pop-up has been clicked off.")
    #print(driver.find_elements_by_xpath('//div[@id="rowContainer"]//ul[@class="ticket-rows"]')[0].text)
    try:
        wait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="production-wrapper"]//'
                                                                         'aside[@class="vdp-modal "][@id="ticketQuantityModal"][@data-state="closed"]')))
        print("Pop-up has been cleared.")
    except TimeoutException:
        print('Time-out error')
else:
    print("No pop-up appeared")
    #print(driver.find_elements_by_xpath('//div[@id="rowContainer"]//ul[@class="ticket-rows"]')[0].text)

# Str of all prices for particular artist/event
vividseats_prices = driver.find_elements_by_xpath('//div[@id="rowContainer"]')[0].text
vividseats_prices = vividseats_prices.split('\nRow')

if "No results" in vividseats_prices[0]:
    print("No tickets available for particular event.")
    vividseats_individual_options_info_df = pd.DataFrame(data=[["NA"] * 3], columns=['row', 'ticket_info', 'price'])
    #individual_ticket_info = event_information_df['artist'].values[0].lower().replace(" ", "_") + "_" + event_information_df['location'].values[0].lower().replace(", ", "_") + "_ticket_info"

    individual_ticket_info = pd.merge(event_information_df, vividseats_individual_options_info_df, left_index=True, right_index=True)

    # Add columns - retailer info
    individual_ticket_info.loc[:, 'retailer'] = retailer
    # time of search
    individual_ticket_info.loc[:, 'time_of_search'] = time_of_search
else:
    print("Tickets are available for particular event.")
    vividseats_individual_options_info = []
    amount_position_index = []
    for index, value in enumerate(vividseats_prices):
        if len(vividseats_prices[index].split('\n')) > 1:
            max_index = index
            vividseats_prices_split = vividseats_prices[index].split('\n')
            print(vividseats_prices_split)
            for index, value in enumerate(vividseats_prices_split):
                if '$' in value:
                    amount_position_index.extend([index])
                    if len(amount_position_index) == max_index:
                        amount_position = index
                        if amount_position == 3:
                            vividseats_individual_options_info.append([vividseats_prices_split[0], vividseats_prices_split[1],
                                         vividseats_prices_split[3]])
                        if amount_position == 1:
                            vividseats_individual_options_info.append([vividseats_prices_split[0], vividseats_prices_split[1].split(' $')[0],
                                         vividseats_prices_split[1].split(' $')[1]])
    # Create DataFrame
    vividseats_individual_options_info_df = pd.DataFrame(data=vividseats_individual_options_info, columns=['row', 'ticket_info', 'price'])

    # Make length same as vividseats_individual_options_info_df
    if len(vividseats_individual_options_info_df) > 1:
        print(str(len(vividseats_individual_options_info_df)) + " ticket options are available.")
        vividseats_individual_options_info_df_len = len(vividseats_individual_options_info_df)-1
        event_information_df_expanded = event_information_df.append([event_information_df]*vividseats_individual_options_info_df_len,
                                                                ignore_index=True)
        # Merge DataFrames on index
        individual_ticket_info = pd.merge(event_information_df_expanded, vividseats_individual_options_info_df, left_index=True, right_index=True)

        # Remove $ from price and convert to int
        individual_ticket_info['price'] = individual_ticket_info['price'].astype(str).str.replace('$', '').astype(int)
        # Add columns - retailer info
        individual_ticket_info.loc[:, 'retailer'] = retailer
        # time of search
        individual_ticket_info.loc[:, 'time_of_search'] = time_of_search
    else:
        print("One ticket option is available.")
        # Merge DataFrames on index
        individual_ticket_info = pd.merge(event_information_df, vividseats_individual_options_info_df, left_index=True, right_index=True)

        # Remove $ from price and convert to int
        individual_ticket_info['price'] = individual_ticket_info['price'].astype(str).str.replace('$','').astype(int)
        # Add columns - retailer info
        individual_ticket_info.loc[:,'retailer'] = retailer
        # time of search
        individual_ticket_info.loc[:,'time_of_search'] = time_of_search

if vividseats_ticket_info is not None:
    print("vividseats_ticket_info exists. Append individual_ticket_info.")
    vividseats_ticket_info = vividseats_ticket_info.append(individual_ticket_info).reset_index(drop=True)
    print("New length of vividseats_ticket_info after appending is: " + str(len(vividseats_ticket_info))+ "." + "\n")
    print("The contents of vividseats_ticket_info are below:")
    print(vividseats_ticket_info)
else:
    vividseats_ticket_info = individual_ticket_info
    print("vividseats_ticket_info has been created.")

### Return back to main vivid seats site that lists all concert dates
# Close window of specific concert/event which has been scraped
driver.close()
driver.switch_to.window(driver.window_handles[0])



# Get seventh concert - works
event_information = driver.find_elements_by_xpath('//table[@id="productionsTable"]//tr[@class="vdp-event-row odd"]')[3].text.split('\n')

# Get current time
time_of_search = dt.now().strftime("%Y-%m-%d %H:%M")

# Empty list to append results to
event_information_list = []
for index, value in enumerate(event_information):
    # Check in day in information
    if value in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        day_index = index
        if day_index == 0:
            day_of_week = [event_information[0]]
            month_day = [event_information[1]]
            clock_time = [event_information[2]]
            artist = [event_information[3]]
            event = [[event_information[4]][0].split('–')[0].strip()]
            city_state = [[event_information[4]][0].split('–')[1].strip()]
# Create DataFrame
event_information_df = pd.DataFrame(data=[day_of_week, month_day, clock_time, artist, event, city_state]).transpose().\
     rename(columns={0:'day', 1:'date', 2:'time', 3:'artist', 4:'event', 5:'location'})

my_href = driver.find_elements_by_xpath('//table[@id="productionsTable"]//tr[@class="vdp-event-row odd"]')[3].get_attribute(name='data-href')

driver.execute_script("window.open('" + my_href +"');")

# Obtain position of current window handle in window handles list
current_window_handle_index = driver.window_handles.index(driver.current_window_handle)
# Obtain position of newly opened tab
new_window_handle_index = current_window_handle_index + 1
driver.switch_to.window(driver.window_handles[new_window_handle_index])

try:
    wait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="production-wrapper"]//'
                                                                     'aside[@class="vdp-modal "][@id="ticketQuantityModal"][@data-state="opened"]')))
    print("Pop-up has been loaded.")
except NoSuchElementException:
    print("No pop-up appeared")


if driver.find_elements_by_xpath('//div[@class="vdp-modal__container"]//div[@class="vdp-modal__header"]//'
                                 'h5[@class="vdp-type-headline5"]')[0].text == "HOW MANY TICKETS?":
    print("Asking for how many tickets I would like.")
    # Click skip - do not select number of seats wanted
    driver.find_element_by_css_selector("button[class='vdp-button--text modal-dismiss']").click()
    print("Asking for how many tickets pop-up has been clicked off.")
    #print(driver.find_elements_by_xpath('//div[@id="rowContainer"]//ul[@class="ticket-rows"]')[0].text)
    try:
        wait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="production-wrapper"]//'
                                                                         'aside[@class="vdp-modal "][@id="ticketQuantityModal"][@data-state="closed"]')))
        print("Pop-up has been cleared.")
    except TimeoutException:
        print('Time-out error')
else:
    print("No pop-up appeared")
    #print(driver.find_elements_by_xpath('//div[@id="rowContainer"]//ul[@class="ticket-rows"]')[0].text)

# Str of all prices for particular artist/event
vividseats_prices = driver.find_elements_by_xpath('//div[@id="rowContainer"]')[0].text
vividseats_prices = vividseats_prices.split('\nRow')

if "No results" in vividseats_prices[0]:
    print("No tickets available for particular event.")
    vividseats_individual_options_info_df = pd.DataFrame(data=[["NA"] * 3], columns=['row', 'ticket_info', 'price'])
    #individual_ticket_info = event_information_df['artist'].values[0].lower().replace(" ", "_") + "_" + event_information_df['location'].values[0].lower().replace(", ", "_") + "_ticket_info"

    individual_ticket_info = pd.merge(event_information_df, vividseats_individual_options_info_df, left_index=True, right_index=True)

    # Add columns - retailer info
    individual_ticket_info.loc[:, 'retailer'] = retailer
    # time of search
    individual_ticket_info.loc[:, 'time_of_search'] = time_of_search
else:
    print("Tickets are available for particular event.")
    vividseats_individual_options_info = []
    amount_position_index = []
    for index, value in enumerate(vividseats_prices):
        if len(vividseats_prices[index].split('\n')) > 1:
            max_index = index
            vividseats_prices_split = vividseats_prices[index].split('\n')
            print(vividseats_prices_split)
            for index, value in enumerate(vividseats_prices_split):
                if '$' in value:
                    amount_position_index.extend([index])
                    if len(amount_position_index) == max_index:
                        amount_position = index
                        if amount_position == 3:
                            vividseats_individual_options_info.append([vividseats_prices_split[0], vividseats_prices_split[1],
                                         vividseats_prices_split[3]])
                        if amount_position == 1:
                            vividseats_individual_options_info.append([vividseats_prices_split[0], vividseats_prices_split[1].split(' $')[0],
                                         vividseats_prices_split[1].split(' $')[1]])
    # Create DataFrame
    vividseats_individual_options_info_df = pd.DataFrame(data=vividseats_individual_options_info, columns=['row', 'ticket_info', 'price'])

    # Make length same as vividseats_individual_options_info_df
    if len(vividseats_individual_options_info_df) > 1:
        print(str(len(vividseats_individual_options_info_df)) + " ticket options are available.")
        vividseats_individual_options_info_df_len = len(vividseats_individual_options_info_df)-1
        event_information_df_expanded = event_information_df.append([event_information_df]*vividseats_individual_options_info_df_len,
                                                                ignore_index=True)
        # Merge DataFrames on index
        individual_ticket_info = pd.merge(event_information_df_expanded, vividseats_individual_options_info_df, left_index=True, right_index=True)

        # Remove $ from price and convert to int
        individual_ticket_info['price'] = individual_ticket_info['price'].astype(str).str.replace('$', '').astype(int)
        # Add columns - retailer info
        individual_ticket_info.loc[:, 'retailer'] = retailer
        # time of search
        individual_ticket_info.loc[:, 'time_of_search'] = time_of_search
    else:
        print("One ticket option is available.")
        # Merge DataFrames on index
        individual_ticket_info = pd.merge(event_information_df, vividseats_individual_options_info_df, left_index=True, right_index=True)

        # Remove $ from price and convert to int
        individual_ticket_info['price'] = individual_ticket_info['price'].astype(str).str.replace('$','').astype(int)
        # Add columns - retailer info
        individual_ticket_info.loc[:,'retailer'] = retailer
        # time of search
        individual_ticket_info.loc[:,'time_of_search'] = time_of_search

if vividseats_ticket_info is not None:
    print("vividseats_ticket_info exists. Append individual_ticket_info.")
    vividseats_ticket_info = vividseats_ticket_info.append(individual_ticket_info).reset_index(drop=True)
    print("New length of vividseats_ticket_info after appending is: " + str(len(vividseats_ticket_info))+ "." + "\n")
    print("The contents of vividseats_ticket_info are below:")
    print(vividseats_ticket_info)
else:
    vividseats_ticket_info = individual_ticket_info
    print("vividseats_ticket_info has been created.")

### Return back to main vivid seats site that lists all concert dates
# Close window of specific concert/event which has been scraped
driver.close()
driver.switch_to.window(driver.window_handles[0])






# Save to csv
vividseats_ticket_info.to_csv("vividseats_ticket_info_take_one.csv", sep=',', mode='a', index=False)




















### Viagogo
# Find link
driver.find_element_by_partial_link_text('viagogo').click()

if driver.current_url.find('viagogo.com/') > 1:
    print("Currently openings: " + ad_urls[0])

print(driver.find_elements_by_xpath('//div[@class="gRow"]//div[@class="gCol12 click "]//div[@id="grid_Local_container"]//'
                                    'div[@id="grid_Local"]//div[@class="w100 p0 el-table mbl"]')[0].text)

print(driver.find_elements_by_xpath('//div[@class="gRow"]//div[@class="gCol12 click "]//div[@id="grid_Local_container"]//'
                                    'div[@id="grid_Local"]//div[@class="w100 p0 el-table mbl"]//'
                                    'div[@class="      el-row-div    "]')[0].text)

my_href = driver.find_elements_by_xpath('//div[@class="gRow"]//div[@class="gCol12 click "]//div[@id="grid_Local_container"]//'
                                    'div[@id="grid_Local"]//div[@class="w100 p0 el-table mbl"]//'
                                    'div[@class="      el-row-div    "]//div[@class="w20 nowrap uum ins last-col "]//'
                                    'div[@class="txtr"]//a')[0].get_attribute(name='href')
print("Currently openings: " + ad_urls[0])
driver.execute_script("window.open('" + my_href +"');")

# Obtain position of current window handle in window handles list
current_window_handle_index = driver.window_handles.index(driver.current_window_handle)
# Obtain position of newly opened tab
new_window_handle_index = current_window_handle_index + 1
driver.switch_to.window(driver.window_handles[new_window_handle_index])



### Scrape specific sites ###


### AmphitheatreMorrison
if driver.current_url.find('amphitheatremorrison.com/') > 1:
    print("Currently openings: " + ad_urls[0])


### BoxOfficeTickets
# driver.find_elements_by_xpath('//tr[@role="row"]//th[@class="eventHeader sorting_disabled"]')[0].text
if driver.current_url.find('boxofficeticket.center/') > 1:
    print("Currently openings: " + ad_urls[0])
    print(driver.find_elements_by_xpath('//table[@class="eventsTbl dataTable no-footer"]')[0].text)
    driver.find_elements_by_xpath('//table[@class="eventsTbl dataTable no-footer"]//th[@class="eventHeader sorting_disabled"]//'
                                  'ul[@class="quantity-selectors"]//li[@class="quantity-selector md-radio"]//'
                                  'input[@type="radio"][@value="1"]')
    print(driver.find_elements_by_xpath(
        '//table[@class="eventsTbl dataTable no-footer"]//tbody//a[@class="eventInfoContainer"]')[0].text)
    print(driver.find_elements_by_xpath(
        '//table[@class="eventsTbl dataTable no-footer"]//tbody//a[@class="eventInfoContainer"]')[0].get_attribute(name='href'))
    print("Currently openings: " + ad_urls[0])
    driver.execute_script("window.open('" + my_href + "');")

    my_href = driver.find_elements_by_xpath('//table[@class="eventsTbl dataTable no-footer"]//'
                              'tbody//tr[@role="row"][@class="odd"]//'
                              'a[@class="btn btn-default buy-btn"]')[0].get_attribute(name='href')
    driver.execute_script("window.open('" + my_href +"');")

    if driver.find_elements_by_xpath('//div[@class="modal-content"]//div[@class="modal-header"]//'
                                     'h4[@class="modal-title"]')[0].text == "TICKETS SELLING OUT":
        print("Tickets selling out pop-up appears.")
        driver.find_elements_by_xpath('//div[@class="modal-content"]//div[@class="modal-header"]//'
                                      'button[@type="button"][@class="close"]')[0].click()
        print("Tickets selling out pop-up has been clicked off.")
    else:
        print("Tickets selling pop-up did not appear.")
    print(driver.find_elements_by_xpath(
        '//div[@class="list-ctn list-ctn-tg-list-on-right"]//div[@class="list-inner-ctn"]//'
        'div[@class="venue-ticket-list clusterize-scroll"]//'
        'div[@id="list-tickets"]//table[@id="tickets-table"]')[0].text)


# Obtain position of current window handle in window handles list
current_window_handle_index = driver.window_handles.index(driver.current_window_handle)
# Obtain position of newly opened tab
new_window_handle_index = current_window_handle_index + 1
driver.switch_to.window(driver.window_handles[new_window_handle_index])

driver.find_elements_by_xpath('//div[@class="list-ctn list-ctn-tg-list-on-right"]//div[@class="list-inner-ctn"]//'
                              'div[@class="venue-ticket-list clusterize-scroll"]//'
                              'div[@id="list-tickets"]//table[@id="tickets-table"]')


# Obtain position of current window handle in window handles list
current_window_handle_index = driver.window_handles.index(driver.current_window_handle)
# Obtain position of newly opened tab
new_window_handle_index = current_window_handle_index - 1
driver.switch_to.window(driver.window_handles[new_window_handle_index])










#
driver.find_elements_by_xpath('//table[@id="productionsTable"]//tr[@class="vdp-event-row odd"]')[0].text
# driver.find_elements_by_xpath('//table[@id="productionsTable"]//tr[@class="vdp-event-row even"]')[0].text

    my_href = driver.find_elements_by_xpath('//table[@id="productionsTable"]//tr[@class="vdp-event-row odd"]//'
                                  'td[@class="vdp-event-row__col--button vdp-event-row__col--button"]//'
                                  'a[@class="vdp-button"]')[0].get_attribute(name='href')
    driver.execute_script("window.open('" + my_href +"');")

# Obtain position of current window handle in window handles list
current_window_handle_index = driver.window_handles.index(driver.current_window_handle)
# Obtain position of newly opened tab
new_window_handle_index = current_window_handle_index + 1
driver.switch_to.window(driver.window_handles[new_window_handle_index])

#driver.find_elements_by_xpath('//div[@class="vdp-modal__container"]')
#driver.find_elements_by_xpath('//div[@class="vdp-modal__body"]')
driver.find_elements_by_xpath('//div[@class="vdp-modal__body"]//figure[@class="row-fluid"]//'
                              'ul[@class="quantity-selectors"]//li[@class="quantity-selector md-radio"]//'
                              'input[@type="radio"][@value="1"]').click()


driver.find_element_by_css_selector("div[class='vdp-modal__container']")

# Obtain remaining URLs
for i in range(0, len(driver.find_elements_by_xpath('//cite[@class="iUh30"]'))):
    print(driver.find_elements_by_xpath('//cite[@class="iUh30"]')[i].text)

for i in range(0, len(driver.find_elements_by_xpath('//cite[@class="iUh30 bc"]'))):
    print(driver.find_elements_by_xpath('//cite[@class="iUh30 bc"]')[i].text)

for i in range(0, len(driver.find_elements_by_xpath('//h3[@class="LC20lb"]'))):
    print(driver.find_elements_by_xpath('//h3[@class="LC20lb"]')[i].text)


for i in range(0, len(driver.find_elements_by_xpath('//a[@style="display:none"]'))):
    print(driver.find_elements_by_xpath('//a[@style="display:none"]')[i])

# Get current tabs
driver.window_handles[0]

driver.find_elements_by_xpath('//li[@class="ads-ad"]')
driver.find_elements_by_xpath('//a[@class="V0MxL r-iSD9cleyK2tA"]')[i].click()

driver.send



driver.find_elements_by_xpath('//li[@class="ads-ad"]//div[@class]//a')[0].get_attribute(name='href')

# Close webdriver
driver.close()

# # Get clickable link text (str) of first ad
# my_href = driver.find_elements_by_xpath('//li[@class="ads-ad"]//a[@class=""]//a')[0].get_attribute(name='href')
# print("Currently openings: " + ad_urls[0])
# driver.execute_script("window.open('" + my_href +"');")
#
# # Obtain position of current window handle in window handles list
# current_window_handle_index = driver.window_handles.index(driver.current_window_handle)
# # Obtain position of newly opened tab
# new_window_handle_index = current_window_handle_index + 1
# driver.switch_to.window(driver.window_handles[new_window_handle_index])