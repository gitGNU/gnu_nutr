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
from django import forms

from models import *

from constants import tracked_nutrient


def get_nutrient_choices():
    choices = [(-1, '')]
    nutr_groups = ['general', 'vitamins', 'minerals', 'amino_acids', 'fats']
    for group in nutr_groups:
        for nutr_id, unit_of_measure, nutr_desc, min_val, max_val in tracked_nutrient[group]:
            choices.append((nutr_id, nutr_desc))
    return choices

def get_factor_choices():
    return [(5, '5'), (4, '4'), (3, '3'), (2, '2'), (1, '1'), (0, ''), (-1, '-1'), (-2, '-2'), (-3, '-3'), (-4, '-4'), (-5, '-5')]


class NutrientSearchForm(forms.Form):
    food_group = forms.ChoiceField()
    nutrient_1 = forms.ChoiceField()
    factor_1 = forms.ChoiceField()
    nutrient_2 = forms.ChoiceField()
    factor_2 = forms.ChoiceField()
    nutrient_3 = forms.ChoiceField()
    factor_3 = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(NutrientSearchForm, self).__init__(*args, **kwargs)
        self.fields['food_group'].choices = \
            [(c.group_id, c.group_name) for c in get_food_groups()]
        nutr_choices = get_nutrient_choices()
        factor_choices = get_factor_choices()
        self.fields['nutrient_1'].choices = \
            [(c[0], c[1]) for c in nutr_choices]
        self.fields['nutrient_2'].choices = \
            [(c[0], c[1]) for c in nutr_choices]
        self.fields['nutrient_3'].choices = \
            [(c[0], c[1]) for c in nutr_choices]
        self.fields['factor_1'].choices = \
            [(c[0], c[1]) for c in factor_choices]
        self.fields['factor_2'].choices = \
            [(c[0], c[1]) for c in factor_choices]
        self.fields['factor_3'].choices = \
            [(c[0], c[1]) for c in factor_choices]

class FormErrors:
    def __init__(self):
        self.factor_1 = False
        self.nutrient_1 = False
        self.factor_2 = False
        self.nutrient_2 = False
        self.factor_3 = False
        self.nutrient_3 = False

def validate(data):
    errors = FormErrors()
    has_errors = False
    if data['nutrient_1'] != '-1' and data['factor_1'] == '0':
        errors.factor_1 = True
        has_errors = True
    if data['nutrient_1'] == '-1' and data['factor_1'] != '0':
        errors.nutrient_1 = True
        has_errors = True
    if data['nutrient_2'] != '-1' and data['factor_2'] == '0':
        errors.factor_2 = True
        has_errors = True
    if data['nutrient_2'] == '-1' and data['factor_2'] != '0':
        errors.nutrient_2 = True
        has_errors = True
    if data['nutrient_3'] != '-1' and data['factor_3'] == '0':
        errors.factor_3 = True
        has_errors = True
    if data['nutrient_3'] == '-1' and data['factor_3'] != '0':
        errors.nutrient_3 = True
        has_errors = True
    if not has_errors:
        if data['factor_1'] == '0' and data['factor_2'] == '0' \
                and data['factor_3'] == '0':
            errors.nutrient_1 = True
            errors.factor_1 = True
            has_errors = True
    return has_errors, errors

def save_nutrient_search_data_to_session(session, data):
    session['nutrient_search'] = {}
    for key, val in data.items():
        session['nutrient_search'][key] = val

@login_required
def nutrient_search(request):
    if request.GET:
        data = request.GET.copy()
        form = NutrientSearchForm(data)
        if data.has_key('search'):
            has_errors, errors = validate(data)
            if not has_errors:
                url = "%s/" % data['food_group']
                if data['nutrient_1'] != '-1':
                    url += "%s/%s/" % (data['nutrient_1'], data['factor_1'])
                if data['nutrient_2'] != '-1':
                    url += "%s/%s/" % (data['nutrient_2'], data['factor_2'])
                if data['nutrient_3'] != '-1':
                    url += "%s/%s/" % (data['nutrient_3'], data['factor_3'])
                save_nutrient_search_data_to_session(request.session, data)
                return HttpResponseRedirect( "/nutrient_search_result/%s" % url)

    else:
        form = NutrientSearchForm({'factor_1':0, 'factor_2':0, 'factor_3':0})
        errors = FormErrors()
    return render_to_response( 'nutrient_search.html',{
            'form': form,
            'errors':errors})
