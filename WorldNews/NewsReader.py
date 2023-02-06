# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 08:43:55 2020

@author: caleb
"""

from bs4 import BeautifulSoup as bs
import requests
import re
import datetime
import pandas as pd
import numpy as np
import time
from PIL import Image, ImageFile
from io import BytesIO
import nltk
from bs4 import BeautifulSoup, NavigableString, Tag
import summarizer as sr
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os

import shutil
def get_top(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        images = soup.find('main').find_all('img')
    except:
        images = soup.find('body').find_all('img')
    
    if len(images) == 0:
        images = soup.find('body').find_all('img')

    data = []
    for img in images[:7]:
        try:
            img_url = img.get('src')
            if not img_url or "logo" in str(img.get('alt', '')).lower():
                continue

            img2_url = img_url if str(url) in str(img_url) else img_url.replace(url, "")
            img_words = re.sub("[^a-zA-Zα-ωΑ-Ω0-9?!,. ]+", ' ', img2_url).split(" ")
            href = img.find_previous('a').get('href')

            if "euronews" not in str(url) and len([word for word in img_words if word.lower() in str(href)]) < 2:
                href = img.find_next('a').get('href')

            if "http" not in href:
                href = '/'.join(str(url).split('/')[:3]) + href

            if "http" not in img_url:
                img_url = '/'.join(str(url).split('/')[:3]) + img_url
            
            response = requests.get(img_url, stream=True)
            im = Image.open(BytesIO(response.content))
            if "live" in str(href) or "liveblog" in str(href):
                continue

            data.append({
                'img_url': img_url,
                'article_url': href,
                'width': im.width,
                'height': im.height,
                'size': im.width * im.height,
            })
        except:
            pass
    
    try:
        top_article = sorted(data, key=lambda x: x['height'], reverse=True)[0]
        
        return top_article['article_url']
    except IndexError:
        pass


def get_article_text(url):
    print(url)
    if url != None:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, features="html.parser")

        # get text
        text = soup.find('body').find_all('p')

        full_text = ' '.join([item.get_text() for item in text[:-1] if len(item.attrs)<=1 and len(nltk.word_tokenize(item.get_text()))>6])
    
    else:
        full_text = "No news articles found"

    

    return full_text

class CountryArticles:
    def __init__(self,country, paper, website,ISO):
        self.iso = str(ISO)
        self.label = str(country)
        self.paper = str(paper)
        self.top_article_link = get_top(website)
        self.article_text = get_article_text(self.top_article_link)
        self.article_summary = sr.run_summarization(self.article_text)
       

def create_html(country_classes):
    sid = SentimentIntensityAnalyzer()
    html = open(dir_path + "/projects.html").readlines()
    linelist = []

    for country in country_classes:
        ss = sum(sid.polarity_scores(sent)['compound'] for sent in nltk.sent_tokenize(str(country.article_text))) / len(nltk.sent_tokenize(str(country.article_summary)))

        newswords = nltk.word_tokenize(str(country.article_summary))
        newarticle1 = ""
        let = 0
        y=0
        for x,word in enumerate(newswords):
            let += len(word)
            if let > len(str(country.top_article_link)):
                newarticle1 = newarticle1 + "\\r\\n" + str(' '.join(newswords[y:x]))
                y=x
                let = 0
        newarticle1 = newarticle1 + "\\r\\n" + str(' '.join(newswords[y:])) + "\\r\\nLink "+ str(country.top_article_link)
        newarticle1 = "\\r\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t" + str(newarticle1)
        combined = newarticle1.replace("'","’").replace(" , ",", ").replace(" ’ ","’").replace("..",".")
        line = "\t\t[{v:'" + str(country.iso) +"',f:'" + str(country.label).replace("'","") + "'},"+str(ss)+",'"+str(combined)+"'],\n"
        linelist.append(line)

    local_time = time.asctime(time.localtime(time.time()))
    print("updated at:", local_time)
    print_time = '\t\t\t\t\t\t\t<i>Last Updated : ' + str(local_time) + '</i></p>\n'

    find2 = html.index('\t\t\t\t\t\t\t<i>Last Updated : [TIME]</i></p>\n')
    html[find2] = print_time
    find = html.index('\t\t\t\t\t\t\t\t[INSERT DATA HERE]\n')
    html[find:find] = linelist
    html.remove('\t\t\t\t\t\t\t\t[INSERT DATA HERE]\n')
    
    save_file = "D://Users/Caleb/Documents/GitHub/caleb-severn.github.io/world-news.html"
    with open(save_file, 'w', encoding='utf-8') as f:
        f.write("".join(html))

    save_file = "D://Users/Caleb/Documents/GitHub/caleb-severn.github.io/projects.html"
    with open(save_file, 'w', encoding='utf-8') as f:
        f.write("".join(html))

start_time  = time.time()
dir_path = os.path.dirname(os.path.realpath(__file__))
main_df = pd.read_csv(dir_path + "\sites.csv", encoding='utf-8')
country_classes = [CountryArticles(value['Country'],value['Paper'],value['Website'],value['ISO']) for key, value in main_df.iterrows() if str(value['Country']) != 'nan']
create_html(country_classes)
print("Done")
print(time.time()-start_time)



    