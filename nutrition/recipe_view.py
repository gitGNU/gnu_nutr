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

class RecipeForm(forms.Form):
    name = forms.CharField(required=True)
    category = forms.ChoiceField()
    num_servings = forms.DecimalField(required=True)

    def __init__(self, *args, **kwargs):
        super(RecipeForm, self).__init__(*args, **kwargs)
        self.fields['category'].choices = \
            [(c.category_id, c.category_name) for c in get_recipe_categories()]

class IngredientForm(forms.Form):
    check = forms.BooleanField(required=False)
    num_measures = forms.DecimalField()
    measure = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        measure_list = kwargs['measure']
        del kwargs['measure']
        super(IngredientForm, self).__init__(*args, **kwargs)
        self.fields['measure'].choices = \
            [(m.measure_id, m.measure_name) for m in measure_list]

def load_recipe_from_database(recipe_id):
    ingredient_form_list = []
    recipe_form = None
    if recipe_id:
        r = get_recipe(recipe_id)
        if r:
            form_data = {'name': r.recipe_name,
                         'num_servings': r.number_servings,
                         'category':  r.category_id}
            recipe_form = RecipeForm(form_data)
            ingredient_list = get_ingredients(recipe_id)
            for i in ingredient_list:
                f = get_food(i.food_id)
                if f:
                    measure_list = get_measures(i.food_id)
                    measure = get_measure_from_measure_list(measure_list, i.measure_id)
                    form_data = {'%s-check' % i.food_id: False,
                                 '%s-num_measures' % i.food_id: i.number_measures,
                                 '%s-measure' % i.food_id: i.measure_id}
                    ingredient_form = IngredientForm(form_data, measure=measure_list, prefix=i.food_id)
                    ingredient_form.food_id = i.food_id
                    ingredient_form.food_name = f.food_name
                    ingredient_form.measure_id = i.measure_id
                    ingredient_form.amount = i.number_measures
                    ingredient_form_list.append(ingredient_form)
        else:
            recipe_category_list = get_recipe_categories()
            form_data = {'name': "Insert your Recipe's Name here",
                         'num_servings': 1.0,
                         'category':  recipe_category_list[0].category_id}
            recipe_form = RecipeForm(form_data)
    else:
        recipe_category_list = get_recipe_categories()
        form_data = {'name': "Insert your Recipe's Name here",
                     'num_servings': 1.0,
                     'category':  recipe_category_list[0].category_id}
        recipe_form = RecipeForm(form_data)
    return recipe_form, ingredient_form_list

def create_forms_from_data(data, recipe_form, ingredient_form_list):
    new_ingredient_form_list = []
    if not data['name']:
        data['name'] = "Insert your Recipe's Name here"
    try:
        num_servings = float(data['num_servings'])
    except ValueError:
        num_servings = 1.0
    if num_servings > 100.0:
        num_servings = 100.0
    form_data = {'name': data['name'],
                   'num_servings': num_servings,
                   'category':  data['category']}
    new_recipe_form = RecipeForm(form_data)
    for i in ingredient_form_list:
        f = get_food(i.food_id)
        if f:
            measure_list = get_measures(i.food_id)
            measure_id = data['%s-measure' % i.food_id]
            measure = get_measure_from_measure_list(measure_list, measure_id)
            if '%s-check' % i.food_id in data:
                check = data['%s-check' % i.food_id]
            else:
                check = False
            num_measures = data['%s-num_measures' % i.food_id]
            try:
                num_measures = float(num_measures)
            except ValueError:
                num_measures = '1.0'
                if num_measures > 10000.0:
                    num_measures = 10000.0
            form_data = {'%s-check' % i.food_id: check,
                         '%s-num_measures' % i.food_id: num_measures,
                         '%s-measure' % i.food_id: measure_id}
            new_ingredient_form = IngredientForm(form_data, measure=measure_list, prefix=i.food_id)
            new_ingredient_form.food_id = i.food_id
            new_ingredient_form.food_name = f.food_name
            new_ingredient_form.measure_id = measure_id
            new_ingredient_form.amount = num_measures
            new_ingredient_form_list.append(new_ingredient_form)
    return new_recipe_form, new_ingredient_form_list

def food_in_recipe(food_id, ingredient_form_list):
    for form in ingredient_form_list:
        if '%s-measure' % food_id in form.data:
            return True
    return False

def create_new_ingredient(food_id):
    name = food_id_2_name(food_id)
    f = get_food(food_id)
    if f and name:
        measure_list = get_measures(food_id)
        ingredient_data = {'%s-check' % food_id: False,
                           '%s-num_measures' % food_id: 1.0,
                           '%s-measure' % food_id: measure_list[0].measure_id}
        ingredient_form = IngredientForm(ingredient_data, measure=measure_list, prefix=food_id)
        ingredient_form.food_id = int(food_id)
        ingredient_form.food_name = f.food_name
        ingredient_form.measure_id = measure_list[0].measure_id
        ingredient_form.amount = 1.0
    return ingredient_form

def delete_from_recipe(old_ingredient_form_list, data):
    new_ingredient_plan_list = []
    for form in old_ingredient_form_list:
        if '%s-check' % form.food_id not in data:
            new_ingredient_plan_list.append(form)
    return new_ingredient_plan_list

def save_recipe_form(user, recipe_form, ingredient_form_list):
    if all_is_valid(recipe_form, ingredient_form_list):
        recipe_id = save_recipe_to_database(user, recipe_form, ingredient_form_list)
        return recipe_id
    return None

def calc_recipe_nutrition(user, recipe_form, ingredient_form_list):
    if all_is_valid(recipe_form, ingredient_form_list):
        recipe_data = recipe_form.cleaned_data
        num_servings = recipe_data['num_servings']
        return calculate_recipe_nutrient_data(user, ingredient_form_list, num_servings)
    else:
        return None, None

def all_is_valid(recipe_form, ingredient_form_list):
    if recipe_form.is_valid():
        for ingredient_form in ingredient_form_list:
            if not ingredient_form.is_valid():
                return False
        return True
    return False

@login_required
def create_recipe(request, food_id=None, recipe_id=None):
    recipe_form, ingredient_form_list = load_recipe_from_database(recipe_id)

    if recipe_id:
        if food_id and not food_in_recipe(food_id, ingredient_form_list):
            new_ingredient_form = create_new_ingredient(food_id)
            if new_ingredient_form:
                ingredient_form_list.append(new_ingredient_form)
                recipe_id = save_recipe_form(request.user, recipe_form, ingredient_form_list)

    if request.POST:
        data = request.POST.copy()
        recipe_form, ingredient_form_list = \
            create_forms_from_data(data, recipe_form, ingredient_form_list)

        if data.has_key('delete_ingredient'):
            ingredient_form_list = delete_from_recipe(ingredient_form_list, data)

        recipe_id = save_recipe_form(request.user, recipe_form, ingredient_form_list)

        if data.has_key('refresh') or data.has_key('delete_ingredient') or \
                data.has_key('save_recipe'):
            return HttpResponseRedirect('/create_recipe/recipe_id/%s/' % recipe_id)

        if data.has_key('add_ingredient'):
            return HttpResponseRedirect('/create_recipe/recipe_id/%s/add_ingredient/'
                                        % recipe_id)

    nutrients, calorie_list = calc_recipe_nutrition(request.user,
                                                    recipe_form,
                                                    ingredient_form_list)

    for i, form in enumerate(ingredient_form_list):
        if calorie_list:
            ingredient_form_list[i].calories = calorie_list[i]

    filler_list = []
    for i in range(10 - len(ingredient_form_list)):
        filler_list.append(i)

    return render_to_response( 'create_recipe.html', {
            "recipe_id": recipe_id,
            "recipe": recipe_form,
            "ingredient_list": ingredient_form_list,
            "filler_list": filler_list,
            "nutrients": nutrients})
