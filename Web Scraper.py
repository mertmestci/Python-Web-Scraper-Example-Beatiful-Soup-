import requests
from bs4 import BeautifulSoup
import tkinter as tk


class AnnouncementScraper:
    def __init__(self):
        self.show_links = []

    def retrieve_webpage(self, url):
        try:
            session = requests.Session()
            response = session.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as error:
            print(f"Error retrieving {url}: {error}")
            return None
        finally:
            session.close()

    def extract_announcements(self, webpage_content):
        soup = BeautifulSoup(webpage_content, 'html.parser')
        announcements = []
        list_card_wrap_elements = soup.find_all(class_='list-card-wrap') # find elements in class list-card-wrap



        announcement_elements = []
        for wrap_element in list_card_wrap_elements:
            card_elements = wrap_element.find_all(class_='list-card')      #find element in class list card but inside the list-card-wrap class
            announcement_elements.extend(card_elements)    
        for element in announcement_elements:
            title_element = element.select_one('h2')
            date_element = element.select_one('.date')
            link_element = element.find('a', href=True)       #find tag a and check href value
            
            if title_element and date_element and link_element:
                title = title_element.get_text(strip=True)     # strip is using for clear the spaces beginning and end of the element
                date = date_element.get_text(strip=True)
                link = link_element['href']                 # take href 
                
                announcements.append({
                    'Title': title,
                    'Date': date,
                    'Link': link
                })

        return announcements

    def collect_announcements(self, base_url, start, end):
        general_announcements = []
        page_numbers = list(range(start, end + 1))

        for page in page_numbers:
            url = f"{base_url}?page={page}"
            webpage_content = self.retrieve_webpage(url)    # taking webpage content with using retrieve_webpage method
            if webpage_content:
                announcements = self.extract_announcements(webpage_content)
                general_announcements.extend(announcements)
                print(f"Retrieved {len(announcements)} announcements from page {url}")
            else:
                print(f"Failed to retrieve announcements from page {url}")

        return general_announcements

class AnnouncementGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Medipol University Announcements Scraper")

        self.announcements_label = tk.Label(self.root, text="Announcements",font =('Arial',12,'bold'))
        self.announcements_label.grid(row=0, column=2, padx=10, pady=10)
        self.announcements_content_label = tk.Label(self.root, text="Content", font=("Arial", 12, "bold"))
        self.announcements_content_label.grid(row=0, column=3, padx=10, pady=10, sticky="w")

        self.listbox = tk.Listbox(self.root, width=80, height=30)
        self.listbox.grid(row=0, column=2, rowspan=4, padx=10, pady=10)
        self.listbox.bind('<<ListboxSelect>>', self.display_content)   # Call display content method when user select announcement

        self.scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL)
        self.scrollbar.grid(row=0, column=1, rowspan=4, sticky='ns')

        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        self.content_text = tk.Text(self.root, width=60, height=30)
        self.content_text.grid(row=0, column=3, rowspan=4, padx=10, pady=120)

        self.scraper = AnnouncementScraper()
        self.announcements = []

        self.load_announcements()
    

    def display_content(self, event):
        selected_index = self.listbox.curselection()
        
        if not selected_index:
            return

        selected_announcement = self.announcements[selected_index[0]]
        announcement_title = selected_announcement['Title']
        self.root.title(f"Medipol University Announcements - {announcement_title}") # Updating title
        
        webpage_content = self.scraper.retrieve_webpage(selected_announcement['Link']) # Taking selected announcement content
        
        if not webpage_content:
            self.update_content_text("There is no content")
            return
    
        self.scraper.links_to_display = []
        content_text, actual_links = self.parse_webpage_content(webpage_content)
        
        self.update_content_text(content_text, actual_links)
        # Color is return Gray when user  selected the announcement
        self.listbox.itemconfig(selected_index, {'fg': 'gray','bg': 'lightgray'})

    def parse_webpage_content(self, webpage_content):
        soup = BeautifulSoup(webpage_content, 'html.parser')
        
        content_paragraphs = soup.select('p')  # take p tags
        link_elements = soup.select('a[href]')    #  take class href in a tag
        
        content_text_parts = []
        for p in content_paragraphs:
            text = p.get_text(strip=True)    # Take text in tag p
            if text:
                content_text_parts.append(text)
        
        actual_links = []
        for link in link_elements:
            href = link['href']
            if href.startswith("https"):    # only adding links which is start https
                actual_links.append(href)
            
        content_text = "\n\n".join(content_text_parts)
        
        return content_text, actual_links

    def update_content_text(self, content_text, actual_links=None):
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(tk.END, content_text)     # adding text 
        
        if actual_links:
            self.content_text.insert(tk.END, "\nURLs in the article:\n")
            for link in actual_links:
                self.content_text.insert(tk.END, f"{link}\n")    # adding available links on the page 



    def load_announcements(self):
        URL= "https://www.medipol.edu.tr/en/announcements"
        Last_page = 5
        start_page = 0
      

        self.announcements = self.scraper.collect_announcements(URL, start_page, Last_page)

        self.listbox.delete(0, tk.END)    # clear listbox because we need actual and new announcements
        for announcement in self.announcements:
            self.listbox.insert(tk.END, announcement['Title'])

   
def main():
    root = tk.Tk()
    app = AnnouncementGUI(root)
    root.mainloop()
main()