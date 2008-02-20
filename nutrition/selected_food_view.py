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
        measures = kwargs['measure']
        del kwargs['measure']
        super(FoodSelectForm, self).__init__(*args, **kwargs)
        self.fields['measure'].choices = [(c.id, '%g %s' % (c.amount, c.name)) for c in measures]

@login_required
def selected_food( request, food_id):
    name = food_id_2_name( int( food_id))
    measures_list = get_measures(food_id)

    if request.method == 'GET':
        form = FoodSelectForm(request.GET, measure=measures_list)
    else:
        form = FoodSelectForm(measure=measures_list)

    if form.is_valid():
        amount = float(form.cleaned_data['amount'])
        measure = int(form.cleaned_data['measure'])
    else:
        amount = 0.0
        measure = measures_list[0].id

    nutrients = get_food_nutrient_data( int( food_id), amount, measure, request.user)
    return render_to_response( 'selected_food.html', {
            "name": name,
            "nutrients": nutrients,
            "form": form})
