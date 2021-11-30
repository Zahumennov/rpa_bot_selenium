from task import ParseAgencies


class RunParseAgencies:
    def __init__(self):
        self.parse = ParseAgencies
        try:
            self.parse.open_the_website("https://itdashboard.gov/")
            self.parse.click_elem("node-23")
            self.parse.get_agencies('//div[@id="agency-tiles-widget"]//div[@class="col-sm-4 text-center noUnderline"]')
            self.parse.excel.create_exel_file('output/agencies.xlsx')
            self.parse.excel.rename_sheet('output/agencies.xlsx', 'Sheet', 'Agencies')
            self.parse.excel.append_row_to_sheet(a.agency_info, 'output/agencies.xlsx', 'Agencies')
            a.get_agency_page(24)
            a.get_individual_invest('output/agencies.xlsx', 'Individual Investments')
            a.download_pdf()
            a.get_pdf_data()
            a.compare_pdf()

        finally:
            a.browser_lib.close_all_browsers()
