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
    food_id = forms.HiddenInput()
    check = forms.BooleanField()
    name = forms.CharField(widget=forms.TextInput(attrs={'readonly':''}))
    num_measures = forms.DecimalField()
    measure = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        measure_list = kwargs['measure']
        del kwargs['measure']
        super(PlanFoodForm, self).__init__(*args, **kwargs)
        self.fields['measure'].choices = \
            [(m.id, '%g %s' %(m.amount, m.name)) for m in measure_list]

def abbreviated_days():
    return day_abbr

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

def create_plan_form(food_id=None,recipe_id=None):
    if food_id:
        measure = get_measures(food_id)
        form_data = {'%s-food_id' % food_id: food_id,
                     '%s-check' % food_id: False,
                     '%s-name' % food_id: i.food.name,
                     '%s-num_measures' % food_id: i.number_measures,
                     '%s-measure' % food_id: i.measure_id}
        form = PlanFoodForm(form_data, measure=measure, prefix=food_id)
        num = (food_id, 'food')
    return form, num

def load_meal_plan_from_session(session, year, month, day):
    plan_list = []
    plan_order = []
    return plan_list, plan_order

def save_meal_plan_to_session(session, data):
    session['meal_plan'] = {}
    for k, v in data.items():
        session['meal_plan'][k] = v

@login_required
def daily_plan(request, year=None, month=None, day=None, food_id=None, recipe_id=None):
    if year == None or month == None or day == None:
        year, month, day = get_today()
    month_calendar = MonthCalendar(year, month, day)

    if food_id:
        plan_list, plan_order = load_meal_plan_from_session(request.session, year, month, day)
        plan_form, plan_num = create_plan_form(food_id=food_id)
        if plan_form:
            plan_list.append(plan_form)
            plan_order.append(plan_num)
    else:
        if request.POST:
            data = request.POST.copy()
            save_meal_plan_to_session(request.session, data)

            if data.has_key('refresh'):
                None

            if data.has_key('add_recipe'):
                return HttpResponseRedirect( 'add_recipe/')

            if data.has_key('add_food'):
                return HttpResponseRedirect( 'add_food/')

            if data.has_key('save'):
                None

            if data.has_key('delete'):
                None

        plan_list, plan_order = load_meal_plan_from_session(request.session, year, month, day)

    return render_to_response( 'daily_plan.html', {
            "cal": month_calendar,
            "plan_list": plan_list,
            "order": plan_order
            })
