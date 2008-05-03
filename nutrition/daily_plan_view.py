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

from calendar import monthcalendar, day_abbr, month_abbr
from datetime import *

from models import *

class PlanFoodForm(forms.Form):
    check = forms.BooleanField()
    num_measures = forms.DecimalField()
    measure = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        measure_list = kwargs['measure']
        del kwargs['measure']
        super(PlanFoodForm, self).__init__(*args, **kwargs)
        self.fields['measure'].choices = \
            [(m.measure_id, m.measure_name) for m in measure_list]

class PlanRecipeForm(forms.Form):
    check = forms.BooleanField()
    num_measures = forms.DecimalField(required=True)
    measure = forms.CharField(widget=forms.TextInput(attrs={'readonly':''}))

def abbreviated_days():
    day_list = [];
    for day in day_abbr:
        day_list.append(day[0])
    return day_list

def abbreviated_month(i):
    return month_abbr[i]

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
        self.prev_year = year - 1
        self.next_year = year + 1
        self.month = month
        self.next_month = month + 1
        if self.next_month > 12:
            self.next_month = 1
        self.prev_month = month - 1
        if self.prev_month < 1:
            self.prev_month = 12
        self.day = day
        self.month_name = abbreviated_month(month)
        self.day_names = abbreviated_days()
        self.calendar_rows = monthcalendar(year, month)

def food_in_plan(food_id, session, year, month, day):
    date_str = '%s%s%s' % (year, month, day)
    for item_type, item_id in session['plan_order' + date_str]:
        if item_type == 'food' and item_id == food_id:
            return True
    return False

def recipe_in_plan(recipe_id, session, year, month, day):
    date_str = '%s%s%s' % (year, month, day)
    for item_type, item_id in session['plan_order' + date_str]:
        if item_type == 'recipe' and item_id == recipe_id:
            return True
    return False

def create_plan_form(session, year, month, day, food_id=None, recipe_id=None):
    if food_id:
        measure = get_measures(food_id)
        name = food_id_2_name(food_id)
        prefix = '%s_food' % food_id
        form_data = {'%s-check' % prefix: False,
                     '%s-num_measures' % prefix: 1,
                     '%s-measure' % prefix: measure[0].measure_id}
        form = PlanFoodForm(form_data, measure=measure, prefix=prefix)
    if recipe_id:
        name = get_recipe_name(recipe_id)
        prefix = '%s_recipe' % recipe_id
        form_data = {'%s-check' % prefix: False,
                     '%s-num_measures' % prefix: 1,
                     '%s-measure' % prefix: '1 serving'}
        form = PlanRecipeForm(form_data, prefix=prefix)
    return form

def initialize_plan_session(session, date_str):
    if 'meal_plan' + date_str not in session:
        session['meal_plan' + date_str] = {}

def clear_plan_session(session, date_str):
    if 'meal_plan' + date_str in session:
        del session['meal_plan' + date_str]
    if 'plan_order' + date_str in session:
        del session['plan_order' + date_str]

def add_new_form_to_session(session, year, month, day, form,
                            food_id=None, recipe_id=None):
    date_str = '%s%s%s' % (year, month, day)
    initialize_plan_session(session, date_str)
    key = 'meal_plan' + date_str
    order_list = session['plan_order' + date_str]
    if food_id:
        name = food_id_2_name(food_id)
        prefix = '%s_food' % food_id
        order_list.append(('food', food_id))
    else:
        prefix = '%s_recipe' % recipe_id
        name = get_recipe_name(recipe_id)
        order_list.append(('recipe', recipe_id))
    session['plan_order' + date_str] = order_list
    session[key]['%s-name' % prefix] = name
    session[key]['%s-num_measures' % prefix] = 1
    session[key]['%s-measure' % prefix] = form.data['%s-measure' % prefix]

def load_plan_order_from_session(session, year, month, day):
    date_str = '%s%s%s' % (year, month, day)
    return session['plan_order' + date_str]

def load_meal_plan_from_session(session, year, month, day):
    date_str = '%s%s%s' % (year, month, day)
    plan_form_list = []
    plan_order = []
    if 'meal_plan' + date_str in session and \
            'plan_order' + date_str in session:
        plan_order = session['plan_order' + date_str]
        session_data = session['meal_plan' + date_str]
        for item_type, item_id in plan_order:
            if item_type == 'food':
                food_id = item_id
                measure = get_measures(food_id)
                prefix = '%s_food' % food_id
                form_data = {'%s-check' % prefix: False,
                             '%s-num_measures' % prefix: session_data['%s-num_measures' % prefix],
                             '%s-measure' % prefix: session_data['%s-measure' % prefix]}
                form = PlanFoodForm(form_data, measure=measure, prefix=prefix)
                plan_form_list.append(form)
            if item_type == 'recipe':
                recipe_id = item_id
                prefix = '%s_recipe' % recipe_id
                form_data = {'%s-check' % prefix: False,
                             '%s-num_measures' % prefix: session_data['%s-num_measures' % prefix],
                             '%s-measure' % prefix: '1 serving'}
                form = PlanRecipeForm(form_data, prefix=prefix)
                plan_form_list.append(form)
    return plan_form_list

def save_plan(session, user, year, month, day):
    plan_form_list = load_meal_plan_from_session(session, year, month, day)
    plan_order = load_plan_order_from_session(session, year, month, day)
    if all_is_valid(plan_form_list):
        save_plan_to_database(user, plan_form_list, plan_order, year, month, day)
        return 1
    return 0

def delete_from_plan(session, data, year, month, day):
    date_str = '%s%s%s' % (year, month, day)
    meal_key = 'meal_plan' + date_str
    order_key = 'plan_order' + date_str
    if order_key in session:
        order = session[order_key]
        for item_type, item_id in order:
            if item_type == 'food':
                prefix = '%s_food' % item_id
            if item_type == 'recipe':
                prefix = '%s_recipe' % item_id
            if '%s-check' % prefix in session[meal_key]:
                del session[meal_key]['%s-name' % prefix]
                del session[meal_key]['%s-num_measures' % prefix]
                del session[meal_key]['%s-measure' % prefix]
                del session[meal_key]['%s-check' % prefix]
                order.remove((item_type, item_id))
        session[order_key] = order

def save_meal_plan_to_session(session, year, month, day, data):
    date_str = '%s%s%s' % (year, month, day)
    key = 'meal_plan' + date_str
#    session[key] = {}
    for k, v in data.items():
        session[key][k] = v

def all_is_valid(plan_form_list):
    for form in plan_form_list:
        if not form.is_valid():
            return False
    return True

def get_plan_nutrient_data(user, session, plan_form_list, year, month, day):
    if all_is_valid(plan_form_list):
        plan_form_data_list = []
        for form in plan_form_list:
            plan_form_data_list.append(form.cleaned_data)
        plan_order = load_plan_order_from_session(session, year, month, day)
        return calculate_plan_nutrient_data(user, plan_form_data_list, plan_order)
    else:
        return None, None

def load_plan_from_database_to_session(session, user, year, month, day):
    plan_list = get_user_plan(user, year, month, day)
    plan_order = []
    date_str = '%s%s%s' % (year, month, day)
    initialize_plan_session(session, date_str)
    key = 'meal_plan' + date_str
    for o in plan_list:
        if o.item_type == 'F':
            food_id = o.item_id
            prefix = '%s_food' % food_id
            session[key]['%s-measure' % prefix] = o.measure
            plan_order.append(('food', food_id))
        else:
            recipe_id = o.item_id
            prefix = '%s_recipe' % recipe_id
            plan_order.append(('recipe', recipe_id))
            session[key]['%s-measure' % prefix] = '1 serving'
        session[key]['%s-num_measures' % prefix] = o.num_measures
        session[key]['%s-name' % prefix] = o.name
    session['plan_order' + date_str] = plan_order

def append_to_plan(plan_form_list, calories_dict, session, year, month, day):
    date_str = '%s%s%s' % (year, month, day)
    print 'calories_dict = ', calories_dict
    if 'meal_plan' + date_str in session and \
            'plan_order' + date_str in session:
        plan_order = session['plan_order' + date_str]
        for i in range(0, len(plan_order)):
            item_type, item_id = plan_order[i]
            plan_form_list[i].item_type = item_type
            plan_form_list[i].item_id = item_id
            prefix = '%s_%s' % (item_id, item_type)
            plan_form_list[i].name_str = session['meal_plan' + date_str]['%s-name' % prefix]
            plan_form_list[i].measure_str = session['meal_plan' + date_str]['%s-measure' % prefix]
            plan_form_list[i].calories = calories_dict[prefix]
            num_measures = session['meal_plan' + date_str]['%s-num_measures' % prefix]
            try:
                val = float(num_measures)
                plan_form_list[i].amount = num_measures
            except ValueError:
                plan_form_list[i].amount = '1.0'
    return plan_form_list

@login_required
def daily_plan(request, year=None, month=None, day=None, food_id=None, recipe_id=None):
    save_result = 2
    if year == None or month == None or day == None:
        year, month, day = get_today()
        date_in_url = False
        date_str = '%s%s%s' % (year, month, day)
        clear_plan_session(request.session, date_str)
    else:
        date_in_url = True

    month_calendar = MonthCalendar(year, month, day)

    date_str = '%s%s%s' % (year, month, day)

    if food_id:
        plan_form_list = load_meal_plan_from_session(request.session, year, month, day)
        if not food_in_plan(food_id, request.session, year, month, day):
            new_form = create_plan_form(request.session, year, month, day, food_id=food_id)
            if new_form:
                plan_form_list.append(new_form)
                add_new_form_to_session(request.session, year, month, day, \
                                            new_form, food_id=food_id)
    elif recipe_id:
        plan_form_list = load_meal_plan_from_session(request.session, year, month, day)
        if not recipe_in_plan(recipe_id, request.session, year, month, day):
            new_form = create_plan_form(request.session, year, month, day, recipe_id=recipe_id)
            if new_form:
                plan_form_list.append(new_form)
                add_new_form_to_session(request.session, year, month, day, \
                                            new_form, recipe_id=recipe_id)
    else:
        if request.POST:
            data = request.POST.copy()
            save_meal_plan_to_session(request.session, year, month, day, data)

            if data.has_key('refresh'):
                None

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
                save_result = save_plan(request.session, request.user, year, month, day)

            if data.has_key('delete'):
                delete_from_plan(request.session, data, year, month, day)
                return HttpResponseRedirect('')
        else:
            load_plan_from_database_to_session(request.session, request.user, year, month, day)

        plan_form_list = load_meal_plan_from_session(request.session, year, month, day)

    print 'plan_form_list = ', plan_form_list

    nutrients, calorie_dict = get_plan_nutrient_data(request.user, request.session,
                                                     plan_form_list, year, month, day)

    plan_form_list = append_to_plan(plan_form_list, calorie_dict, request.session,
                                    year, month, day)

    filler_list = [i for i in range(10 - len(plan_form_list))]

    return render_to_response( 'daily_plan.html', {
            "cal": month_calendar,
            "plan_list": plan_form_list,
            "filler_list": filler_list,
            "nutrients": nutrients,
            "save_result" : save_result
            })
