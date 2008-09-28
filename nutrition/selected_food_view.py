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

class FoodSelectForm(forms.Form):
    num_measures = forms.DecimalField(required=True)
    measure = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        measures = kwargs['measure_choices']
        del kwargs['measure_choices']
        super(FoodSelectForm, self).__init__(*args, **kwargs)
        self.fields['measure'].choices = [(c.measure_id, c.measure_name) for c in measures]

@login_required
def selected_food( request, food_id, measure=None, num_measures=None):
    food_name = food_id_2_name(int(food_id))
    measures_list = get_measures(food_id)
    if not food_name or not measures_list:
        raise Http404

    if measure:
        measure_ids = [m.measure_id for m in measures_list]
        if int(measure) not in measure_ids:
            raise Http404

    if request.method == 'GET':
        if request.GET:
            form = FoodSelectForm(request.GET, measure_choices=measures_list)
        else:
            if measure:
                if not num_measures:
                    num_measures = 1.0
                form_data = {'num_measures': num_measures, 'measure': measure}
                form = FoodSelectForm(form_data, measure_choices=measures_list)
            else:
                form_data = {'num_measures': 1.0, 'measure': measures_list[0].measure_id}
                form = FoodSelectForm(form_data, measure_choices=measures_list)
    else:
        if measure:
            if not num_measures:
                num_measures = 1.0
            form_data = {'num_measures': num_measures, 'measure': measure}
            form = FoodSelectForm(form_data, measure_choices=measures_list)
        else:
            form_data = {'num_measures': 1.0, 'measure': measures_list[0].measure_id}
            form = FoodSelectForm(form_data, measure_choices=measures_list)

    if form.is_valid():
        num_measures = float(form.cleaned_data['num_measures'])
        measure_id = int(form.cleaned_data['measure'])
    else:
        num_measures = 0.0
        measure_id = measures_list[0].measure_id

    nutrients = get_food_nutrient_data(int(food_id), num_measures, measure_id, request.user)

    return render_to_response( 'selected_food.html', {
            "food_name": food_name,
            "food_id": food_id,
            "nutrients": nutrients,
            "form": form})
