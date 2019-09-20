import re

from src.settings import config

from src.utils.cadastro_logger import CadastroLogger

logger = CadastroLogger(__name__).logger


class Address:
    """ Domain class for storing Address in Catastro format"""
    def __init__(self, address):
        self.full_address = address.strip()

        ''' Initialization in case some data is not present'''
        self.first_line = None
        self.second_line = None
        self.street = None
        self.cp = None
        self.city = None
        self.province_parentheses = None
        self.province = None

        self.doorway = None
        self.floor = None
        self.door = None

        self.site = None
        self.lot = None

        ''' NLP searchers '''
        self.first_line = self.get_first_line()
        self.second_line = self.get_second_line()

        self.street = self.get_street()
        self.doorway = self.get_doorway()
        self.floor = self.get_floor()
        self.door = self.get_door()

        self.site = self.get_site()
        self.lot = self.get_lot()

        self.cp = self.get_cp()
        self.province_parentheses, self.province = self.get_province()
        self.city = self.get_city()

    def get_first_line(self):
        if self.first_line is not None:
            return self.first_line
        second_line = re.search(config['separator'], self.full_address)

        new_line_pos = None
        if second_line:  # From HTML I will get the separation
            new_line_pos = second_line.span()[0]
        else:  # From XML not
            cp = re.search(r'[0-9]{5}', self.full_address)
            if cp:
                new_line_pos = cp.span()[0]

        return self.full_address[:new_line_pos].strip() if new_line_pos is not None\
            else self.full_address

    def get_second_line(self):
        if self.second_line is not None:
            return self.second_line

        second_line = re.search(config['separator'], self.full_address)

        new_line_pos = None
        if second_line:  # From HTML I will get the separation
            new_line_pos = second_line.span()[0]
        else:  # From XML not
            cp = re.search(r'[0-9]{5}', self.full_address)
            if cp:
                new_line_pos = cp.span()[0]

        return self.full_address[new_line_pos:].strip() if new_line_pos is not None \
            else self.full_address

    def get_street(self):
        return self.get_first_line()

    def get_doorway(self):
        if self.doorway is not None:
            return self.doorway

        doorway_text = None
        doorway = re.search(r'Es:([-a-zA-Z0-9]+)', self.get_first_line())

        if doorway:
            doorway_text = doorway.group(1)

        return doorway_text

    def get_door(self):
        if self.door is not None:
            return self.door

        door_text = None
        door = re.search(r'Pt:([-a-zA-Z0-9]+)', self.get_first_line())

        if door:
            door_text = door.group(1)

        return door_text

    def get_floor(self):
        if self.floor is not None:
            return self.floor

        floor_text = None
        floor = re.search(r'Pl:([-a-zA-Z0-9]+)', self.get_first_line())

        if floor:
            floor_text = floor.group(1)

        return floor_text

    def get_site(self):
        if self.site is not None:
            return self.site

        site_text = None
        site = re.search(r'Polígono ([-a-zA-Z0-9]+)', self.get_first_line())

        if site:
            site_text = site.group(1)

        return site_text

    def get_lot(self):
        if self.lot is not None:
            return self.lot

        lot_text = None
        lot = re.search(r'Parcela ([-a-zA-Z0-9]+)', self.get_first_line())

        if lot:
            lot_text = lot.group(1)

        return lot_text

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
        city_text = city_text.replace(config['separator'],'').strip()
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
        return dict(full_address=self.full_address, first_line=self.first_line, second_line=self.second_line, street=self.street, cp=self.cp, city=self.city, province_parantheses=self.province_parentheses, province=self.province, doorway=self.doorway, floor=self.floor, door=self.door, site=self.site, lot=self.lot)
