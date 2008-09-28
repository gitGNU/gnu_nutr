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

from datetime import *
import time

from models import *

class PlanFoodForm(forms.Form):
    check = forms.BooleanField(required=False)
    num_measures = forms.DecimalField()
    measure = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        measure_list = kwargs['measure']
        del kwargs['measure']
        super(PlanFoodForm, self).__init__(*args, **kwargs)
        self.fields['measure'].choices = \
            [(m.measure_id, m.measure_name) for m in measure_list]

class PlanRecipeForm(forms.Form):
    check = forms.BooleanField(required=False)
    num_measures = forms.DecimalField(required=True)
    measure = forms.CharField(widget=forms.TextInput(attrs={'readonly':''}))

class PlanCopyDate(forms.Form):
    copy_date = forms.DateField(input_formats=['%Y/%m/%d'], widget=forms.TextInput(attrs={'style':'width:10em'}))

def get_today():
    dt = date.today()
    return dt.year, dt.month, dt.day

class MonthCalendar:
    def __init__(self, year, month, day):
        if year:
            year = int(year)
        if month:
            month = int(month)
        if day:
            day = int(day)
        self.year = year
        self.month = month
        self.day = day

def food_in_plan(food_id, plan_form_list):
    for form in plan_form_list:
        if form.item_type == 'food' and form.item_id == food_id:
            return True
    return False

def recipe_in_plan(recipe_id, plan_form_list):
    for form in plan_form_list:
        if form.item_type == 'recipe' and form.item_id == recipe_id:
            return True
    return False

def create_plan_form(food_id=None, recipe_id=None):
    form = None
    if food_id:
        measure_list = get_measures(food_id)
        name = food_id_2_name(food_id)
        if name and measure_list:
            prefix = '%s_food' % food_id
            form_data = {'%s-check' % prefix: False,
                         '%s-num_measures' % prefix: 1,
                         '%s-measure' % prefix: measure_list[0].measure_id}
            form = PlanFoodForm(form_data, measure=measure_list, prefix=prefix)
            form.item_type = 'food'
            form.item_id = food_id
            form.name_str = name
            form.measure_str = measure_list[0].measure_id
    elif recipe_id:
        name = get_recipe_name(recipe_id)
        if name:
            prefix = '%s_recipe' % recipe_id
            form_data = {'%s-check' % prefix: False,
                         '%s-num_measures' % prefix: 1,
                         '%s-measure' % prefix: '1 serving'}
            form = PlanRecipeForm(form_data, prefix=prefix)
            form.item_type = 'recipe'
            form.item_id = recipe_id
            form.name_str = name
            form.measure_str = '1 serving'
    return form

def save_plan_to_database(user, plan_form_list, year, month, day):
    if all_is_valid(plan_form_list):
        save_plan_to_db(user, plan_form_list, year, month, day)
        return 1
    return 0

def delete_from_plan(old_plan_form_list, data):
    new_plan_form_list = []
    for form in old_plan_form_list:
        if form.item_type == 'food':
            food_id = form.item_id
            if '%s_food-check' % food_id not in data:
                new_plan_form_list.append(form)
        if form.item_type == 'recipe':
            recipe_id = form.item_id
            if '%s_recipe-check' % recipe_id not in data:
                new_plan_form_list.append(form)
    return new_plan_form_list

def all_is_valid(plan_form_list):
    for form in plan_form_list:
        if not form.is_valid():
            return False
    return True

def get_plan_nutrient_data(user, plan_form_list):
    if all_is_valid(plan_form_list):
        return calculate_plan_nutrient_data(user, plan_form_list)
    else:
        return None, None

def load_plan_from_database(user, year, month, day):
    plan_data_list = get_user_plan(user, year, month, day)
    plan_form_list = []
    for o in plan_data_list:
        if o.item_type == 'F':
            food_id = o.item_id
            prefix = '%s_food' % food_id
            measure_list = get_measures(food_id)
            name = food_id_2_name(food_id)
            if name and measure_list:
                selected_measure = get_measure_from_measure_list(measure_list, o.measure)
                form_data = {'%s-check' % prefix: False,
                             '%s-num_measures' % prefix: o.num_measures,
                             '%s-measure' % prefix: o.measure}
                form = PlanFoodForm(form_data, measure=measure_list, prefix=prefix)
                form.item_type = 'food'
                form.item_id = food_id
                form.name_str = name
                form.measure_str = selected_measure.measure_id
                plan_form_list.append(form)
        elif o.item_type == 'R':
            recipe_id = o.item_id
            name = get_recipe_name(recipe_id)
            if name:
                prefix = '%s_recipe' % recipe_id
                form_data = {'%s-check' % prefix: False,
                             '%s-num_measures' % prefix: o.num_measures,
                             '%s-measure' % prefix: '1 serving'}
                form = PlanRecipeForm(form_data, prefix=prefix)
                form.item_type = 'recipe'
                form.item_id = recipe_id
                form.name_str = name
                form.measure_str = '1 serving'
                plan_form_list.append(form)
    return plan_form_list

def create_plan_from_data(data, old_plan_form_list, year, month, day):
    new_plan_form_list = []
    for form in old_plan_form_list:
        if form.item_type == 'food':
            food_id = form.item_id
            prefix = '%s_%s' % (form.item_id, form.item_type)
            measure_list = get_measures(food_id)
            name = food_id_2_name(food_id)
            if name and measure_list:
                measure_id = data['%s-measure' % prefix]
                selected_measure = get_measure_from_measure_list(measure_list, measure_id)
                if '%s-check' % prefix in data:
                    check = data['%s-check' % prefix]
                else:
                    check = False
                try:
                    num_measures = float(data['%s-num_measures' % prefix])
                except ValueError:
                    num_measures = 1.0
                if num_measures > 10000.0:
                    num_measures = 10000.0
                form_data = {'%s-check' % prefix: check,
                             '%s-num_measures' % prefix: num_measures,
                             '%s-measure' % prefix: measure_id}
                new_form = PlanFoodForm(form_data, measure=measure_list, prefix=prefix)
                new_form.item_type = 'food'
                new_form.item_id = food_id
                new_form.name_str = name
                new_form.measure_str = selected_measure.measure_id
                new_plan_form_list.append(new_form)
        elif form.item_type == 'recipe':
            recipe_id = form.item_id
            prefix = '%s_%s' % (form.item_id, form.item_type)
            name = get_recipe_name(recipe_id)
            if name:
                if '%s-check' % prefix in data:
                    check = data['%s-check' % prefix]
                else:
                    check = False
                try:
                    num_measures = float(data['%s-num_measures' % prefix])
                except ValueError:
                    num_measures = 1.0
                if num_measures > 10000.0:
                    num_measures = 10000.0
                form_data = {'%s-check' % prefix: check,
                             '%s-num_measures' % prefix: num_measures,
                             '%s-measure' % prefix: '1 serving'}
                new_form = PlanRecipeForm(form_data, prefix=prefix)
                new_form.item_type = 'recipe'
                new_form.item_id = recipe_id
                new_form.name_str = name
                new_form.measure_str = '1 serving'
                new_plan_form_list.append(new_form)
    return new_plan_form_list

def append_calorie_data_to_plan(old_plan_form_list, calories_dict):
    new_plan_form_list = []
    for form in old_plan_form_list:
        prefix = '%s_%s' % (form.item_id, form.item_type)
        form.calories = calories_dict[prefix]
        try:
            val = float(form.data['%s-num_measures' % prefix])
            form.amount = val
        except ValueError:
            form.amount = '1.0'
        new_plan_form_list.append(form)
    return new_plan_form_list

def parse_date(date_string):
    try:
        return time.strptime(date_string, "%Y/%m/%d")
    except ValueError:
        return None

def copy_plan_from_date(user, source_date):
    year = source_date.strftime('%Y')
    month = source_date.strftime('%m')
    day = source_date.strftime('%d')
    plan_form_list = load_plan_from_database(user, year, month, day)
    return plan_form_list

@login_required
def daily_plan(request, year=None, month=None, day=None, food_id=None, recipe_id=None):

    plan_date = None
    if year or month or day:
        try:
            plan_date = date(int(year), int(month), int(day))
        except ValueError:
            raise Http404

    save_result = 2

    if year == None or month == None or day == None:
        year, month, day = get_today()
        date_in_url = False
        date_str = '%s%s%s' % (year, month, day)
    else:
        date_in_url = True
        date_str = '%s%s%s' % (year, month, day)

    month_calendar = MonthCalendar(year, month, day)

    if plan_date:
        delta =  plan_date - date.today()
        days_from_today = delta.days
    else:
        days_from_today = 0

    if food_id:
        # FIXME: need to check web-page - not just database - problem
        # with reload page.
        plan_form_list = load_plan_from_database(request.user, year, month, day)
        if not food_in_plan(food_id, plan_form_list):
            new_form = create_plan_form(food_id=food_id)
            if new_form:
                plan_form_list.append(new_form)
                save_plan_to_database(request.user, plan_form_list, year, month, day)
    elif recipe_id:
        plan_form_list = load_plan_from_database(request.user, year, month, day)
        if not recipe_in_plan(recipe_id, plan_form_list):
            new_form = create_plan_form(recipe_id=recipe_id)
            if new_form:
                plan_form_list.append(new_form)
                save_plan_to_database(request.user, plan_form_list, year, month, day)
    else:
        if request.POST:

            plan_form_list = load_plan_from_database(request.user, year, month, day)
            data = request.POST.copy()
            plan_form_list = create_plan_from_data(data, plan_form_list, year, month, day)
            save_result = save_plan_to_database(request.user, plan_form_list, year, month, day)

            if data.has_key('refresh'):
                return HttpResponseRedirect('')

            if data.has_key('copy_plan') and data.has_key('copy_date'):
                form_data = {'copy_date' : data['copy_date']}
                copy_date_form = PlanCopyDate(form_data)
                if copy_date_form.is_valid():
                    plan_form_list = copy_plan_from_date(request.user,
                                                         copy_date_form.cleaned_data['copy_date'])
                    save_result = save_plan_to_database(request.user, plan_form_list, year, month, day)
                return HttpResponseRedirect('')

            if data.has_key('add_recipe'):
                if date_in_url:
                    return HttpResponseRedirect('add_recipe/')
                else:
                    return HttpResponseRedirect('%s/%s/%s/add_recipe/' % (year, month, day))

            if data.has_key('add_food'):
                if date_in_url:
                    return HttpResponseRedirect('add_food/')
                else:
                    return HttpResponseRedirect('%s/%s/%s/add_food/' % (year, month, day))

            if data.has_key('save'):
                return HttpResponseRedirect('')

            if data.has_key('delete'):
                plan_form_list = delete_from_plan(plan_form_list, data)
                save_plan_to_database(request.user, plan_form_list, year, month, day)
                return HttpResponseRedirect('')

        plan_form_list = load_plan_from_database(request.user, year, month, day)

    nutrients, calorie_dict = get_plan_nutrient_data(request.user, plan_form_list)

    plan_form_list = append_calorie_data_to_plan(plan_form_list, calorie_dict)

    filler_list = [i for i in range(10 - len(plan_form_list))]

    copy_date_form = PlanCopyDate()

    return render_to_response( 'daily_plan.html', {
            "cal": month_calendar,
            "plan_list": plan_form_list,
            "filler_list": filler_list,
            "nutrients": nutrients,
            "copy_date_form": copy_date_form,
            "save_result" : save_result,
            "days_from_today" : days_from_today
            })
