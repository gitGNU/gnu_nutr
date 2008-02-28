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

class RecipeForm(forms.Form):
    name = forms.CharField(required=True)
    category = forms.ChoiceField()
    num_servings = forms.DecimalField(required=True)

    def __init__(self, *args, **kwargs):
        super(RecipeForm, self).__init__(*args, **kwargs)
        self.fields['category'].choices = \
            [(c.id, c.name) for c in get_recipe_categories()]

class IngredientForm(forms.Form):
    food_id = forms.HiddenInput()
    check = forms.BooleanField()
    name = forms.CharField(widget=forms.TextInput(attrs={'readonly':''}))
    num_measures = forms.DecimalField()
    measure = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        measure_list = kwargs['measure']
        del kwargs['measure']
        super(IngredientForm, self).__init__(*args, **kwargs)
        self.fields['measure'].choices = \
            [(m.id, '%g %s' %(m.amount, m.name)) for m in measure_list]

def load_recipe_from_id(recipe_id):
    ingredient_list = []
    ingredient_order = []
    recipe = None
    recipe_data = get_recipe(recipe_id)
    form_data = {'name': recipe_data.name,
                 'num_servings': recipe_data.number_servings,
                 'category':  recipe_data.category.id}
    recipe = RecipeForm(form_data)
    ingredients = get_ingredients(recipe_id)
    for i in ingredients:
        food_id = i.food_id
        ingredient_order.append(food_id)
        measure = get_measures(food_id)
        form_data = {'%s-food_id' % food_id: food_id,
                     '%s-check' % food_id: False,
                     '%s-name' % food_id: i.food.name,
                     '%s-num_measures' % food_id: i.number_measures,
                     '%s-measure' % food_id: i.measure_id}
        ingredient = IngredientForm(form_data, measure=measure, prefix=food_id)
        ingredient_list.append(ingredient)
    return recipe, ingredient_list, ingredient_order

def load_recipe_from_session(session):
    ingredient_list = []
    ingredient_order = []
    recipe = None
    if 'recipe_data' in session:
        recipe_data = session['recipe_data']
        form_data = {'name': recipe_data['name'],
                     'num_servings': recipe_data['num_servings'],
                     'category':  recipe_data['category']}
        recipe = RecipeForm(form_data)
        if 'ingredient_order' in session:
            ingredient_order = session['ingredient_order']
            for food_id in ingredient_order:
                measure = get_measures(food_id)
                form_data = {'%s-food_id' % food_id: food_id,
                             '%s-check' % food_id: False,
                             '%s-name' % food_id: recipe_data['%s-name' % food_id],
                             '%s-num_measures' % food_id: recipe_data['%s-num_measures' % food_id],
                             '%s-measure' % food_id: recipe_data['%s-measure' % food_id]}
                ingredient = IngredientForm(form_data, measure=measure, prefix=food_id)
                ingredient_list.append(ingredient)
    return recipe, ingredient_list, ingredient_order

def save_recipe_to_session(session, data):
    session['recipe_data'] = {}
    for key, val in data.items():
        session['recipe_data'][key] = val

def save_recipe_from_id_to_session(session, recipe, ingredient_list, ingredient_order):
    session['recipe_data'] = {}
    session['ingredient_order'] = ingredient_order
    for key, val in recipe.data.items():
        session['recipe_data'][key] = val
    for i in ingredient_list:
        for key, val in i.data.items():
            session['recipe_data'][key] = val

def clear_recipe_session(session):
    if 'ingredient_order' in session:
        del session['ingredient_order']
    if 'recipe_data' in session:
        del session['recipe_data']

def create_new_ingredient(food_id, session, ingredient_order):
    new_ingredient = []
    if food_id and food_id not in ingredient_order:
        name = food_id_2_name(food_id)
        measure = get_measures(food_id)
        new_ingredient_data = {'%s-food_id' % food_id: food_id,
                               '%s-check' % food_id: False,
                               '%s-name' % food_id: name,
                               '%s-num_measures' % food_id: 1,
                               '%s-measure' % food_id: measure[0].id}
        new_ingredient = IngredientForm(new_ingredient_data, measure=measure, prefix=food_id)
        session['ingredient_order'] = ingredient_order + [food_id]
        ingredient_order += [food_id]
        session['recipe_data']['%s-name' % food_id] = name
        session['recipe_data']['%s-num_measures' % food_id] = 1
        session['recipe_data']['%s-measure' % food_id] = measure[0].id
    return new_ingredient, ingredient_order

def delete_ingredients(session, data):
    if 'ingredient_order' in session:
        ingredient_order = session['ingredient_order']
        for food_id in session['ingredient_order']:
            if '%s-check' % food_id in session['recipe_data']:
                del session['recipe_data']['%s-name' % food_id]
                del session['recipe_data']['%s-num_measures' % food_id]
                del session['recipe_data']['%s-measure' % food_id]
                del session['recipe_data']['%s-check' % food_id]
                ingredient_order.remove(food_id)
        session['ingredient_order'] = ingredient_order

def save_recipe(session, user):
    recipe, ingredient_list, ingredient_order = load_recipe_from_session(session)
    if all_is_valid(recipe, ingredient_list):
        save_recipe_to_database(user, recipe, ingredient_list, ingredient_order)
        return 1
    return 0

def get_recipe_nutrient_data(user, recipe, ingredient_list, ingredient_order):
    if all_is_valid(recipe, ingredient_list):
        recipe_data = recipe.cleaned_data
        num_servings = recipe_data['num_servings']
        ingredient_data_list = []
        for ingredient in ingredient_list:
            ingredient_data_list.append(ingredient.cleaned_data)
        return calculate_recipe_nutrient_data(user, ingredient_data_list,
                                              ingredient_order, num_servings)
    else:
        return None, None, None, None, None

def all_is_valid(recipe, ingredient_list):
    if recipe.is_valid():
        for ingredient in ingredient_list:
            if not ingredient.is_valid():
                return False
        return True
    return False

@login_required
def create_recipe(request, food_id=None, recipe_id=None):
    if 'recipe_data' in request.session:
        print 'before: recipe_data = ', request.session['recipe_data']
        print 'before: session = ', request.session
    save_result = 2
    if recipe_id:
        recipe, ingredient_list, ingredient_order = load_recipe_from_id(recipe_id)
        save_recipe_from_id_to_session(request.session, recipe, ingredient_list, ingredient_order)
    elif food_id:
        if food_id == '0':
            clear_recipe_session(request.session)
            recipe = RecipeForm()
            ingredient_list = []
            ingredient_order = []
        else:
            recipe, ingredient_list, ingredient_order = load_recipe_from_session(request.session)
            new_ingredient, ingredient_order = \
                create_new_ingredient(food_id, request.session, ingredient_order)
            if new_ingredient:
                ingredient_list.append(new_ingredient)
    else:
        if request.POST:
            data = request.POST.copy()
            save_recipe_to_session(request.session, data)

            if data.has_key('refresh'):
                None

            if data.has_key('add_ingredient'):
                return HttpResponseRedirect( '/add_ingredient/')

            if data.has_key('delete_ingredient'):
                delete_ingredients(request.session, data)
                return HttpResponseRedirect( '/create_recipe/')

            if data.has_key('save_recipe'):
                save_result = save_recipe(request.session, request.user)

        recipe, ingredient_list, ingredient_order = load_recipe_from_session(request.session)

    nutrients = get_recipe_nutrient_data(request.user, recipe, ingredient_list, ingredient_order)

    if 'recipe_data' in request.session:
        print 'after: recipe_data = ', request.session['recipe_data']

    return render_to_response( 'create_recipe.html', {
            "recipe": recipe,
            "ingredient_list": ingredient_list,
            "nutrients": nutrients,
            "save_result": save_result})
