import time

from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files


class ParseAgencies:

    def __init__(self):
        self.browser_lib = Selenium()
        self.agency_info = {}
        self.exel = Files()

    def open_the_website(self, url):
        self.browser_lib.open_available_browser(url)

    def click_elem(self, elem):
        self.browser_lib.click_element(elem)

    def get_agencies(self, xpath):

        all_agencies = self.browser_lib.find_elements(xpath)
        list_of_agency = [agency.text.split("\n") for agency in all_agencies]
        name_of_agency = [value[0] for value in list_of_agency]
        total = [value[2] for value in list_of_agency]
        self.agency_info = {'Agency': name_of_agency, 'Total spending': total}

    def create_exel_file(self, path):
        try:
            self.exel.create_workbook(path=path, fmt='xlsx')
            self.exel.rename_worksheet('Sheet', 'Agencies')
            self.exel.append_rows_to_worksheet(self.agency_info, 'Agencies', True)
            self.exel.save_workbook()
        finally:
            print(self.exel.read_worksheet('Agencies', True))
            self.exel.close_workbook()


if __name__ == "__main__":
    a = ParseAgencies()

    try:
        a.open_the_website("https://itdashboard.gov/")
        a.click_elem("node-23")
        time.sleep(4)
        a.get_agencies('//div[@id="agency-tiles-widget"]//div[@class="col-sm-4 text-center noUnderline"]')
        a.create_exel_file('output/agencies.xlsx')

    finally:
        a.browser_lib.close_all_browsers()
