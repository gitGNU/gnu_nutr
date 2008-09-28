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

class RecipeSearchForm(forms.Form):
    text = forms.CharField(max_length=60)
    category = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(RecipeSearchForm, self).__init__(*args, **kwargs)
        self.fields['category'].choices = [(c.category_id, c.category_name)
                                           for c in get_recipe_categories()]

class RecipeDelete(forms.Form):
    check = forms.BooleanField(required=False)

@login_required
def search_recipe(request):
    data = request.POST.copy()
    if data.has_key('text'):
        first_show = False
    else:
        first_show = True

    recipe_search_form = RecipeSearchForm(request.POST)
    check_recipe_list = []
    text = ''

    if data.has_key('delete'):
        for key, value in data.items():
            if key.find('check') != -1 and value == 'on':
                recipe_id = key[:-6]
                delete_recipe_owned_by_user(request.user, recipe_id)

    if recipe_search_form.is_valid():
        text = recipe_search_form.cleaned_data['text']
        category = int(recipe_search_form.cleaned_data['category'])
        recipes = get_recipes_matching(text, category)
        # TODO: only have check boxes against recipes owned by user
        own_recipes = filter_recipes_owned_by_user(request.user, recipes)
        check_recipe_list = []
        for r in recipes:
            form_data = {'%s_check' % r.recipe_id : False}
            recipe_delete_form = RecipeDelete(form_data, prefix=r.recipe_id)
            recipe_delete_form.recipe_id = r.recipe_id
            recipe_delete_form.recipe_name = r.recipe_name
            recipe_delete_form.username = request.user.username
            check_recipe_list.append(recipe_delete_form)


    return render_to_response( 'search_recipe.html', {
            "form": recipe_search_form,
            "first_show": first_show,
            "text": text,
            "recipes": check_recipe_list
            })
