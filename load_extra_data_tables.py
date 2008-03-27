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

def run_psql_command( cmd):
    run_cmd = 'psql -d ' + settings.DATABASE_NAME +\
        ' -U ' + settings.DATABASE_USER +\
        ' -c "' + cmd + '"'
    print run_cmd
    (status, output) = commands.getstatusoutput(run_cmd)
    print 'status = %d' % status
    print "output = %s" % output
    if status != 0:
        sys.exit(0)

def psql_truncate_table( table_name):
    run_psql_command( 'TRUNCATE TABLE ' + table_name + ';')

def psql_drop_table( table_name):
    run_psql_command( 'DROP TABLE ' + table_name + ';')

def psql_copy( input_file, table_name):
    run_psql_command( '\COPY ' + table_name + ' FROM \'' + input_file +
                      '\' WITH DELIMITER \'^\' NULL AS \'\'')

def load_recipe_category( file):
    psql_copy(  file , 'nutrition_recipe_category')

if __name__== "__main__":
    if len( sys.argv) == 2:
        load_recipe_category( sys.argv[1])
    else:
        print "Usage: " + sys.argv[0] + " <full/path/to/file>"
