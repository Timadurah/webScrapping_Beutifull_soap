import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, Float, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import asyncio
from pyppeteer import launch
import schedule
import time

DATABASE_URL = "postgresql://user:password@localhost/mydatabase"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    price = Column(Float, index=True)

Base.metadata.create_all(bind=engine)

def save_items(items):
    session = SessionLocal()
    for item in items:
        product = Product(title=item['title'], price=float(item['price'].replace('$', '')))
        session.add(product)
    session.commit()
    session.close()

def parse_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    for item in soup.select('.item-class'):  # Replace with actual classes
        title = item.select_one('.title-class').text.strip()
        price = item.select_one('.price-class').text.strip()
        items.append({'title': title, 'price': price})
    return items

async def fetch_dynamic_page(url):
    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.goto(url, {'waitUntil': 'networkidle2'})
    content = await page.content()
    await browser.close()
    return content

def job():
    url = 'https://example.com/dynamic-products'
    html = asyncio.get_event_loop().run_until_complete(fetch_dynamic_page(url))
    items = parse_page(html)
    save_items(items)

schedule.every().day.at("10:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
