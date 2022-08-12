from email.policy import default
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time 
import requests
import json
import time
import os
import csv


def get_channel_name_and_list(channel_url: str) -> list:
    driver = webdriver.Firefox()
    driver.get(f"{channel_url}/videos")
    time.sleep(5)
    channel_name = driver.find_element(By.ID, 'channel-header-container').find_elements(By.ID, 'text-container')[0].find_element(By.TAG_NAME, 'yt-formatted-string').text
    main_data = []

    #StackOverflow solution
    last_height = driver.execute_script('return document.documentElement.scrollHeight')
    while True:
        driver.execute_script('window.scrollTo(0, document.documentElement.scrollHeight)')
        time.sleep(2)
        new_height = driver.execute_script('return document.documentElement.scrollHeight')
        if new_height == last_height:
            break
        last_height = new_height
    ######################

    contents = driver.find_elements(By.ID, "contents")[1]
    videos = contents.find_elements(By.ID, "video-title")
    print(f"{'Title':^100}<>{'Views':^12}<>{'Likes':^10}<>{' Likes/Views '}")
    for video in videos:
        video_url = video.get_attribute("href")
        if "/shorts/" in video_url:
            video_url = f"https://www.youtube.com/watch?v={video_url.split('/')[-1]}"
        video_title = video.text
        
        r = requests.get(video_url)
        soup = BeautifulSoup(r.text, "lxml")
        for tag in soup.find_all("script"):
            govnocode = "var ytInitialData = "
            if tag.text.startswith(govnocode):
                data = tag.text[len(govnocode):-1]
                dick = json.loads(data)
                break
        views = int("".join(dick["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"][0]["videoPrimaryInfoRenderer"]["viewCount"]["videoViewCountRenderer"]["viewCount"]["simpleText"].split()[:-1]))
        try:
            likes = int("".join(dick["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"][0]["videoPrimaryInfoRenderer"]["videoActions"]["menuRenderer"]["topLevelButtons"][0]["toggleButtonRenderer"]["defaultText"]["accessibility"]["accessibilityData"]["label"].split()[:-2]))
        except: likes = 0
        main_data += [[video_title, views, likes, likes/views]]
        print(f"{video_title:100s} <> {views:12,} <> {likes:10,} <> {likes/views:.3f}")
    return (channel_name, main_data)

def main():
    channel_url = input("Channel URL: ")
    channel_name, data = get_channel_name_and_list(channel_url)
    with open(f"{channel_name}.csv", "w", newline="") as csvfile:
        w = csv.writer(csvfile, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        w.writerow(["Title", "Views", "Likes", "Likes/Views"])
        w.writerows(data)
    
if __name__ == "__main__":
    main()