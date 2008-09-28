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

class RecipeData:
    def __init__(self, id, name, category, number_servings):
        self.id = id
        self.name = name
        self.category = category
        self.number_servings = number_servings

class IngredientData:
    def __init__(self, food_id, food_name, number_measures, measure_name, measure_id):
        self.food_id = food_id
        self.food_name = food_name
        self.number_measures = number_measures
        self.measure_name = measure_name
        self.measure_id = measure_id

@login_required
def selected_recipe(request, recipe_id):
    r = get_recipe(recipe_id)
    if not r:
        raise Http404
    recipe = RecipeData(recipe_id, r.recipe_name, r.category_name,
                        r.number_servings)
    ingredients = get_ingredients(recipe_id)
    ingredient_list = []
    for i in ingredients:
        ingredient_list.append(IngredientData(i.food_id, i.food_name, i.number_measures, i.measure_name, i.measure_id))
    nutrient_vals = get_recipe_nutrient_data(recipe_id)
    nutr_dict = {}
    for n in nutrient_vals:
        nutr_dict[n.nutrient_id] = n.value
    rdi_dict = set_user_rdis_dict(request.user)
    nutrients = populate_nutrient_values(nutr_dict, rdi_dict)
    if request.user.id == r.user.id:
        owner = True
    else:
        owner = False

    return render_to_response( 'selected_recipe.html', {
            "recipe": recipe,
            "ingredient_list": ingredient_list,
            "nutrients": nutrients,
            "owner": owner
            })
