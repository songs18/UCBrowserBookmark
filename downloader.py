import csv
import gzip
import json
import sys
import urllib.request

cookie='xxxx'
x_csrf_token='xxxx'


def request_page_of(dir_guid, page_index):
	url = 'https://cloud.uc.cn/api/bookmark/listdata'

	header = {
		'cookie': cookie,
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
		'x-csrf-token': x_csrf_token,
		'content-type': 'application/json',
		'referer': 'https://cloud.uc.cn/home/phone/{}'.format(dir_guid),
		'origin': 'https://cloud.uc.cn',
		'sec-ch-ua-platform': 'Windows',
		'accept': 'application/json, text/plain, */*',
		'accept-encoding': 'gzip, deflate, br',
		'accept-language': 'en,zh-CN;q=0.9,zh;q=0.8',
		'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
		'sec-ch-ua-mobile': '?0',
		'sec-fetch-dest': 'empty',
		'sec-fetch-mode': 'cors',
		'sec-fetch-site': 'same-origin'}

	data = {'cur_page': page_index, 'type': "phone", 'dir_guid': dir_guid}
	print(data)
	request = urllib.request.Request(url=url, headers=header, method='POST',
									 data=bytes(json.dumps(data), encoding='utf8'))

	gzip_response = urllib.request.urlopen(request)
	html_response = gzip.GzipFile(fileobj=gzip_response)
	one_page_bookmarks = json.loads(html_response.read().decode())

	return one_page_bookmarks


def patient_request_page_of(dir_guid, page_index):
	for retry_index in range(5):
		try:
			return request_page_of(dir_guid, page_index)
		except Exception as exp:
			print(exp)
			if retry_index == 4:
				sys.exit(-1)
			print('retry...')


def resolve_(one_page_bookmarks):
	bookmarks = list()
	for item_json in one_page_bookmarks['data']['list']:
		bookmarks.append(item_json)

	return bookmarks


def request_all_pages(dir_guid):
	cur_page = 1
	bookmark_set = list()
	while True:
		one_page_bookmarks = patient_request_page_of(dir_guid, cur_page)
		bookmarks = resolve_(one_page_bookmarks)
		bookmark_set.extend(bookmarks)

		print('pege={}, collected {} bookmarks.'.format(cur_page, len(bookmarks)))

		if not one_page_bookmarks['data']['meta']['has_last_page']:
			break

		cur_page += 1

	return bookmark_set


def extract_title(bookmark_set):
	return bookmark_set[0].keys()


def save_bookmarks_to(bookmark_set, file_path):
	with open(file_path, 'w', newline='', encoding='utf-8-sig') as fw:
		csver = csv.writer(fw, )

		title_row = extract_title(bookmark_set)
		csver.writerow(title_row)

		for item in bookmark_set:
			csver.writerow([item[k] for k in title_row])


def download_bookmarks():
	dir_guids = ['0']

	while True:
		if len(dir_guids) == 0:
			break

		dir_guid = dir_guids.pop(0)
		bookmark_set = request_all_pages(dir_guid)

		dir_guids.extend([item['guid'] for item in bookmark_set if item['is_directory'] == 1])

		save_bookmarks_to(bookmark_set, './files/{}.csv'.format(dir_guid))
