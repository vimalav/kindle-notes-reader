# !python3
# duplicateFinder_bkp.py - Finds and deletes similar highlights [similar strings from a list]

import json
from os import path
from difflib import SequenceMatcher
# import threading
import concurrent.futures


# returns how similar two strings are
def text_matcher(text_a, text_b):
    return int(SequenceMatcher(None, text_a, text_b).ratio() * 100)


# asks the same question until right answers are given
def permission(input_text, op_1, op_2):
    answer = ''
    while answer == '':
        answer = input('%s? [%s/%s]' % (input_text, op_1, op_2))

        if answer == op_1 or answer == op_2:
            return answer
        answer = ''


def update_files(title_of_book, delete_list, data, file_path):
    delete_list.sort(reverse=True)
    for d in delete_list:
        data['highlights'].pop(d)
    with open(file_path, 'w') as json_doc:
        json.dump(data, json_doc, indent=4)
    print(title_of_book + ' updated!')


def get_numbers():
    list_a = []
    while True:
        try:
            list_a = [int(x) for x in input('Select highlights to keep [separated by ","] : ').split(',')]
            break
        except ValueError:
            continue
    return list_a


def search_books(book_dict, book_index):
    # print (book_index)
    # book_index = book_titles['books'].index(book_dict)
    book_name = book_dict['title']
    book_author = ';'.join(book_dict['authors'])
    book_folder_path = path.join('Y:\\Works\\PythonSample\\KindleNotes\\books', book_author, book_name, '')

    with open(book_folder_path + 'highlights.json', 'r') as json_file:
        book_record = json.load(json_file)

    matches_log = []
    seen_log = []
    # delete_log = []
    # print('Scanning [%s/%s] : %s' % (book_number, book_titles['totalBooks'], title))

    # print(str(round(book_number / book_titles['totalBooks'] * 100, 2)) + '% Complete')

    # book_number += 1
    # print('scanning' + book_name)
    for j in book_record['highlights']:
        matches_temp_log = []
        search_text = j['text']
        index_search_text = book_record['highlights'].index(j)

        if index_search_text in seen_log:
            continue

        seen_log.append(index_search_text)
        matches_temp_log.append(index_search_text)

        # finding similar highlights
        for k in book_record['highlights']:
            check_text = k['text']
            index_check_text = book_record['highlights'].index(k)

            match_percent = text_matcher(search_text, check_text)

            if 80 < match_percent < 100:
                seen_log.append(index_check_text)
                matches_temp_log.append(index_check_text)

        # if matches found..
        if len(matches_temp_log) > 1:
            matches_log.append(matches_temp_log)

    if len(matches_log) > 1:
        print(str(len(matches_log)) + ' matches found in ' + book_name)
        matches_book_log.update({book_index: matches_log})
        with open(book_folder_path + 'matches.json', 'w') as json_doc:
            json.dump(matches_book_log, json_doc, indent=4)


matches_book_log = {}


def main():
    with open('Y:\\Works\\PythonSample\\KindleNotes\\books\\titles.json', 'r') as jsonFile:
        book_titles = json.load(jsonFile)
    print('Scanning Titles..')

    with concurrent.futures.ThreadPoolExecutor() as thread_executor:
        futures = [thread_executor.submit(search_books, title_dict, book_titles['books'].index(title_dict)) for
                   title_dict in book_titles['books']]
        return_value = [f.result() for f in futures]

    if len(matches_book_log) > 0:
        print('Similar highlights found : ')

    for match_index in matches_book_log:
        delete_log = []

        title = book_titles['books'][match_index]['title']
        author = ';'.join(book_titles['books'][match_index]['authors'])
        folder_path = path.join('Y:\\Works\\PythonSample\\KindleNotes\\books', author, title, '')

        with open(folder_path + 'highlights.json', 'r') as json_file:
            highlights_record = json.load(json_file)

        for each_match_list in matches_book_log[match_index]:
            rank_list = [0]*len(each_match_list)
            longest = [0, 0]
            punctuations_list = ['.', '!', '”', '“', ')', '?']

            for item in each_match_list:
                match_text = highlights_record['highlights'][item]['text']
                print('%s : %s\n' % (each_match_list.index(item), match_text))

            # trying out a prediction code ;)  if succeeds can automate the whole cleaning :D
                if match_text[0].isupper():
                    rank_list[each_match_list.index(item)] += 1
                if match_text[0].isupper() and match_text[-2] == '.':
                    rank_list[each_match_list.index(item)] += 1
                if match_text[0] == '“' and match_text[-2] == '”':
                    rank_list[each_match_list.index(item)] += 2
                if match_text[-2] in punctuations_list:
                    rank_list[each_match_list.index(item)] += 1
                if len(match_text) > longest[0] and (match_text[0].isuppper() or match_text[-2] in punctuations_list):
                    longest[0] = len(match_text)
                    longest[1] = each_match_list.index(item)

            rank_list[longest[1]] += 1
            recommendation = rank_list.index(max(rank_list))

            if rank_list.count(max(rank_list)) > 1:
                recommendation = 'not sure'
            elif 4 in rank_list and 3 in rank_list:
                recommendation = 'not sure'

            if max(rank_list) == 4 and 3 not in rank_list:
                each_match_list.remove(each_match_list[recommendation])
            elif max(rank_list) == 3:
                each_match_list.remove(each_match_list[recommendation])
            # end of prediction code

            else:
                print('Keep recommendation from %s : %s' % (rank_list, str(recommendation)))
                for item in get_numbers():  # this asks for input
                    each_match_list.remove(each_match_list[item])

            for item in each_match_list:
                delete_log.append(item)
            # delete_log = matches_log
            # print(delete_log)
            print('Highlight saved!\n')

        update_files(title, delete_log, highlights_record, file_path=folder_path + 'highlights.json')

    print('All files cleaned!')


if __name__ == '__main__':
    main()
