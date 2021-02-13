import requests
import datetime
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

# Update Name and Symbol to change which stock is checked.
COMPANY_NAME = "Twitter"
COMPANY_SYMBOL = "TWTR"

USERNAME = os.environ.get("EMAIL_USER")
PASSWORD = os.environ.get("PASSWORD")

# You can change EMAIL_PRIVATE to update the email address that the information is sent to.
EMAIL_PRIVATE = os.environ.get("EMAIL_PRIVATE")

parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": COMPANY_SYMBOL,
    "datatype": "json",
    "apikey": API_KEY
}
# Stock API request
stock_api = requests.get(url="https://www.alphavantage.co/query?", params=parameters)
stock_api.raise_for_status()
stock_info = stock_api.json()

# Getting yesterday and the day before date for running API searches
yesterday_date = stock_info["Meta Data"]["3. Last Refreshed"]
day_before = yesterday_date.split("-")
day_before = [int(numeric_string) for numeric_string in day_before]
day_before[2] = day_before[2] - 1

# Due to the use of split and adding the extra zeros through an f string, I have to check if month
# and date are less than 10 due to adding a zero to 11 or higher would error the remaining code.
if day_before[1] < 10 and day_before[2] > 10:
    day_before_date = f"{day_before[0]}-0{day_before[1]}-{day_before[2]}"
elif day_before[2] < 10 and day_before[1] > 10:
    day_before_date = f"{day_before[0]}-{day_before[1]}-0{day_before[2]}"
elif day_before[1] < 10 and day_before[2] < 10:
    day_before_date = f"{day_before[0]}-0{day_before[1]}-0{day_before[2]}"

today = str(datetime.date.today())

# I have noticed with API that it doesnt always update on the day, therefore, I have a try, except so
# that it will catch this and use yesterday and the data of the day before. This is just a project to
# see that it would work, with a paid API this would not be needed.
try:
    stock_close_day_today = float(stock_info["Time Series (Daily)"][today]["4. close"])
    print(f"Today {today}: ${round(stock_close_day_today, 2)}")
    stock_close_yesterday = float(stock_info["Time Series (Daily)"][yesterday_date]["4. close"])
    print(f"Yesterday {yesterday_date} : ${round(stock_close_yesterday, 2)}")
except KeyError:
    stock_close_yesterday = float(stock_info["Time Series (Daily)"][yesterday_date]["4. close"])
    print(f"Yesterday close {yesterday_date} : ${round(stock_close_yesterday, 2)}")
    stock_close_day_before_yesterday = float(stock_info["Time Series (Daily)"][day_before_date]["4. close"])
    print(f"Day before yesterday close {day_before_date}: ${round(stock_close_day_before_yesterday, 2)}")


def notify(yesterday, the_day_before):
    # Check for news
    # News API
    news_parameters = {
        "apikey": NEWS_API_KEY,
        "qInTitle": COMPANY_NAME

    }
    news_api = requests.get(url="https://newsapi.org/v2/everything?", params=news_parameters)
    news_api.raise_for_status()
    news_articles = news_api.json()["articles"]
    print(news_articles)
    top_three_articles = news_articles[:3]
    articles_formatted = [f"Headline: {article['title']} \n Brief: "
                          f"{article['description'].encode('utf-8').strip()}" for article in top_three_articles]
    difference = round((yesterday - the_day_before), 2)
    if difference > .05*yesterday:
        print(f"The stock prices is up ${difference}")
        for article in articles_formatted:
            with smtplib.SMTP("SMTP.gmail.com", 587) as connection:
                connection.starttls()
                connection.login(user=USERNAME, password=PASSWORD)
                connection.sendmail(from_addr=USERNAME,
                                    to_addrs=EMAIL_PRIVATE,
                                    msg=f"Subject:{COMPANY_NAME} Stock Update \n\nStock difference is "
                                        f"up ${difference} News: {article}")

    elif difference < -.05*yesterday:
        print(f"The stock prices is down ${difference}")
        for article in articles_formatted:
            with smtplib.SMTP("SMTP.gmail.com", 587) as connection:
                connection.starttls()
                connection.login(user=USERNAME, password=PASSWORD)
                connection.sendmail(from_addr=USERNAME,
                                    to_addrs=EMAIL_PRIVATE,
                                    msg=f"Subject:{COMPANY_NAME} Stock Update \n\nStock difference is "
                                        f"up ${difference} News: {article}")


try:
    #notify(stock_close_day_today, stock_close_yesterday)
    notify(890, 720)
except NameError:
    notify(stock_close_yesterday, stock_close_day_before_yesterday)

