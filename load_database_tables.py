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
from psycopg2 import *

conn = connect("dbname=" + settings.DATABASE_NAME + \
                   " user=" + settings.DATABASE_USER + \
                   " password=" + settings.DATABASE_PASSWORD)
curs = conn.cursor()

# def run_psql_command(cmd):
#     run_cmd = 'psql -d ' + settings.DATABASE_NAME +\
#         ' -U ' + settings.DATABASE_USER +\
#         ' -c "' + cmd + '"'
#     print run_cmd
#     (status, output) = commands.getstatusoutput(run_cmd)
#     print 'status = %d' % status
#     print "output = %s" % output
#     if status != 0:
#         sys.exit(0)

def run_psql_command(cmd):
    print cmd
    curs.execute(cmd)
    conn.commit()

def psql_truncate_table(table_name):
    run_psql_command('TRUNCATE TABLE ' + table_name + ';')

def psql_drop_table(table_name):
    run_psql_command('DROP TABLE ' + table_name + ';')

def psql_copy(input_file, table_name):
    run_psql_command('\COPY ' + table_name + ' FROM \'' + input_file +
                     '\' WITH DELIMITER \'^\' NULL AS \'\'')

def load_food_group(file):
    f_in = open(file, 'r')
    f_out = open(file + '_out', 'w')
    for line in f_in:
        s = line.replace('~', '')
        f_out.write(s)
    f_in.close()
    f_out.close()
    psql_copy(file + '_out', 'nutrition_food_group')
    run_psql_command('INSERT into nutrition_food_group (group_id, name) VALUES (\'0\', \'All\')')

def load_food(file):
    f_in = open(file, 'r')
    f_out = open(file + '_out', 'w')
    for line in f_in:
        (food_id, group_id, name, dummy1) = line.replace('~', '').split('^', 3)
        if name != '':
            f_out.write('%s^%s^%s\r\n' % (food_id, group_id, name))
    f_in.close()
    f_out.close()
    psql_copy(file + '_out', 'nutrition_food')

def load_nutrient_definition(file):
    f_in = open(file, 'r')
    f_out = open(file + '_out', 'w')
    for line in f_in:
        (nutrient_id, unit_of_measure, dummy1, name, dummy2) = \
            line.replace('~', '').split('^', 4)
        f_out.write('%s^%s^%s\r\n' % (nutrient_id, unit_of_measure, name))
    f_in.close()
    f_out.close()
    psql_copy(file + '_out', 'nutrition_nutrient_definition')

def load_nutrient_data(file):
    f_in = open(file, 'r')
    f_out = open(file + '_out', 'w')
    for line in f_in:
        (food_id, nutrient_id, value, dummy1) = line.replace('~', '').split('^', 3)
        n = (1000 * int(food_id)) + int(nutrient_id)
        f_out.write('%d^%s^%s^%s\r\n' % (n, food_id, nutrient_id, value))
    f_in.close()
    f_out.close()
    psql_copy( file + '_out', 'nutrition_nutrient_data')

def load_measure(file):
    f_in = open(file, 'r')
    f_out = open(file + '_out', 'w')
    for line in f_in:
        (food_id, measure_id, amount, name, grams, dummy1) = \
            line.replace('~', '').split('^', 5)
        n = (100 * int(food_id) + int(measure_id))
        if amount != '':
            f_out.write('%d^%s^%s^%s^%s^%s\r\n' %
                         (n, food_id, measure_id, amount, name, grams))
    f_in.close()
    f_out.close()
    psql_copy(file + '_out', 'nutrition_measure')
    run_psql_command('INSERT into nutrition_measure SELECT (100 * foods.food_id) AS id, foods.food_id, 0 AS measure_id, 1 AS amount, \'gm\' AS name, 1.0 AS grams FROM (SELECT DISTINCT(food_id) FROM nutrition_measure) AS foods;')

def truncate_all_tables():
    psql_truncate_table('nutrition_food cascade')
    psql_truncate_table('nutrition_food_group cascade')
    psql_truncate_table('nutrition_nutrient_data cascade')
    psql_truncate_table('nutrition_nutrient_definition cascade')
    psql_truncate_table('nutrition_measure cascade')

def drop_all_tables():
    psql_drop_table('nutrition_food')
    psql_drop_table('nutrition_food_group')
    psql_drop_table('nutrition_nutrient_data')
    psql_drop_table('nutrition_nutrient_definition')
    psql_drop_table('nutrition_measure')

def load_all_tables(directory):
    load_food_group(directory + '/FD_GROUP.txt')
    load_food(directory + '/FOOD_DES.txt')
    load_nutrient_definition(directory + '/NUTR_DEF.txt')
    load_nutrient_data(directory + '/NUT_DATA.txt')
    load_measure(directory + '/WEIGHT.txt')

if __name__== "__main__":
    if len(sys.argv) == 2:
        truncate_all_tables()
        load_all_tables(sys.argv[1])
    else:
        print "Usage: " + sys.argv[0] + " <directory>"
