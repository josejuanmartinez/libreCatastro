import copy
import re


class OntologyConverter:

    def __init__(self):

        with open("../templates/ontology.owl") as ont_f, \
                open("../templates/individual_city.xml") as ind_city_f, \
                open("../templates/individual_province.xml") as ind_province_f, \
                open("../templates/individual_coord.xml") as ind_coord_f, \
                open("../templates/individual_address.xml") as ind_address_f, \
                open("../templates/individual_cadaster.xml") as ind_cadaster_f:

            self.ont_template = ont_f.read()
            self.city_template = ind_city_f.read()
            self.province_template = ind_province_f.read()
            self.coord_template = ind_coord_f.read()
            self.address_template = ind_address_f.read()
            self.cadaster_template = ind_cadaster_f.read()

    def cadastro_dict_to_ontology(self, cadastro_list):

        ont = copy.deepcopy(self.ont_template)

        for cadastro_entry in cadastro_list:
            ont = ont.replace("####INDIVIDUALS####", ''.join(["####INDIVIDUALS####",
                                                                      self.instantiate_individual(cadastro_entry)]))

        ont = ont.replace("####INDIVIDUALS####", '')

        return ont

    def instantiate_individual(self, cadastro_entry):
        individuals = ''

        cadaster = ''
        for header, value in cadastro_entry.items():
            if header == 'Referencia catastral':
                txt = copy.deepcopy(self.cadaster_template)
                txt = txt.replace("####CADASTER####", value)
                individuals = ''.join([individuals, txt])
                cadaster = value
            elif header == 'Localización':
                city_txt = copy.deepcopy(self.city_template)
                province_txt = copy.deepcopy(self.province_template)
                address_txt = copy.deepcopy(self.address_template)

                cp = re.search(r'[0-9]{5}', value)
                cp_span = cp.span()
                cp_span_end = cp_span[1]

                city_text = value[cp_span_end:]
                province = re.search(r'\(([^\)]+)\)', city_text)
                province_span = province.span()
                province_start = province_span[0]
                province_end = province_span[1]
                province_text = value[province_start:province_end]

                province_txt = province_txt.replace("####CADASTER####", cadaster)
                province_txt = province_txt.replace("####PROVINCE####", province_text)

                city_txt = city_txt.replace("####CITY####", city_text)
                city_txt = city_txt.replace("####PROVINCE####", province_text)

                address_txt = address_txt.replace("####ADDRESS####", value)
                address_txt = address_txt.replace("####CITY####", city_text)

                individuals = ''.join([individuals, province_txt, city_txt, address_txt])

        #print(individuals)
        return individuals




