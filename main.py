import dotenv as env
import os
import requests
import datetime as dt
from twilio.rest import Client

env.load_dotenv("B:/Coding/Python/EnviromentVariables/.env")

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
alpha_vantage_api_key = os.getenv("snp_alpha_vantage_api_key")
news_api_key = os.getenv("snp_news_api_key")
account_sid = os.getenv("ra_twillio_account_sid")
auth_token = os.getenv("ra_twillio_auth_token")

today_date = dt.date.today() - dt.timedelta(4)
yesterday = dt.datetime.now() - dt.timedelta(5)
yesterday_date = dt.datetime.strftime(yesterday, '%Y-%m-%d')
# print(yesterday_date)
# print(today_date)

alpha_vantage_params = {
    "function": "TIME_SERIES_INTRADAY",
    "symbol": STOCK,
    "interval": "60min",
    "apikey": alpha_vantage_api_key,

}

news_api_params = {
    "q": "Tesla",
    "from": f"{today_date}",
    "sortBy": "popularity",
    "apiKey": f"{news_api_key}",
    "language": "en",
}


def get_change(current, previous):
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return float('inf')


## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
send_message = False
with requests.get("https://www.alphavantage.co/query", params=alpha_vantage_params) as connection:
    connection.raise_for_status()
    response = connection.json()
    previous_day_open = float(response["Time Series (60min)"][f"{str(yesterday_date)} 19:00:00"]["1. open"])
    current_day_open = float(response["Time Series (60min)"][f"{str(today_date)} 12:00:00"]["1. open"])
    # print(previous_day_open)
    # print(current_day_open)
    percent = abs(round(get_change(current_day_open, previous_day_open), 2))
if percent == 5:
    send_message = True

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.

with requests.get("https://newsapi.org/v2/everything", params=news_api_params) as connection:
    connection.raise_for_status()
    response = connection.json()
    results = response["articles"][:3]
# results_dict = [{}]
# for num in range(0, 3):
#     results_dict.append(results[num])
# results_dict.append(results[num]["description"])
# print(results_dict)
# print(results_dict)
## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number.
if not send_message:

    formatted_articles = [f"Headline: {article['title']}. \nBrief: {article['description']}" for article in results]
    print(formatted_articles)
    client = Client(account_sid, auth_token)

    for article in formatted_articles:
        message = client.messages \
            .create(
            body=article,
            from_='+447481337984',
            to='+447876203324'
        )
        print(message.status)

# Optional: Format the SMS message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""
