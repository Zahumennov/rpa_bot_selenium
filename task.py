import time

from RPA.Browser.Selenium import Selenium

from utils import WorkWithExcel


class ParseAgencies:

    def __init__(self):
        self.browser_lib = Selenium()
        self.agency_info = {}
        self.excel = WorkWithExcel()
        self.all_agencies = []
        self.uii_url = []

    def open_the_website(self, url):
        self.browser_lib.open_available_browser(url)

    def click_elem(self, elem):
        self.browser_lib.wait_until_element_is_visible(elem)
        self.browser_lib.click_element(elem)

    def get_agencies(self, xpath):
        self.browser_lib.wait_until_element_is_visible(
            "//div[@id='agency-tiles-widget']//div[@class='col-sm-4 text-center noUnderline']", 15
        )
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
            except:
                print('Element not found!')
            values = [val.text for val in value]
            data.append(values)

        self.excel.append_row_to_sheet(data, path, sheet)

    def download_pdf(self):
        pass


if __name__ == "__main__":
    a = ParseAgencies()

    try:
        a.open_the_website("https://itdashboard.gov/")
        a.click_elem("node-23")
        a.get_agencies('//div[@id="agency-tiles-widget"]//div[@class="col-sm-4 text-center noUnderline"]')
        a.excel.create_exel_file('output/agencies.xlsx')
        a.excel.rename_sheet('output/agencies.xlsx', 'Sheet', 'Agencies')
        a.excel.append_row_to_sheet(a.agency_info, 'output/agencies.xlsx', 'Agencies')
        a.get_agency_page(24)
        a.get_individual_invest('output/agencies.xlsx', 'Individual Investments')

    finally:
        a.browser_lib.close_all_browsers()
