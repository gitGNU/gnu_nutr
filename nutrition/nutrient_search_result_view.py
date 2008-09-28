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

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django import forms

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

def append_to_lists(nutr_id_list, factor_list, nutr, factor):
    if nutr and factor:
        try:
            int_nutr = int(nutr)
            float_factor = float(factor)
            nutr_id_list.append(int_nutr)
            factor_list.append(float_factor)
        except ValueError:
            pass
    return nutr_id_list, factor_list


@login_required
def nutrient_search_result(request, food_group=None, nutr1=None, fact1=None,
                           nutr2=None, fact2=None,
                           nutr3=None, fact3=None):
    group_ids = [g.group_id for g in get_food_groups()]
    if int(food_group) not in group_ids:
        raise Http404

    nutr_name = Nutrient_Name()
    score_query = ''
    select_query = ''
    group_by = ''

    max_dict = get_max_dict()
    rdi_dict = get_user_rdis_dict(request.user)

    nutr_id_list = []
    factor_list = []

    nutr_id_list, factor_list = append_to_lists(nutr_id_list, factor_list, nutr1, fact1)
    nutr_id_list, factor_list = append_to_lists(nutr_id_list, factor_list, nutr2, fact2)
    nutr_id_list, factor_list = append_to_lists(nutr_id_list, factor_list, nutr3, fact3)

    if not nutr_id_list or not food_group:
        return HttpResponseRedirect('/nutrient_search/')

    for i, nutr_id in enumerate(nutr_id_list):
        factor = factor_list[i]
        if nutr_id in rdi_dict and rdi_dict[nutr_id] != 0.0:
            factor /= rdi_dict[nutr_id]
        elif nutr_id in max_dict and max_dict[nutr_id] != 0.0:
            factor /= max_dict[nutr_id]
        else:
            # The nutr_id is not found in rdi_dict or max_dict. It's invalid.
            raise Http404
        if score_query != '':
            score_query += ' + '

        score_query += "(value_%d * %f)" % (nutr_id, factor)
        select_query += ", value_%d" % nutr_id
        group_by = group_by + ", value_%d " % nutr_id
        nutr_name.names.append(tracked_nutr_id_2_name_dict[nutr_id])
        nutr_name.names.append('% RDI')


    if food_group == '0':
        query = "select food_id, food_name, max(" + score_query + ") as score" + select_query + " from nutrition_nutrient_score group by food_id, food_name " + group_by + "order by score desc limit 200;"
    else:
        query = "select food_id, food_name, max(" + score_query + ") as score" + select_query + " from nutrition_nutrient_score where group_id = '" + food_group + "' group by food_id, food_name " + group_by + "order by score desc limit 200;"

    result = my_custom_sql(query)

    scores = []
    for row in result:
        food_id = row[0]
        name = row[1]
        score = row[2]
        values_list = []
        for i, nutr_id in enumerate(nutr_id_list):
            if nutr_id in rdi_dict and rdi_dict[nutr_id] != 0.0:
                percent_rdi = 100.0 * row[3 + i]/rdi_dict[nutr_id]
            else:
                percent_rdi = "-"
            values_list.append(Values(row[3 + i], percent_rdi))
        scores.append(Nutrient_Score(food_id, name, score, values_list))

    return render_to_response( 'nutrient_search_result.html',{
            "scores": scores,
            "nutr_name": nutr_name
            })
