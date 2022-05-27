import csv


def read_csv_at(file_path):
	bookmarks = list()
	with open(file_path, 'r', encoding='utf-8-sig') as fr:
		csvreder = csv.reader(fr)
		next(csvreder)

		bookmarks = [(item[6], item[3], item[7], item[-1]) for item in csvreder]

	return bookmarks


def traverse_directory(root_file_path):
	flatten_bookmarks = read_csv_at(root_file_path)

	nested_bookmarks = list()
	for item in flatten_bookmarks:
		if item[0] == '1':
			nested_bookmarks.append((item[-2], traverse_directory('./files/{}.csv'.format(item[1]))))
		else:
			nested_bookmarks.append(item)

	return nested_bookmarks


def to_minimal_chrome_bookmarks(bookmarks):
	bookmark_strs = list()
	for idx, item in enumerate(bookmarks):
		if len(item) == 4:
			bookmark_strs.append('<DT><A HREF="{}">{}</A>'.format(item[-1], item[-2]))
		elif len(item) == 2:
			bookmark_strs.append('<DT> <H3>{}</H3>\n'.format(item[0]) + to_minimal_chrome_bookmarks(item[1]))
		else:
			raise Exception('Error')

	bookmark_html = '<DL><p>\n' + '\n'.join(bookmark_strs) + '\n</DL><p>'

	return bookmark_html


def save_bookmark_to(file_path, html_str):
	with open(file_path, 'w', encoding='utf8') as fw:
		fw.write(html_str)


def format_bookmarks_to_chrome():
	bookmarks = traverse_directory('./files/0.csv')

	html_preifx = '<!DOCTYPE NETSCAPE-Bookmark-file-1>\n <!-- This is an automatically generated file.\n It will be read and overwritten.\n DO NOT EDIT! -->\n<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n<TITLE>Bookmarks</TITLE>\n<H1>Bookmarks</H1>'
	html_str = to_minimal_chrome_bookmarks(bookmarks)

	html_text = html_preifx +'<DL>/<p>\n'+ html_str+'\n</DL><p>'

	save_bookmark_to('./uc_bookmark.html', html_text)
