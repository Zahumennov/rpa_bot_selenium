import os
import re
import time

from RPA.Browser.Selenium import Selenium
from RPA.PDF import PDF

from utils import WorkWithExcel


class ParseAgencies:

    NUM_OF_AGENCY = 24

    def __init__(self):
        self.browser_lib = Selenium()
        self.agency_info = {}
        self.excel = WorkWithExcel()
        self.all_agencies = []
        self.uii = []
        self.uii_url = []
        self.investment_title = []
        self.browser_lib.set_download_directory(os.path.join(os.getcwd(), 'output'))
        self.pdf = PDF()
        self.name_of_inv = []
        self.unique_inv_ident = []

    def open_the_website(self, url):
        self.browser_lib.open_available_browser(url)

    def click_elem(self, elem):
        self.browser_lib.wait_until_element_is_visible(elem)
        self.browser_lib.click_element(elem)

    def get_agencies(self, xpath):
        self.browser_lib.wait_until_element_is_visible(
            "//div[@id='agency-tiles-widget']//div[@class='col-sm-4 text-center noUnderline']", 15)
        self.all_agencies = self.browser_lib.find_elements(xpath)
        list_of_agency = [agency.text.split("\n") for agency in self.all_agencies]
        name_of_agency = [value[0] for value in list_of_agency]
        total = [value[2] for value in list_of_agency]
        self.agency_info = {'Agency': name_of_agency, 'Total spending': total}

    def get_agency_page(self, num_of_agency):
        agency = self.all_agencies[num_of_agency - 1]
        agency_url = self.browser_lib.find_element(agency).find_element_by_tag_name('a').get_attribute('href')
        self.browser_lib.go_to(agency_url)

    def get_individual_invest(self, path, sheet):
        data = []

        self.excel.create_new_sheet(path, sheet)

        self.browser_lib.wait_until_element_is_visible("//table[@id='investments-table-object']", 15)
        self.browser_lib.wait_until_page_contains_element(
            '//*[@id="investments-table-object_length"]/label/select', 15
        )
        self.browser_lib.find_element('//*[@id="investments-table-object_length"]/label/select').click()
        self.browser_lib.find_element('//*[@id="investments-table-object_length"]/label/select/option[4]').click()
        self.browser_lib.wait_until_element_is_visible("//a[@class='paginate_button next disabled']", 20)

        table = self.browser_lib.find_element("//table[@id='investments-table-object']")
        rows = table.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')

        for row in rows:
            value = row.find_elements_by_tag_name('td')

            try:
                self.uii_url.append(value[0].find_element_by_tag_name('a').get_attribute('href'))
                self.investment_title.append(value[2].text)
                self.uii.append(value[0].text)
            except Exception:
                pass

            values = [val.text for val in value]
            data.append(values)

        self.excel.append_row_to_sheet(data, path, sheet)

    def download_pdf(self):
        for url in self.uii_url:
            self.browser_lib.go_to(url)
            self.browser_lib.wait_until_page_contains_element('//div[@id="business-case-pdf"]')
            self.browser_lib.find_element('//div[@id="business-case-pdf"]').click()
            self.browser_lib.wait_until_element_is_visible("//div[@id='business-case-pdf']//span", 15)
            self.browser_lib.wait_until_element_is_not_visible("//div[@id='business-case-pdf']//span", 15)
        time.sleep(3)

    def get_pdf_data(self):
        for pdf_name in self.uii:
            text = self.pdf.get_text_from_pdf(f'output/{pdf_name}.pdf')
            self.name_of_inv.append(re.search(
                r'Name of this Investment:(.*)2\.', text[1]).group(1).strip())
            self.unique_inv_ident.append(re.search(
                r'Unique Investment Identifier \(UII\):(.*)Section B', text[1]).group(1).strip())

    def compare_pdf(self):
        for i in range(len(self.investment_title)):
            if self.name_of_inv[i] == self.investment_title[i]:
                print(f'PDF name: {self.name_of_inv[i]} comfirmed!')
            else:
                print(f'PDF name: {self.name_of_inv[i]} does not match')
            if self.unique_inv_ident[i] == self.uii[i]:
                print(f'PDF UII:{self.unique_inv_ident[i]} comfirmed!')
            else:
                print(f'PDF UII:{self.unique_inv_ident[i]} does not match')


if __name__ == "__main__":
    parse = ParseAgencies()

    try:
        parse.open_the_website("https://itdashboard.gov/")
        parse.click_elem("node-23")
        parse.get_agencies('//div[@id="agency-tiles-widget"]//div[@class="col-sm-4 text-center noUnderline"]')
        parse.excel.create_exel_file('output/agencies.xlsx')
        parse.excel.rename_sheet('output/agencies.xlsx', 'Sheet', 'Agencies')
        parse.excel.append_row_to_sheet(parse.agency_info, 'output/agencies.xlsx', 'Agencies')
        parse.get_agency_page(parse.NUM_OF_AGENCY)
        parse.get_individual_invest('output/agencies.xlsx', 'Individual Investments')
        parse.download_pdf()
        parse.get_pdf_data()
        parse.compare_pdf()

    finally:
        parse.browser_lib.close_all_browsers()
