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

class IngredientSearchForm(forms.Form):
    text = forms.CharField(required=False)
    food_group = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(IngredientSearchForm, self).__init__(*args, **kwargs)
        self.fields['food_group'].choices = \
            [(c.group_id, c.group_name) for c in get_food_groups()]

@login_required
def add_ingredient(request, recipe_id=None):
    if recipe_id and not get_recipe(recipe_id):
        raise Http404

    data = request.GET.copy()
    if data.has_key('text'):
        first_show = False
    else:
        first_show = True
    form = IngredientSearchForm(data)
    if form.is_valid():
        search_text = form.cleaned_data['text']
        food_group = int(form.cleaned_data['food_group'])
        food_list = get_food_from_food_str(search_text, food_group)
    else:
        search_text = ""
        food_list = []

    return render_to_response("add_ingredient.html", {
            "search_text": search_text,
            "first_show": first_show,
            "form": form,
            "recipe_id": recipe_id,
            "food_list": food_list})
