import pymysql

import xlwt

conn = pymysql.connect(host='localhost', password='123456', user='root', database='test', charset='utf8')


cursor = conn.cursor()

count = cursor.execute('select * from test')

fields = cursor.description

content = cursor.fetchall()

workbook = xlwt.Workbook(encoding='utf-8')

sheet = workbook.add_sheet('test', cell_overwrite_ok=True)

# 写入字段的名字
for field in range(0, len(fields)):
	sheet.write(0, field, fields[field][0])


row = 1
col = 0

for row in range(1, len(content)+1):
	for col in range(0, len(fields)):
		sheet.write(row, col, content[row-1][col])
workbook.save('bookname.xls')