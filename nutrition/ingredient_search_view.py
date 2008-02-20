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

class IngredientSearchForm(forms.Form):
    food_search_str = forms.CharField(required=False)
    food_group = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(IngredientSearchForm, self).__init__(*args, **kwargs)
        self.fields['food_group'].choices = \
            [(c.group_id, c.name) for c in get_food_groups()]

@login_required
def add_ingredient(request):
    if request.GET:
        form = IngredientSearchForm(request.GET)
        if form.is_valid():
            food_search_str = form.cleaned_data['food_search_str']
            food_group = int(form.cleaned_data['food_group'])
            if food_search_str == '':
                food_list = []
            else:
                food_list = get_food_from_food_str(food_search_str, food_group)
        else:
            food_list = []
    else:
        form = IngredientSearchForm()
        food_list = []

    return render_to_response( 'add_ingredient.html',{
            'form': form,
            'food_list': food_list})
