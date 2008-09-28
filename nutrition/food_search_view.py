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

class FoodSearchForm(forms.Form):
    text = forms.CharField(max_length=60)
    food_group = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(FoodSearchForm, self).__init__(*args, **kwargs)
        self.fields['food_group'].choices = \
            [(g.group_id, g.group_name) for g in get_food_groups()]


def process_food_search_request(request):
    nbr_results_per_page = 50.0
    data = request.GET.copy()

    pages = {}

    if data.has_key('page'):
        try:
            current_page = int(data['page'])
        except ValueError:
            current_page = 1
    else:
        current_page = 1

    pages['first'] = False
    pages['last'] = False
    pages['current'] = False
    pages['p1'] = False
    pages['p2'] = False
    pages['p10'] = False
    pages['m1'] = False
    pages['m2'] = False
    pages['m10'] = False

    form = FoodSearchForm(data)
    if form.is_valid():
        search_text = form.cleaned_data['text']
        food_group = int(form.cleaned_data['food_group'])
        start_range, end_range = (50 * (current_page - 1)), (50 * current_page)
        food_list, total_count = get_food_from_food_str(search_text, food_group,
                                                        start_range, end_range)
        nbr_pages, rem = divmod(total_count, nbr_results_per_page)
        if rem > 0:
            nbr_pages += 1
        nbr_pages = int(nbr_pages)

        pages['first'] = 1
        if nbr_pages != 1:
            pages['last'] = nbr_pages
        else:
            pages['last'] = 1

        pages['current'] = current_page

        if current_page - 1 > 1:
            pages['m1'] = current_page - 1
        else:
            pages['m1'] = False

        if current_page - 2 > 1:
            pages['m2'] = current_page - 2
        else:
            pages['m2'] = False

        if current_page - 10 > 1:
            pages['m10'] = current_page - 10
        else:
            pages['m10'] = False

        if current_page + 1 < nbr_pages:
            pages['p1'] = current_page + 1
        else:
            pages['p1'] = False

        if current_page + 2 < nbr_pages:
            pages['p2'] = current_page + 2
        else:
            pages['p2'] = False

        if current_page + 10 < nbr_pages:
            pages['p10'] = current_page + 10
        else:
            pages['p10'] = False

    else:
        search_text = ""
        food_group = 0
        food_list = []

    dict = {"search_text": search_text,
            "form": form,
            "foods": food_list,
            "food_group": food_group,
            "pages": pages,
            "current_page": current_page}
    return dict

@login_required
def food_search(request):
    dict = process_food_search_request(request)
    return render_to_response("food_search.html", dict)
