# import requests
import re
import time
import alp
import string

# from bs4 import BeautifulSoup

def getComics(url):
    # Get HTML Content
    # response = requests.get(url)
    response = alp.Request(url)
    # Make soup
    # soup = BeautifulSoup(response.text)
    soup = response.souper()

    #Get the date from the top of the page
    headline = soup.find('div', class_='Headline')
    headlineText = headline.get_text(strip=True)
    d = re.search("([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})", headlineText)
    d = d.group(1)
    date = time.strptime(d, "%m/%d/%Y")

    # Find the table containing the comics
    # table = soup.find("table", {"style":"width: 100%;" ,"border": "1"})
    # print table
    found = False
    comics_table = None
    max_rows = 0
    for table in soup.findAll('table'):
        number_of_rows = len(table.findAll(lambda tag: tag.name == 'tr' and tag.findParent('table') == table))
        if number_of_rows > max_rows:
            if table.findAll(text='DARK HORSE COMICS') and table.findAll(text='IMAGE COMICS'):
                found = True
                comics_table = table
                max_rows = number_of_rows

    entries = {}
    for publisher in comics_table.findAll("td", {"colspan":"3", "align":"center"}):
        # Extract Publishers Name
        name = string.capwords(publisher.text)
        
        # Build a list to hold all books for that publisher
        books = []

        # Look for all books underneath that publisher
        tdCount = 0
        book = {}
        for cell in publisher.find_all_next():
            
            # Break between publishers and end of table
            if cell.attrs == {'colspan': '3', 'align': 'center', 'bgcolor': '#E5E7ED'}:
                break
            if cell.name == "h2":
                break
            if cell.name == "p":
                break

            # Each book consists of 3 td cells
            if cell.name == "td":
                
                tdCount = tdCount + 1

                if tdCount == 1:
                    for link in cell.findAll('a'):
                        thing = link.get('href')
                    book['link'] = thing
                    book['id'] = cell.text
                elif tdCount == 2:
                    text = re.sub('\s*(\(|\[).+$', '',cell.text)
                    book['title'] = string.capwords(text)
                elif tdCount == 3:
                    book['price'] = cell.text
                
                # Prepare variables for next book
                if tdCount == 3:
                    book['date'] = date
                    books.append(book) # Add book dict to books list
                    book = {}   # instantiate a fresh book dictionary
                    tdCount = 0 # reset the td count for next book

        # Add publisher to publisher dictionary
        entries[name] = books

    return entries

if __name__ == "__main__":

    # url = "http://www.previewsworld.com/Home/1/1/71/952" # New Releases
    url = "http://www.previewsworld.com/Home/1/1/71/954" # Upcoming Releases
    
    entries = getComics(url)

    # Print out dictionary
    print entries.keys()
    for key in entries.keys():
        print key
        print '***************'
        for book in entries[key]:
            print '%s - %s' % (book['title'], book['price'])
            print ''


