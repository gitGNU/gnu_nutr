#!/usr/bin/env python

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

import commands
import sys

import settings
from nutrition.constants import *

from psycopg2 import *

conn = connect("dbname=" + settings.DATABASE_NAME + \
                   " user=" + settings.DATABASE_USER + \
                   " password=" + settings.DATABASE_PASSWORD)
curs = conn.cursor()

def run_psql_command(cmd):
    print cmd
    curs.execute(cmd)
    conn.commit()

def set_nutrients_to_zero():
    nutr_dict = {}
    for nutr_id, unit, name in tracked_nutrient.general:
        nutr_dict[nutr_id] = 0.0
    for nutr_id, unit, name in tracked_nutrient.vitamins:
        nutr_dict[nutr_id] = 0.0
    for nutr_id, unit, name in tracked_nutrient.minerals:
        nutr_dict[nutr_id] = 0.0
    for nutr_id, unit, name in tracked_nutrient.amino_acids:
        nutr_dict[nutr_id] = 0.0
    for nutr_id, unit, name in tracked_nutrient.fats:
        nutr_dict[nutr_id] = 0.0
    return nutr_dict

def get_default_rdi():
    nutr_dict = {}
    for nutr_id, unit, name, min, max in rdi_default.general:
        nutr_dict[nutr_id] = min
    for nutr_id, unit, name, min, max in rdi_default.vitamins:
        nutr_dict[nutr_id] = min
    for nutr_id, unit, name, min, max in rdi_default.minerals:
        nutr_dict[nutr_id] = min
    for nutr_id, unit, name, min, max in rdi_default.amino_acids:
        nutr_dict[nutr_id] = min
    for nutr_id, unit, name, min, max in rdi_default.fats:
        nutr_dict[nutr_id] = min
    return nutr_dict

def insert_table_max_avg_per_200():
    avg_dict = {}
    curs.execute('truncate table nutrition_nutrient_score_max cascade')
    conn.commit()
    curs.execute("select nutrient_id from nutrition_nutrient_definition")
    result = curs.fetchall()
    for (id,) in result:
        curs.execute("select nutrient_id, avg(val_per_200), max(val_per_200) from nutrition_per_200 where nutrient_id = '%d' group by nutrient_id" % id)
        food_id, avg, max = curs.fetchone()
        curs.execute("insert into nutrition_nutrient_score_max values ( '%d', '%f', '%f')" % \
                         (food_id, avg, max))
        conn.commit()


def run():
    curs.execute('truncate table nutrition_nutrient_score cascade')
 #    try:
#         curs.execute('drop table nutrition_per_200')
#         conn.commit()
#     except:
#         pass
    try:
        curs.execute('drop table temp')
        conn.commit()
    except:
        pass

    # python seems to complain about this, but I can run it fine from within psql.

    # create table of nutrient data per 200 calories, rather than per 100 g
#    curs.execute("create table nutrition_per_200 as select a.food_id, a.nutrient_id, 200.0*(a.value/b.value) as val_per_200 from nutrition_nutrient_data a, nutrition_nutrient_data b where a.food_id = b.food_id and b.nutrient_id='208' and b.value <> 0;")
    conn.commit()
    curs.execute("create table temp as select distinct food_id from nutrition_per_200")
    conn.commit()
    curs.execute('select food_id from temp')
    result = curs.fetchall()
    # create table of de-normalized data
    for r in result:
        food_id = r[0]
        curs.execute("select * from nutrition_per_200 where food_id = '%s'" % food_id)
        all_nutrients_for_food = curs.fetchall()
        nutr_dict = set_nutrients_to_zero()
        for food_id, nutr_id, value_per_200 in all_nutrients_for_food:
            nutr_dict[nutr_id] = value_per_200
            text = "insert into nutrition_nutrient_score values ( '%d', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f')" % \
                         (food_id,
                          nutr_dict[203],
                          nutr_dict[204],
                          nutr_dict[205],
                          nutr_dict[291],
                          nutr_dict[209],
                          nutr_dict[269],
                          nutr_dict[221],
                          nutr_dict[255],
                          nutr_dict[262],
                          nutr_dict[301],
                          nutr_dict[303],
                          nutr_dict[304],
                          nutr_dict[305],
                          nutr_dict[306],
                          nutr_dict[307],
                          nutr_dict[309],
                          nutr_dict[312],
                          nutr_dict[315],
                          nutr_dict[317],
                          nutr_dict[318],
                          nutr_dict[319],
                          nutr_dict[321],
                          nutr_dict[322],
                          nutr_dict[334],
                          nutr_dict[337],
                          nutr_dict[338],
                          nutr_dict[404],
                          nutr_dict[405],
                          nutr_dict[406],
                          nutr_dict[410],
                          nutr_dict[415],
                          nutr_dict[417],
                          nutr_dict[418],
                          nutr_dict[401],
                          nutr_dict[324],
                          nutr_dict[323],
                          nutr_dict[341],
                          nutr_dict[342],
                          nutr_dict[343],
                          nutr_dict[430],
                          nutr_dict[501],
                          nutr_dict[502],
                          nutr_dict[503],
                          nutr_dict[504],
                          nutr_dict[505],
                          nutr_dict[506],
                          nutr_dict[507],
                          nutr_dict[508],
                          nutr_dict[509],
                          nutr_dict[510],
                          nutr_dict[511],
                          nutr_dict[512],
                          nutr_dict[513],
                          nutr_dict[514],
                          nutr_dict[515],
                          nutr_dict[516],
                          nutr_dict[517],
                          nutr_dict[518],
                          nutr_dict[606],
                          nutr_dict[645],
                          nutr_dict[646],
                          nutr_dict[605],
                          nutr_dict[601],
                          nutr_dict[636],
                          nutr_dict[618],
                          nutr_dict[675],
                          nutr_dict[851],
                          nutr_dict[629],
                          nutr_dict[621],
                          nutr_dict[619],
                          nutr_dict[620])
        curs.execute(text)
        conn.commit()
    curs.execute('drop table temp')
    conn.commit()

if __name__== "__main__":
#    run()
    insert_table_max_avg_per_200()
