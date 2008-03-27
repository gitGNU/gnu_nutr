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
    food_id = forms.IntegerField(widget=forms.HiddenInput)
    check = forms.BooleanField()
    name = forms.CharField(widget=forms.HiddenInput)
    num_measures = forms.DecimalField()
    measure = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        measure_list = kwargs['measure']
        del kwargs['measure']
        super(IngredientForm, self).__init__(*args, **kwargs)
        self.fields['measure'].choices = \
            [(m.id, '%g %s' %(m.amount, m.name)) for m in measure_list]

def load_recipe_from_id(recipe_id):
    ingredient_form_list = []
    recipe = None
    recipe_data = get_recipe(recipe_id)
    form_data = {'name': recipe_data.name,
                 'num_servings': recipe_data.number_servings,
                 'category':  recipe_data.category.id}
    recipe_form = RecipeForm(form_data)
    ingredients = get_ingredients(recipe_id)
    for i in ingredients:
        food_id = i.food_id
        measure = get_measures(food_id)
        form_data = {'%s-food_id' % food_id: food_id,
                     '%s-check' % food_id: False,
                     '%s-name' % food_id: i.food.name,
                     '%s-num_measures' % food_id: i.number_measures,
                     '%s-measure' % food_id: i.measure_id}
        ingredient_form = IngredientForm(form_data, measure=measure, prefix=food_id)
        ingredient_form_list.append(ingredient_form)
    return recipe_form, ingredient_form_list

def load_recipe_from_session(session):
    ingredient_form_list = []
    recipe = None
    if 'recipe_data' in session:
        recipe_data = session['recipe_data']
        form_data = {'name': recipe_data['name'],
                     'num_servings': recipe_data['num_servings'],
                     'category':  recipe_data['category']}
        recipe_form = RecipeForm(form_data)
        if 'ingredient_order' in session:
            ingredient_order = session['ingredient_order']
            for food_id in ingredient_order:
                measure = get_measures(food_id)
                form_data = {'%s-food_id' % food_id: food_id,
                             '%s-check' % food_id: False,
                             '%s-name' % food_id: recipe_data['%s-name' % food_id],
                             '%s-num_measures' % food_id: recipe_data['%s-num_measures' % food_id],
                             '%s-measure' % food_id: recipe_data['%s-measure' % food_id]}
                ingredient_form = IngredientForm(form_data, measure=measure, prefix=food_id)
                ingredient_form_list.append(ingredient_form)
    return recipe_form, ingredient_form_list

def save_recipe_to_session(session, data):
    session['recipe_data'] = {}
    for key, val in data.items():
        session['recipe_data'][key] = val

def save_recipe_from_id_to_session(session, recipe_form, ingredient_form_list):
    session['recipe_data'] = {}
    order_list = []
    for key, val in recipe_form.data.items():
        session['recipe_data'][key] = val
    for form in ingredient_form_list:
        for key, val in form.data.items():
            if key.split('-')[1] == 'food_id':
                order_list.append(val)
            session['recipe_data'][key] = val
    session['ingredient_order'] = order_list

def clear_recipe_session(session):
    if 'ingredient_order' in session:
        del session['ingredient_order']
    if 'recipe_data' in session:
        del session['recipe_data']

def create_new_ingredient(food_id, session):
    ingredient_form = []
    if 'ingredient_order' in session:
        order_list = session['ingredient_order']
    else:
        order_list = []
    print 'order_list = ', order_list
    if food_id and int(food_id) not in order_list:
        name = food_id_2_name(food_id)
        measure = get_measures(food_id)
        ingredient_data = {'%s-food_id' % food_id: food_id,
                           '%s-check' % food_id: False,
                           '%s-name' % food_id: name,
                           '%s-num_measures' % food_id: 1,
                           '%s-measure' % food_id: measure[0].id}
        ingredient_form = IngredientForm(ingredient_data, measure=measure, prefix=food_id)
        if ingredient_form:
            session['recipe_data']['%s-food_id' % food_id] = food_id
            session['recipe_data']['%s-name' % food_id] = name
            session['recipe_data']['%s-num_measures' % food_id] = 1
            session['recipe_data']['%s-measure' % food_id] = measure[0].id
            session['ingredient_order'] = order_list + [int(food_id)]
            print 'after: order_list = ', session['ingredient_order']
    return ingredient_form

def delete_ingredients(session, data):
    if 'ingredient_order' in session:
        ingredient_order = session['ingredient_order']
        for food_id in session['ingredient_order']:
            if '%s-check' % food_id in session['recipe_data']:
                del session['recipe_data']['%s-food_id' % food_id]
                del session['recipe_data']['%s-name' % food_id]
                del session['recipe_data']['%s-num_measures' % food_id]
                del session['recipe_data']['%s-measure' % food_id]
                del session['recipe_data']['%s-check' % food_id]
                ingredient_order.remove(food_id)
        session['ingredient_order'] = ingredient_order

def save_recipe(session, user):
    recipe_form, ingredient_form_list = load_recipe_from_session(session)
    if all_is_valid(recipe_form, ingredient_form_list):
        save_recipe_to_database(user, recipe_form, ingredient_form_list)
        return 1
    return 0

def get_recipe_nutrient_data(user, recipe_form, ingredient_form_list):
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
    save_result = 2
    if recipe_id:
        recipe_form, ingredient_form_list = load_recipe_from_id(recipe_id)
        save_recipe_from_id_to_session(request.session, recipe_form, ingredient_form_list)
    elif food_id:
        if food_id == '0':
            clear_recipe_session(request.session)
            recipe_form = RecipeForm()
            ingredient_form_list = []
        else:
            recipe_form, ingredient_form_list = load_recipe_from_session(request.session)
            new_ingredient_form = create_new_ingredient(food_id, request.session)
            if new_ingredient_form:
                ingredient_form_list.append(new_ingredient_form)
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

        recipe_form, ingredient_form_list = load_recipe_from_session(request.session)

    nutrients, calorie_list = get_recipe_nutrient_data(request.user, recipe_form,
                                                       ingredient_form_list)

    for i in range(0, len(ingredient_form_list)):
        if calorie_list:
            ingredient_form_list[i].calories = calorie_list[i]
        data = ingredient_form_list[i].data
        food_id = data.keys()[0].split('-')[0]
        ingredient_form_list[i].name_str = data['%s-name' % food_id]
        ingredient_form_list[i].id = food_id
        ingredient_form_list[i].measure_str = data['%s-measure' % food_id]
        num_measures = data['%s-num_measures' % food_id]
        try:
            val = float(num_measures)
            ingredient_form_list[i].amount = num_measures
        except ValueError:
            ingredient_form_list[i].amount = '1.0'

    return render_to_response( 'create_recipe.html', {
            "recipe": recipe_form,
            "ingredient_list": ingredient_form_list,
            "nutrients": nutrients,
            "save_result": save_result})
