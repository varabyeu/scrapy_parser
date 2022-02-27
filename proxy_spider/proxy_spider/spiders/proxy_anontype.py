import scrapy
import json


class ProxyAnontypeSpider(scrapy.Spider):
    name = 'proxy_anontype'
    allowed_domains = ['www.nntime.com']
    start_urls = ['http://www.nntime.com/proxy-list-01.htm']

    def parse(self, response):
        unsorted_data = {}
        data_odd = {}
        # current URL has a table with structure like odd row, even row
        # so, to read table body particular rows css selector is used
        odd_rows = response.css('table.data tr.odd')
        # cycle "for" iterates the list of particular row with class 'odd'
        for pos, odd_row in enumerate(odd_rows):
            pos = 2 * pos + 1
            odd_row_ip = odd_row.css('td')[1].css('::text').extract()
            odd_anon_type = odd_row.css('td')[2].css('::text').extract()
            data_odd['ip_address'] = odd_row_ip[0]
            data_odd['port'] = odd_anon_type[0]
            # data from table add to unsorted data dictionary
            unsorted_data[pos] = data_odd
        even_rows = response.css('table.data tr.even')
        data_even = {}
        for pos, even_row in enumerate(even_rows):
            pos = 2 * pos
            even_row_ip = even_row.css('td')[1].css('::text').extract()
            even_anon_type = even_row.css('td')[2].css('::text').extract()
            data_odd['ip_address'] = even_row_ip[0]
            data_odd['port'] = even_anon_type[0]
            unsorted_data[pos] = data_odd
        sorted_data = {}
        # to sort data positions is used
        for i in range(len(odd_rows) + len(even_rows) + 2):
            if i in unsorted_data.keys():
                sorted_data[i] = unsorted_data[i]
        with open('data.json', 'w') as file:
            json.dump(sorted_data, file)
