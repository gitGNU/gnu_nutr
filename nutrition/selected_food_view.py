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

class FoodSelectForm(forms.Form):
    amount = forms.DecimalField(required=True)
    measure = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        measures = kwargs['measure_choices']
        del kwargs['measure_choices']
        super(FoodSelectForm, self).__init__(*args, **kwargs)
        self.fields['measure'].choices = [(c.id, '%g %s' % (c.amount, c.name)) for c in measures]

@login_required
def selected_food( request, food_id, measure=None, amount=None):
    name = food_id_2_name( int( food_id))
    measures_list = get_measures(food_id)

    if request.method == 'GET':
        if request.GET:
            form = FoodSelectForm(request.GET, measure_choices=measures_list)
        else:
            if measure and amount:
                form_data = {'amount': amount, 'measure': measure}
                form = FoodSelectForm(form_data, measure_choices=measures_list)
    else:
        if measure and amount:
            form_data = {'amount': amount, 'measure': measure}
            form = FoodSelectForm(form_data, measure_choices=measures_list)
        else:
            form = FoodSelectForm(measure_choices=measures_list)
    if form.is_valid():
        amount_data = float(form.cleaned_data['amount'])
        measure_data = int(form.cleaned_data['measure'])
    else:
        amount_data = 0.0
        measure_data = measures_list[0].id

    nutrients = get_food_nutrient_data(int(food_id), amount_data, measure_data, request.user)
    return render_to_response( 'selected_food.html', {
            "name": name,
            "nutrients": nutrients,
            "form": form})
