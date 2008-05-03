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

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django import newforms as forms

from models import *
from constants import tracked_nutr_id_2_name_dict

def get_nutrient_search_data_from_session(session):
    data = {}
    for key, val in session['nutrient_search'].items():
        data[key] = val
    return data

class Nutrient_Name:
    def __init__(self):
        self.names = []

class Values:
    def __init__(self, value, percent_rdi):
        self.value = value
        self.percent_rdi = percent_rdi

class Nutrient_Score:
    def __init__(self, food_id, name, score, values_list):
        self.food_id = food_id
        self.name = name
        self.values_list = values_list
        self.score = score

@login_required
def nutrient_search_result(request):
    data = get_nutrient_search_data_from_session(request.session)
    food_group = data['food_group']
    nutr_name = Nutrient_Name()
    score_query = ''
    select_query = ''
    group_by = ''

    max_dict = get_max_dict()
    rdi_dict = get_user_rdis_dict(request.user)

    nutr_id_list = []
    for str in ['1', '2', '3', '4', '5', '6']:
        if data['nutrient_%s' % str] != '-1':
            nutr_id = data['nutrient_%s' % str]
            int_nutr_id = int(nutr_id)
            nutr_id_list.append(int_nutr_id)
            scaling_factor = float(data['factor_%s' % str])
            if int_nutr_id in rdi_dict and rdi_dict[int_nutr_id] != 0.0:
                scaling_factor /= rdi_dict[int_nutr_id]
            elif int_nutr_id in max_dict and max_dict[int_nutr_id] != 0.0:
                scaling_factor /= max_dict[int_nutr_id]
            if score_query != '':
                score_query += ' + '

            score_query += "(value_%s * %f)" % (nutr_id, scaling_factor)
            select_query += ", value_%s" % nutr_id
            group_by = group_by + ", value_%s " % nutr_id
            nutr_name.names.append(tracked_nutr_id_2_name_dict[int_nutr_id])
            nutr_name.names.append('% RDI')

    if food_group == '0':
        query = "select food_id, food_name, max(" + score_query + ") as score" + select_query + " from nutrition_nutrient_score group by food_id, food_name " + group_by + "order by score desc limit 200;"
    else:
        query = "select food_id, food_name, max(" + score_query + ") as score" + select_query + " from nutrition_nutrient_score where group_id = '" + food_group + "' group by food_id, food_name " + group_by + "order by score desc limit 200;"

    print 'query = ', query
    result = my_custom_sql(query)

    print 'result = ', result
    base_path = request.get_full_path()
    print 'base_path = ', base_path

    scores = []
    for row in result:
        food_id = row[0]
        name = row[1]
        score = row[2]
        values_list = []
        for i in range(0, len(nutr_id_list)):
            nutr_id = nutr_id_list[i]
            if nutr_id in rdi_dict and rdi_dict[nutr_id] != 0.0:
                percent_rdi = 100.0 * row[3 + i]/rdi_dict[nutr_id]
            else:
                percent_rdi = "-"
            values_list.append(Values(row[3 + i], percent_rdi))
        scores.append(Nutrient_Score(food_id, name, score, values_list))

    print 'scores = ', scores

    return render_to_response( 'nutrient_search_result.html',{
            "scores": scores,
            "nutr_name": nutr_name
            })
