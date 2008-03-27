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
from django import newforms as forms

from models import *

class RdiForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'readonly':''}))
    min = forms.DecimalField(required=True)
    max = forms.DecimalField(required=True)
    unit_of_measure = forms.CharField(widget=forms.TextInput(attrs={'readonly':''}))

class Nutrient_Category:
    pass

def set_rdi_form_elements(rdi_list):
    rdi_dict = {}
    for r in rdi_list:
        rdi_dict[r.nutrient_id] = (r.min_nutrient_value, r.max_nutrient_value)
    nutrient_category = Nutrient_Category()
    nutrient_category.general = []
    for nutr_id, unit, desc in tracked_nutrient.general:
        form_data = {'%s-name' % nutr_id: desc,
                     '%s-min' % nutr_id: rdi_dict[nutr_id][0],
                     '%s-max' % nutr_id: rdi_dict[nutr_id][1],
                     '%s-unit_of_measure' % nutr_id: unit}
        nutrient_category.general.append(RdiForm(form_data, prefix='%s' % nutr_id))
    nutrient_category.minerals = []
    for nutr_id, unit, desc in tracked_nutrient.minerals:
        form_data = {'%s-name' % nutr_id: desc,
                     '%s-min' % nutr_id: rdi_dict[nutr_id][0],
                     '%s-max' % nutr_id: rdi_dict[nutr_id][1],
                     '%s-unit_of_measure' % nutr_id: unit}
        nutrient_category.minerals.append(RdiForm(form_data, prefix='%s' % nutr_id))
    nutrient_category.vitamins = []
    for nutr_id, unit, desc in tracked_nutrient.vitamins:
        form_data = {'%s-name' % nutr_id: desc,
                     '%s-min' % nutr_id: rdi_dict[nutr_id][0],
                     '%s-max' % nutr_id: rdi_dict[nutr_id][1],
                     '%s-unit_of_measure' % nutr_id: unit}
        nutrient_category.vitamins.append(RdiForm(form_data, prefix='%s' % nutr_id))
    nutrient_category.amino_acids = []
    for nutr_id, unit, desc in tracked_nutrient.amino_acids:
        form_data = {'%s-name' % nutr_id: desc,
                     '%s-min' % nutr_id: rdi_dict[nutr_id][0],
                     '%s-max' % nutr_id: rdi_dict[nutr_id][1],
                     '%s-unit_of_measure' % nutr_id: unit}
        nutrient_category.amino_acids.append(RdiForm(form_data, prefix='%s' % nutr_id))
    nutrient_category.fats = []
    for nutr_id, unit, desc in tracked_nutrient.fats:
        form_data = {'%s-name' % nutr_id: desc,
                     '%s-min' % nutr_id: rdi_dict[nutr_id][0],
                     '%s-max' % nutr_id: rdi_dict[nutr_id][1],
                     '%s-unit_of_measure' % nutr_id: unit}
        nutrient_category.fats.append(RdiForm(form_data, prefix='%s' % nutr_id))
    return nutrient_category

def load_post_data_to_form(data):
    nutrient_category = Nutrient_Category()
    nutrient_category.general = []
    for nutr_id, unit, desc in tracked_nutrient.general:
        form_data = {'%s-name' % nutr_id: desc,
                     '%s-min' % nutr_id: data['%s-min' % nutr_id],
                     '%s-max' % nutr_id: data['%s-max' % nutr_id],
                     '%s-unit_of_measure' % nutr_id: unit}
        nutrient_category.general.append(RdiForm(form_data, prefix='%s' % nutr_id))
    nutrient_category.minerals = []
    for nutr_id, unit, desc in tracked_nutrient.minerals:
        form_data = {'%s-name' % nutr_id: desc,
                     '%s-min' % nutr_id: data['%s-min' % nutr_id],
                     '%s-max' % nutr_id: data['%s-max' % nutr_id],
                     '%s-unit_of_measure' % nutr_id: unit}
        nutrient_category.minerals.append(RdiForm(form_data, prefix='%s' % nutr_id))
    nutrient_category.vitamins = []
    for nutr_id, unit, desc in tracked_nutrient.vitamins:
        form_data = {'%s-name' % nutr_id: desc,
                     '%s-min' % nutr_id: data['%s-min' % nutr_id],
                     '%s-max' % nutr_id: data['%s-max' % nutr_id],
                     '%s-unit_of_measure' % nutr_id: unit}
        nutrient_category.vitamins.append(RdiForm(form_data, prefix='%s' % nutr_id))
    nutrient_category.amino_acids = []
    for nutr_id, unit, desc in tracked_nutrient.amino_acids:
        form_data = {'%s-name' % nutr_id: desc,
                     '%s-min' % nutr_id: data['%s-min' % nutr_id],
                     '%s-max' % nutr_id: data['%s-max' % nutr_id],
                     '%s-unit_of_measure' % nutr_id: unit}
        nutrient_category.amino_acids.append(RdiForm(form_data, prefix='%s' % nutr_id))
    nutrient_category.fats = []
    for nutr_id, unit, desc in tracked_nutrient.fats:
        form_data = {'%s-name' % nutr_id: desc,
                     '%s-min' % nutr_id: data['%s-min' % nutr_id],
                     '%s-max' % nutr_id: data['%s-max' % nutr_id],
                     '%s-unit_of_measure' % nutr_id: unit}
        nutrient_category.fats.append(RdiForm(form_data, prefix='%s' % nutr_id))
    return nutrient_category


def all_is_valid(nutrients):
    for n in nutrients.general:
        if not n.is_valid():
            return False
    for n in nutrients.vitamins:
        if not n.is_valid():
            return False
    for n in nutrients.minerals:
        if not n.is_valid():
            return False
    for n in nutrients.amino_acids:
        if not n.is_valid():
            return False
    for n in nutrients.fats:
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
        rdi_list = get_user_rdis(request.user.id)
        if not rdi_list:
            rdi_list = get_default_rdi()
        nutrients = set_rdi_form_elements(rdi_list)

    return render_to_response( 'set_rdi.html',{
            "nutrients":nutrients
            })
