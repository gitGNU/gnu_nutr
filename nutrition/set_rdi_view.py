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
from constants import tracked_nutrient
from django import forms

from models import *

class RdiForm(forms.Form):
    min = forms.DecimalField(required=True)
    max = forms.DecimalField(required=True)

def set_rdi_form(nutr_id, rdi_dict, desc, unit):
    form_data = {'%s-min' % nutr_id: rdi_dict[nutr_id][0],
                 '%s-max' % nutr_id: rdi_dict[nutr_id][1]}
    rdi_form = RdiForm(form_data, prefix='%s' % nutr_id)
    rdi_form.name = desc
    rdi_form.unit_of_measure = unit
    return rdi_form

def set_rdi_form_from_data(nutr_id, data, desc, unit):
    form_data = {'%s-min' % nutr_id: data['%s-min' % nutr_id],
                 '%s-max' % nutr_id: data['%s-max' % nutr_id]}
    rdi_form = RdiForm(form_data, prefix='%s' % nutr_id)
    rdi_form.name = desc
    rdi_form.unit_of_measure = unit
    return rdi_form

class Nutrient_Category:
    pass

def set_rdi_form_elements(rdi_list):
    rdi_dict = {}
    for r in rdi_list:
        rdi_dict[r.nutrient_id] = (r.min_nutrient_value, r.max_nutrient_value)
    nutrient_category = {}
    nutr_groups = ['general', 'vitamins', 'minerals', 'amino_acids', 'fats']
    for group in nutr_groups:
        nutrient_category[group] = []
        for nutr_id, unit, desc, min_val, max_val in tracked_nutrient[group]:
            rdi_form = set_rdi_form(nutr_id, rdi_dict, desc, unit)
            nutrient_category[group].append(rdi_form)
    return nutrient_category

def load_post_data_to_form(data):
    nutrient_category = Nutrient_Category()
    nutrient_category.general = []
    nutrient_category = {}
    nutr_groups = ['general', 'vitamins', 'minerals', 'amino_acids', 'fats']
    for group in nutr_groups:
        nutrient_category[group] = []
        for nutr_id, unit, desc, min_val, max_val in tracked_nutrient[group]:
            rdi_form = set_rdi_form_from_data(nutr_id, data, desc, unit)
            nutrient_category[group].append(rdi_form)
    return nutrient_category


def all_is_valid(nutrients):
    nutr_groups = ['general', 'vitamins', 'minerals', 'amino_acids', 'fats']
    for group in nutr_groups:
        for n in nutrients[group]:
            if not n.is_valid():
                return False
    return True

@login_required
def set_rdi(request):
    if request.POST:
        data = request.POST.copy()
        nutrients = load_post_data_to_form(data)
        if data.has_key('save'):
            if all_is_valid(nutrients):
                save_rdi_to_database(request.user, nutrients)
    else:
        rdi_list = get_user_rdis(request.user)
        if not rdi_list:
            rdi_list = get_default_rdi()
        nutrients = set_rdi_form_elements(rdi_list)

    return render_to_response( 'set_rdi.html',{
            "nutrients": nutrients
            })
