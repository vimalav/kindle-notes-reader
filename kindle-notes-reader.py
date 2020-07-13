#!/usr/bin/env python3
# Script to format Kindle Highlights and Notes in Markdown

"""
-- ToDo --

1   DONE - Dict of book details
    DONE - book_record={'Book 1':{'Author:':'Yuval Nova','Title:':'Sapiens','Highlights:':{'time1':'h1','time2':'h2'}}}
    DONE - Auto detect Kindle and run the script

2   DONE - Split each Book Notes into separate file
    - Convert to markdown / HTML later - generate HTML from python Flask(?) 
    - Store the records in Firebase(?) for access through web Django(?)
    DONE- book_titles = {'id':number,'title':book_title,'authors':author_name,'cover':cover_link}

3   WIP  - Upload text to GitHub Pages
    DONE  - Crate HTML page with all the data. the data should be JSON format
    DONE  - Populate the data (json) using Javascript(?)
    WIP  - Python script to automate Git add + commit whenever reader script runs


4   Second Brain creation
    - Adding notes to Evernote / Web page upload
    - multi threading to make the program faster - BEWARE of concurrency issues

5   DONE - Fetch book meta data from the web (Cover, ISBN, Author etc)
    DONE - Use google API to search for book by book_title
    DONE - Method to store the data - database(?) - json
    DONE - maybe i can get the Google Books API data directly.
    - OR Try parsing amazon for the book details. Using Beautiful Soup (what are pandas?!)

6   Create Quote wallpaper with the highlights (on demand)
    - Got to know this can be done pretty neatly in python
    - Run python in the server(?)

7   Link between Notes (Tag Notes)
    - Wikipedia API for linking keywords from highlights?
    - Also checkout google NLP API - for sentiment analysis of the text highlights
"""

import json
import os
import re
import time
from difflib import SequenceMatcher
from string import ascii_uppercase
import requests
from PIL import Image
import duplicateFinder
import PIL

def split_title_author(book_meta_details):
    split = re.split(r'\s\(', book_meta_details)
    title_of_book = split[0]
    author_of_book = re.sub('[^a-zA-Z0-9 ,;]', '', split[-1])
    return title_of_book, author_of_book


# heart of program - thanks to arainchi: https://stackoverflow.com/a/19871956/13745861
def find(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in find(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in find(j, kv):
                yield x


def get_book_cover(book_titles_dict):

    for book in book_titles_dict['books']:
        if not os.path.exists(book['thumbnail']):
            title_of_book = book['title']
            author_of_book = ';'.join(book['authors'])
            link_to_folder = os.path.join('Y:\\Works\\PythonSample\\KindleNotes\\books', author_of_book, title_of_book,
                                          '')

            try:
                # google books API call
                response = requests.get('https://www.googleapis.com/books/v1/volumes?q=' + title_of_book)
                book_json = response.json()

            except (ConnectionError, TimeoutError):
                print('Google books API unavailable : ' + title)
                return

            for attempt in range(2):
                try:
                    photo_link = book_json['items'][attempt]['volumeInfo']['imageLinks']['thumbnail']
                    photo_high_res = photo_link.replace("zoom=1", "zoom=0")
                    photo_response = requests.get(photo_high_res)
                    with open(link_to_folder + 'cover.jpg', 'wb') as photo_data:
                        photo_data.write(photo_response.content)

                    # making thumbnail
                    im = Image.open(link_to_folder + 'cover.jpg')
                    width, height = (im.size[0], im.size[1])
                    new_width, new_height = 170, 252

                    if int(new_width * height / width) < new_height:
                        new_width = int(new_height * width / height)
                    resized_im = im.resize((new_width * 2, new_height * 2))
                    resized_im.save(link_to_folder + 'thumbnail.jpg')
                    break

                except (FileNotFoundError, ReferenceError, PermissionError):
                    print('Cover for ' + title_of_book + ' unavailable in try ' + str(attempt))


def text_matcher(text_a, text_b):
    return int(SequenceMatcher(None, text_a, text_b).ratio()*100)


def update_files(data, file_path):
    with open(file_path, 'w') as json_doc:
        json.dump(data, json_doc, indent=4)


def print_with_loader(text):
    for x in range(0, 3):
        b = text + ("." * x)
        print(b, end="\r")
        time.sleep(.5)
    print(text + '..')


def get_path():  # checks if Kindle is connected -- this is a jugaad code, prone to error.
    for letter in ascii_uppercase:
        file_path = os.path.join(letter + ':', 'documents', 'My Clippings.txt')
        if os.path.exists(file_path):
            return file_path
    return ""


print_with_loader(text="Kindle Notes Reader")  # animated heading

kindle_path = get_path()  # prompt to connect Kindle
while kindle_path == "":
    input('Please connect your Kindle..(press any key to continue)')
    kindle_path = get_path()

print('Loading "My Clippings" from Kindle')  # opening My Clippings file from Kindle
highlights_file = open(kindle_path, mode='r', encoding='utf_8_sig')
kindle_text = highlights_file.readlines()

# this now simple try - except code took you hell lot of time - just to remind
try:  # check for existing books
    with open('books/titles.json', 'r') as json_file:
        book_titles = json.load(json_file)  # update the titles dictionary
except FileNotFoundError:
    book_titles = {'totalBooks': 0, 'books': []}

timeRegEx = re.compile(r', (.*)')

line_number = 0
compare_text = ['', '']
empty = ['', '\n']

while True:
    book_meta = re.sub('[^a-zA-Z0-9() ,;]', '', kindle_text[line_number])
    highlight_time = (timeRegEx.search(kindle_text[line_number + 1])).group(1)
    highlight_text = kindle_text[line_number + 3]
    line_number = line_number + 5

    temp_record = {'meta_data': {}, 'highlights': []}
    title, author = split_title_author(book_meta)  # returns title and author
    folder_path = os.path.join('books', author, title, '')

    if title not in list(find(book_titles, 'title')):

        # creating folder
        os.makedirs(folder_path, exist_ok=True)

        # eliminating empty highlights
        if highlight_text in empty:
            continue
        compare_text.append(highlight_text)

        # with open(folder_path + 'highlights.txt', 'w', encoding='utf_8_sig') as file:
        #     file.write('Added on: ' + highlight_time + '\n\n' + highlight_text + '\n--------\n\n')

        # updating json files
        book_titles['totalBooks'] += 1
        book_titles['books'].append({'title': title, 'authors': author.split(';'), 'selfLink': folder_path,
                                     'thumbnail': folder_path + 'thumbnail.jpg'})
        update_files(book_titles, file_path='books/titles.json')

        temp_record['meta_data'].update({'bookId': str(book_titles['totalBooks']), 'title': title})
        temp_record['meta_data'].update({'authors': author.split(';'), 'selfLink': folder_path})
        temp_record['meta_data'].update({'thumbnail': folder_path + 'thumbnail.jpg'})

        temp_record['highlights'].append({'time': highlight_time, 'text': highlight_text})
        update_files(temp_record, file_path=folder_path + 'highlights.json')
        temp_record.clear()
        # print('Added highlights : ' + title)
    else:
        with open(folder_path + 'highlights.json', 'r') as jsonFile:
            temp_record = json.load(jsonFile)

        # refining highlights

        # checks for highlight_time duplicate
        if 0 == len(list(find(temp_record, highlight_time))):
            if highlight_text in empty:  # skips empty lines
                continue
            compare_text.append(highlight_text)
            match = compare_text.count(highlight_text)
            if match < 2:   # if there are no duplicates
                # print(match)
                # print(highlight_text)
                temp_record['highlights'].append({'time': highlight_time, 'text': highlight_text})
                update_files(temp_record, file_path=folder_path + 'highlights.json')
                temp_record.clear()
                # with open(folder_path + 'highlights.txt', 'a', encoding='utf_8_sig') as file:
                #     file.write('Added on: ' + highlight_time + '\n\n' + highlight_text + '\n--------\n\n')
            compare_text.pop(0)
    if line_number >= len(kindle_text):  # when kindle_text scan reaches end
        get_book_cover(book_titles)
        print('\nBook covers updated..')
        break

answer = ''
while answer == '':
    answer = input('Run duplicateFinder? (y/n)')
    if answer == 'y' or answer == 'n':
        if answer == 'y':
            duplicateFinder.main()
        break
    answer = ''

print('Kindle highlights & notes updated!')
