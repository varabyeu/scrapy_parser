import scrapy
import json


def calculate_port(formula: str, dict_var: dict) -> str:
    """This function is used to calculate port using JS code in HTML doc
    """
    new_formula = ''
    for symbol in formula:
        if symbol in dict_var:
            new_formula += str(dict_var[symbol])
        elif symbol == '+':
            continue
        else:
            new_formula += symbol
    return new_formula


def read_rows(all_rows, script_variables, count) -> dict:
    """This func read row in our html table and return dict"""
    parsed_rows_data = {}
    row_data = {}
    pos_odd = -1
    pos_even = 0
    for row in all_rows:
        ip_adress = row.css('td')[1].css('::text').extract()[0]
        port_func = row.css('td').css('::text').extract()[1][19:-1]
        port = calculate_port(port_func, script_variables)
        row_data['ip_address'] = ip_adress
        row_data['port'] = port
        if count == 'even':
            pos_even += 2
            parsed_rows_data[pos_even] = {'ip_address': ip_adress, 'port': port}
        else:
            pos_odd += 2
            parsed_rows_data[pos_odd] = {'ip_address': ip_adress, 'port': port}
    return parsed_rows_data


class ProxyAnontypeSpider(scrapy.Spider):
    name = 'proxy_anontype'
    allowed_domains = ['www.nntime.com']
    start_urls = ['http://www.nntime.com/proxy-list-01.htm']

    def parse(self, response):
        """Parsing

        This func parses html doc and gets data to calculate port,
        gets data of ip_adress and return a dict with a structure like
        {position: {ip_adress: 'ip_adress', port: 'port'}, ...}
        """
        # parsing head to get variable values to calculate port
        head = response.css('head script').extract()[1]
        within_tag = False
        variables_data = []
        for symbol in head:
            if symbol == '<':
                within_tag = True
                continue
            elif symbol == '>':
                within_tag = False
            elif within_tag == False:
                variables_data.append(symbol)
        # making dict with name: value
        dict_variables = {}
        for iter in range(len(variables_data)):
            if variables_data[iter] == '=':
                dict_variables[variables_data[iter-1]] = int(variables_data[iter + 1])
        # current URL has a table with structure like odd row, even row
        # so, to read table body particular rows css selector is used
        odd_rows = response.css('table.data tr.odd')
        even_rows = response.css('table.data tr.even')
        # call functions to get data
        odd_data = read_rows(odd_rows, dict_variables, 'odd')
        even_data = read_rows(even_rows, dict_variables, 'even')
        unsorted_data = odd_data | even_data
        # sorting data by increase position
        sorted_data = {}
        for i in range(len(odd_rows) + len(even_rows) + 2):
            if i in unsorted_data.keys():
                sorted_data[i] = unsorted_data[i]
        # writing data to a file
        with open('data.json', 'w') as file:
            json.dump(sorted_data, file)
