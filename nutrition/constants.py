# web_nutrition: a web based nutrition and diet analysis program.
# Copyright (C) 2008 Edgar Denny

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

class Tracked_Nutrients:
    def __init__(self):
        self.general = [
            [208, 'kcal', 'Energy'],
            [203, 'g', 'Protein'],
            [204, 'g', 'Total lipid (fat)'],
            [205, 'g', 'Carbohydrates'],
            [291, 'g', 'Fiber, total dietary'],
            [209, 'g', 'Starch'],
            [269, 'g', 'Sugars, total'],
            [221, 'g', 'Alcohol, ethyl'],
            [255, 'g', 'Water'],
            [262, 'mg', 'Caffeine']]
#     [207, 'g', 'Ash'],
#     [210, 'g', 'Sucrose'],
#     [211, 'g', 'Glucose (dextrose)'],
#     [212, 'g', 'Fructose'],
#     [213, 'g', 'Lactose'],
#     [214, 'g', 'Maltose'],
#     [257, 'g', 'Adjusted Protein'],
#     [263, 'mg', 'Theobromine'],
#     [268, 'kj', 'Energy'],
#     [287, 'g', 'Galactose'],

        self.minerals = [
            [301, 'mg', 'Calcium, Ca'],
            [303, 'mg', 'Iron, Fe'],
            [304, 'mg', 'Magnesium, Mg'],
            [305, 'mg', 'Phosphorus, P'],
            [306, 'mg', 'Potassium, K'],
            [307, 'mg', 'Sodium, Na'],
            [309, 'mg', 'Zinc, Zn'],
            [312, 'mg', 'Copper, Cu'],
            [315, 'mg', 'Manganese, Mn'],
            [317, 'mcg', 'Selenium, Se']]
#    [313, 'mcg', 'Fluoride, F'],

        self.vitamins = [
            [318, 'IU', 'Vitamin A'],
            [319, 'mcg', 'Retinol'],
            [321, 'mcg', 'Alpha-Carotene'],
            [322, 'mcg', 'Beta-Carotene'],
            [334, 'mcg', 'Beta-Cryptoxanthin'],
            [337, 'mcg', 'Lycopene'],
            [338, 'mcg', 'Lutein + Zeaxanthin'],
            [404, 'mg', 'B1 (Thiamin)'],
            [405, 'mg', 'B2 (Riboflavin)'],
            [406, 'mg', 'B3 (Niacin)'],
            [410, 'mg', 'B5 (Pantothenic acid)'],
            [415, 'mg', 'B6 (Pyridoxine)'],
            [417, 'mcg', 'Folate'],
            [418, 'mcg', 'B12 (Cyanocobalamin)'],
            [401, 'mg', 'Vitamin C'],
            [324, 'IU', 'Vitamin D'],
            [323, 'mg', 'Vitamin E (Alpha-Tocopherol)'],
            [341, 'mg', 'Tocopherol, beta'],
            [342, 'mg', 'Tocopherol, gamma'],
            [343, 'mg', 'Tocopherol, delta'],
            [430, 'mcg', 'Vitamin K (Phylloquinone)']]
#    [320, 'mcg_RAE', 'Vitamin A, RAE'],
#     [421, 'mg', 'Choline, total'],
#     [431, 'mcg', 'Folic acid'],
#     [432, 'mcg', 'Folate, food'],
#     [435, 'mcg_DFE', 'Folate, DFE'],
#     [573, 'mg', 'Vitamin E, added'],
#     [578, 'mcg', 'Vitamin B-12, added'],

        self.amino_acids = [
            [501, 'g', 'Tryptophan'],
            [502, 'g', 'Threonine'],
            [503, 'g', 'Isoleucine'],
            [504, 'g', 'Leucine'],
            [505, 'g', 'Lysine'],
            [506, 'g', 'Methionine'],
            [507, 'g', 'Cystine'],
            [508, 'g', 'Phenylalanine'],
            [509, 'g', 'Tyrosine'],
            [510, 'g', 'Valine'],
            [511, 'g', 'Arginine'],
            [512, 'g', 'Histidine'],
            [513, 'g', 'Alanine'],
            [514, 'g', 'Aspartic acid'],
            [515, 'g', 'Glutamic acid'],
            [516, 'g', 'Glycine'],
            [517, 'g', 'Proline'],
            [518, 'g', 'Serine']]
#     [454, 'mg', 'Betaine'],
#     [521, 'g', 'Hydroxyproline']]

        self.fats = [
            [606, 'g', 'Fatty acids, total saturated'],
            [645, 'g', 'Fatty acids, total monounsaturated'],
            [646, 'g', 'Fatty acids, total polyunsaturated'],
            [605, 'g', 'Fatty acids, total trans'],
            [601, 'mg', 'Cholesterol'],
            [636, 'mg', 'Phytosterols'],
            [618, 'g', '18:2 undifferentiated'],
            [675, 'g', '18:2 n-6 c,c (linoleic acid)'],
            [851, 'g', '18:3 n-3 c,c,c (alpha-linolenic acid, ALA)'],
            [629, 'g', '20:5 n-3 (EPA)'],
            [621, 'g', '22:6 n-3 (DHA)'],
            [619, 'g', '18:3 undifferentiated'],
            [620, 'g', '20:4 undifferentiated']
    ]
#     [607, 'g', '4:0'],
#     [608, 'g', '6:0'],
#     [609, 'g', '8:0'],
#     [610, 'g', '10:0'],
#     [611, 'g', '12:0'],
#     [612, 'g', '14:0'],
#     [613, 'g', '16:0'],
#     [614, 'g', '18:0'],
#     [615, 'g', '20:0'],
#     [617, 'g', '18:1 undifferentiated'],
#     [624, 'g', '22:0'],
#     [625, 'g', '14:1'],
#     [626, 'g', '16:1 undifferentiated'],
#     [627, 'g', '18:4'],
#     [628, 'g', '20:1'],
#     [630, 'g', '22:1 undifferentiated'],
#     [631, 'g', '22:5 n-3'],
#     [638, 'mg', 'Stigmasterol'],
#     [639, 'mg', 'Campesterol'],
#     [641, 'mg', 'Beta-sitosterol'],
#     [652, 'g', '15:0'],
#     [653, 'g', '17:0'],
#     [654, 'g', '24:0'],
#     [662, 'g', '16:1 t'],
#     [663, 'g', '18:1 t'],
#     [664, 'g', '22:1 t'],
#     [665, 'g', '18:2 t not further defined'],
#     [666, 'g', '18:2 i'],
#     [669, 'g', '18:2 t,t'],
#     [670, 'g', '18:2 CLAs'],
#     [671, 'g', '24:1 c'],
#     [672, 'g', '20:2 n-6 c,c'],
#     [673, 'g', '16:1 c'],
#     [674, 'g', '18:1 c'],
#     [676, 'g', '22:1 c'],
#     [685, 'g', '18:3 n-6 c,c,c'],
#     [687, 'g', '17:1'],
#     [689, 'g', '20:3 undifferentiated'],
#     [693, 'g', 'Fatty acids, total trans-monoenoic'],
#     [695, 'g', 'Fatty acids, total trans-polyenoic'],
#     [696, 'g', '13:0'],
#     [697, 'g', '15:1'],
#     [852, 'g', '20:3 n-3'],
#     [853, 'g', '20:3 n-6'],
#     [855, 'g', '20:4 n-6'],
#     [856, 'g', '18:3i'],
#     [857, 'g', '21:5'],
#     [858, 'g', '22:4']]

class DefaultRdi:
    def __init__(self):
        self.general = [
            [208, 'kcal', 'Energy', 1950, 2500],
            [203, 'g', 'Protein', 56, 280],
            [204, 'g', 'Total lipid (fat)', 65, 195],
            [205, 'g', 'Carbohydrates', 130, 650],
            [291, 'g', 'Fiber, total dietary', 30, 150],
            [209, 'g', 'Starch', 0, 0],
            [269, 'g', 'Sugars, total', 0, 0],
            [221, 'g', 'Alcohol, ethyl', 0, 0],
            [255, 'g', 'Water', 3700, 18500],
            [262, 'mg', 'Caffeine', 0, 0]]
#     [207, 'g', 'Ash'],
#     [210, 'g', 'Sucrose'],
#     [211, 'g', 'Glucose (dextrose)'],
#     [212, 'g', 'Fructose'],
#     [213, 'g', 'Lactose'],
#     [214, 'g', 'Maltose'],
#     [257, 'g', 'Adjusted Protein'],
#     [263, 'mg', 'Theobromine'],
#     [268, 'kj', 'Energy'],
#     [287, 'g', 'Galactose'],

        self.minerals = [
            [301, 'mg', 'Calcium, Ca', 1000, 2500],
            [303, 'mg', 'Iron, Fe', 8, 45],
            [304, 'mg', 'Magnesium, Mg', 7.1, 11],
            [305, 'mg', 'Phosphorus, P', 700, 4000],
            [306, 'mg', 'Potassium, K', 4700, 23500],
            [307, 'mg', 'Sodium, Na', 1500, 2300],
            [309, 'mg', 'Zinc, Zn', 11, 40],
            [312, 'mg', 'Copper, Cu', 0.9, 10],
            [315, 'mg', 'Manganese, Mn', 2.3, 11],
            [317, 'mcg', 'Selenium, Se', 55, 400]]
#    [313, 'mcg', 'Fluoride, F'],

        self.vitamins = [
            [318, 'IU', 'Vitamin A', 4000, 10000],
            [319, 'mcg', 'Retinol', 0, 0],
            [321, 'mcg', 'Alpha-Carotene', 0, 0],
            [322, 'mcg', 'Beta-Carotene', 0, 0],
            [334, 'mcg', 'Beta-Cryptoxanthin', 0, 0],
            [337, 'mcg', 'Lycopene', 0, 0],
            [338, 'mcg', 'Lutein + Zeaxanthin', 0, 0],
            [404, 'mg', 'B1 (Thiamin)', 1.2, 6],
            [405, 'mg', 'B2 (Riboflavin)', 1.3, 6.5],
            [406, 'mg', 'B3 (Niacin)', 16, 35],
            [410, 'mg', 'B5 (Pantothenic acid)', 5, 25],
            [415, 'mg', 'B6 (Pyridoxine)', 1.7, 100],
            [417, 'mcg', 'Folate', 400, 1000],
            [418, 'mcg', 'B12 (Cyanocobalamin)', 2.4, 12],
            [401, 'mg', 'Vitamin C', 90, 2000],
            [324, 'IU', 'Vitamin D', 400, 2000],
            [323, 'mg', 'Vitamin E (Alpha-Tocopherol)', 15, 1000],
            [341, 'mg', 'Tocopherol, beta', 0, 0],
            [342, 'mg', 'Tocopherol, gamma', 0, 0],
            [343, 'mg', 'Tocopherol, delta', 0, 0],
            [430, 'mcg', 'Vitamin K (Phylloquinone)', 120, 600]]
#     [320, 'mcg_RAE', 'Vitamin A, RAE'],
#     [421, 'mg', 'Choline, total'],
#     [431, 'mcg', 'Folic acid'],
#     [432, 'mcg', 'Folate, food'],
#     [435, 'mcg_DFE', 'Folate, DFE'],
#     [573, 'mg', 'Vitamin E, added'],
#     [578, 'mcg', 'Vitamin B-12, added'],

        self.amino_acids = [
            [501, 'g', 'Tryptophan', 0, 0],
            [502, 'g', 'Threonine', 0, 0],
            [503, 'g', 'Isoleucine', 0, 0],
            [504, 'g', 'Leucine', 0, 0],
            [505, 'g', 'Lysine', 0, 0],
            [506, 'g', 'Methionine', 0, 0],
            [507, 'g', 'Cystine', 0, 0],
            [508, 'g', 'Phenylalanine', 0, 0],
            [509, 'g', 'Tyrosine', 0, 0],
            [510, 'g', 'Valine', 0, 0],
            [511, 'g', 'Arginine', 0, 0],
            [512, 'g', 'Histidine', 0, 0],
            [513, 'g', 'Alanine', 0, 0],
            [514, 'g', 'Aspartic acid', 0, 0],
            [515, 'g', 'Glutamic acid', 0, 0],
            [516, 'g', 'Glycine', 0, 0],
            [517, 'g', 'Proline', 0, 0],
            [518, 'g', 'Serine', 0, 0]]
#     [454, 'mg', 'Betaine'],
#     [521, 'g', 'Hydroxyproline']]

        self.fats = [
            [606, 'g', 'Fatty acids, total saturated', 20, 60],
            [645, 'g', 'Fatty acids, total monounsaturated', 0, 0],
            [646, 'g', 'Fatty acids, total polyunsaturated', 0, 0],
            [605, 'g', 'Fatty acids, total trans', 0, 0],
            [601, 'mg', 'Cholesterol', 300, 900],
            [636, 'mg', 'Phytosterols', 0, 0],
            [618, 'g', '18:2 undifferentiated', 0, 0],
            [675, 'g', '18:2 n-6 c,c (linoleic acid)', 14, 70],
            [851, 'g', '18:3 n-3 c,c,c (alpha-linolenic acid, ALA)', 1.6, 8 ],
            [629, 'g', '20:5 n-3 (EPA)', 0, 0],
            [621, 'g', '22:6 n-3 (DHA)', 0, 0],
            [619, 'g', '18:3 undifferentiated', 0, 0],
            [620, 'g', '20:4 undifferentiated', 0, 0]
            ]
#     [607, 'g', '4:0'],
#     [608, 'g', '6:0'],
#     [609, 'g', '8:0'],
#     [610, 'g', '10:0'],
#     [611, 'g', '12:0'],
#     [612, 'g', '14:0'],
#     [613, 'g', '16:0'],
#     [614, 'g', '18:0'],
#     [615, 'g', '20:0'],
#     [617, 'g', '18:1 undifferentiated'],
#     [624, 'g', '22:0'],
#     [625, 'g', '14:1'],
#     [626, 'g', '16:1 undifferentiated'],
#     [627, 'g', '18:4'],
#     [628, 'g', '20:1'],
#     [630, 'g', '22:1 undifferentiated'],
#     [631, 'g', '22:5 n-3'],
#     [638, 'mg', 'Stigmasterol'],
#     [639, 'mg', 'Campesterol'],
#     [641, 'mg', 'Beta-sitosterol'],
#     [652, 'g', '15:0'],
#     [653, 'g', '17:0'],
#     [654, 'g', '24:0'],
#     [662, 'g', '16:1 t'],
#     [663, 'g', '18:1 t'],
#     [664, 'g', '22:1 t'],
#     [665, 'g', '18:2 t not further defined'],
#     [666, 'g', '18:2 i'],
#     [669, 'g', '18:2 t,t'],
#     [670, 'g', '18:2 CLAs'],
#     [671, 'g', '24:1 c'],
#     [672, 'g', '20:2 n-6 c,c'],
#     [673, 'g', '16:1 c'],
#     [674, 'g', '18:1 c'],
#     [676, 'g', '22:1 c'],
#     [685, 'g', '18:3 n-6 c,c,c'],
#     [687, 'g', '17:1'],
#     [689, 'g', '20:3 undifferentiated'],
#     [693, 'g', 'Fatty acids, total trans-monoenoic'],
#     [695, 'g', 'Fatty acids, total trans-polyenoic'],
#     [696, 'g', '13:0'],
#     [697, 'g', '15:1'],
#     [852, 'g', '20:3 n-3'],
#     [853, 'g', '20:3 n-6'],
#     [855, 'g', '20:4 n-6'],
#     [856, 'g', '18:3i'],
#     [857, 'g', '21:5'],
#     [858, 'g', '22:4']]

rdi_default = DefaultRdi()

tracked_nutrient = Tracked_Nutrients()

all_nutrient_ids = (203, 204, 205, 207, 208, 209, 210, 211, 212, 213, 214, 221, 255, 257, 262, 263, 268, 269, 287, 291, 301, 303, 304, 305, 306, 307, 309, 312, 313, 315, 317, 318, 319, 320, 321, 322, 323, 324, 334, 337, 338, 341, 342, 343, 401, 404, 405, 406, 410, 415, 417, 418, 421, 430, 431, 432, 435, 454, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 521, 573, 578, 601, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 617, 618, 619, 620, 621, 624, 625, 626, 627, 628, 629, 630, 631, 636, 638, 639, 641, 645, 646, 652, 653, 654, 662, 663, 664, 665, 666, 669, 670, 671, 672, 673, 674, 675, 676, 685, 687, 689, 693, 695, 696, 697, 851, 852, 853, 855, 856, 857, 858)

def create_nutrient_id_2_name_measure_dict():
    nutr_dict = {}
    for id, unit, name in tracked_nutrient.general:
        nutr_dict[id] = '%s (%s)' % (name, unit)
    for id, unit, name in tracked_nutrient.vitamins:
        nutr_dict[id] = '%s (%s)' % (name, unit)
    for id, unit, name in tracked_nutrient.minerals:
        nutr_dict[id] = '%s (%s)' % (name, unit)
    for id, unit, name in tracked_nutrient.amino_acids:
        nutr_dict[id] = '%s (%s)' % (name, unit)
    for id, unit, name in tracked_nutrient.fats:
        nutr_dict[id] = '%s (%s)' % (name, unit)
    return nutr_dict

tracked_nutrient_id_2_name_measure_dict = create_nutrient_id_2_name_measure_dict()
