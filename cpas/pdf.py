import pandas as pd
import numpy as np
import PyPDF2


pdf_file = open('C:/Users/jodie/Downloads/List-of-Government-Primary-Schools-2016.pdf', 'rb')
read_pdf = PyPDF2.PdfFileReader(pdf_file)
number_of_pages = read_pdf.getNumPages()
data = []
for i in range(number_of_pages):
    page = read_pdf.getPage(i)
    page_content = page.extractText()
    data.append(page_content.splitlines())

data = [item for sublist in data for item in sublist]

new_strings = []

for string in data:
    new_string = string.replace('€', '')
    new_strings.append(new_string)

data = new_strings

headings = data[0:9]
del data[0:9]
print(headings)

df = pd.DataFrame(columns=headings)

while len(data) > 0:
    if data[8].isdigit():
        new_record = data[0:9]
        del data[0:9]
    else:
        new_record = data[0:8]
        del data[0:8]
        new_record.insert(7, np.NaN)


    df_length = len(df)
    df.loc[df_length] = new_record

df.to_csv('C:/Users/jodie/Documents/Gary Unicef Stuff/gov_schools.csv')


