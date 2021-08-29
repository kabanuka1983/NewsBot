from asyncio import sleep

import requests
from bs4 import BeautifulSoup
from datetime import datetime

from data.loader import bot, scheduler
from data.urls import headers, domain, URL
from utils import database

db = database.DBCommands()


def get_soup(url, header=headers):
    req = requests.get(url, headers=header)
    return BeautifulSoup(req.text, "lxml")


def get_all_post_list(soup, post_date):
    all_post_articles = soup.find_all(class_="col-13 article-time")
    all_post_list = []

    for art in all_post_articles:
        item_timestamp = get_post_timestamp(art)
        item_href = get_post_href(art)
        item_title = get_post_title(art)

        if item_timestamp > post_date:
            all_post_list.append((item_title, item_href, item_timestamp))
    return all_post_list


def get_post_timestamp(art):
    date_string = f'{art.find("span").find_next_sibling().string} {art.find("span").string}'
    date_datetime = str_to_datetime(date_string)
    return date_datetime.timestamp()


def get_post_href(art):
    return f'{domain}{art.find_previous(class_="grid article").find(class_="article-link").get("href")}'


def get_post_title(art):
    return f'{art.find_previous(class_="grid article").find(class_="article-link").string.strip()}'


def str_to_datetime(str):
    return datetime.strptime(str, "%d.%m.%Y %H:%M")


async def publications_update():
    now_date = datetime.now().timestamp()
    for k, _ in URL.items():
        await db.add_new_category(category=k, timestamp=now_date)
    db_publications = await db.get_publications()
    for db_category in db_publications:
        category: str = db_category.category
        last_post_timestamp = db_category.last_publication_timestamp
        url = URL[category]
        soup = get_soup(url)
        all_post_list = get_all_post_list(soup, last_post_timestamp)
        all_pages_list = []
        if all_post_list:
            while all_post_list:
                all_pages_list.extend(all_post_list)
                url = f'{domain}{soup.find(class_="pager").find("a", class_=False).get("href")}'
                soup = get_soup(url)
                all_post_list = get_all_post_list(soup, last_post_timestamp)
        all_pages_list.sort(key=lambda post: post[2], reverse=True)
        await db.update_publications(category, all_pages_list, now_date)
    await main_publications()


async def main_publications():
    db_publications = await db.get_publications()
    publications_dict = {}
    for publication in db_publications:
        publications_dict[publication.category] = eval(str(publication.publications))

    check_list = []
    for _, v in publications_dict.items():
        check_list.extend(v)
    if len(check_list) == 0:
        return

    db_subscribers_for_posting = await db.get_subscribers_for_posting()
    for subscriber in db_subscribers_for_posting:
        chat_id = subscriber.subscriber_id
        categories_dict = subscriber.get_categories_dict()

        all_publications_list = []
        for category, status in categories_dict.items():
            if status and publications_dict[category]:
                all_publications_list.extend(publications_dict[category])
        all_publications_list.sort(key=lambda p: p[2], reverse=False)

        flood_count = 0
        for post in all_publications_list:
            if flood_count > 98:
                await sleep(1)
            post_title = post[0]
            post_href = post[1]
            post_date = datetime.fromtimestamp(post[2]).strftime('%d-%m-%Y %H:%M')
            await bot.send_message(chat_id=chat_id,
                                   text=f'<b>{post_title}</b>\n<a href="{post_href}">{post_date}</a>',
                                   parse_mode="HTML",
                                   disable_web_page_preview=False)
            flood_count += 1


scheduler.add_job(publications_update, 'cron', minute='*/30')
