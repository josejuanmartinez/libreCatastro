import json
import re

from src.settings import config


class Address:
    def __init__(self, address):
        self.full_address = address
        print("Full address: {}", self.full_address)
        print("Separator: {}", config['separator'])
        self.first_line = None
        self.second_line = None
        self.street = None
        self.cp = None
        self.city = None
        self.province_parentheses = None
        self.province = None

        self.first_line = self.get_first_line()
        self.second_line = self.get_second_line()

        self.street = self.get_street()
        self.cp = self.get_cp()
        self.province_parentheses, self.province = self.get_province()
        self.city = self.get_city()

    def get_first_line(self):
        if self.first_line is not None:
            return self.first_line
        second_line = re.search(config['separator'], self.full_address)
        second_line_span = second_line.span()

        return self.full_address[:second_line_span[0]]

    def get_second_line(self):
        if self.second_line is not None:
            return self.second_line

        second_line = re.search(config['separator'], self.full_address)
        second_line_span = second_line.span()

        return self.full_address[second_line_span[1]:]

    def get_street(self):
        return self.get_first_line()

    def get_cp(self):
        if self.cp is not None:
            return self.cp

        cp_text = None
        cp = re.search(r'[0-9]{5}', self.get_second_line())

        if cp:
            cp_span = cp.span()
            cp_text = self.second_line[cp_span[0]:cp_span[1]]

        return cp_text

    def get_city(self):
        if self.city is not None:
            return self.city

        city_text = self.second_line.replace(self.province_parentheses, '')
        if self.cp is not None:
            city_text = city_text.replace(self.cp, '')

        return city_text.strip()

    def get_province(self):
        if self.province_parentheses is not None and self.province is not None:
            return self.province_parentheses, self.province

        province = re.search(r'\(([^)]+)\)', self.second_line)

        province_span = province.span()
        province_parentheses_text = self.second_line[province_span[0]:province_span[1]]
        province_text = province.group(1)

        return province_parentheses_text, province_text

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
