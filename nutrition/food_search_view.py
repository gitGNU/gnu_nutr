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

class FoodSearchForm(forms.Form):
    text = forms.CharField(max_length=60)
    food_group = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(FoodSearchForm, self).__init__(*args, **kwargs)
        self.fields['food_group'].choices = [(g.group_id, g.name) for g in get_food_groups()]

@login_required
def food_search( request):
    if request.method == 'GET':
        form = FoodSearchForm(request.GET)
        if form.is_valid():
            search_text = form.cleaned_data['text']
            food_group = int(form.cleaned_data['food_group'])
            foods = get_food_from_food_str(search_text, food_group)
        else:
            search_text = ""
            foods = []
    else:
        search_text = ""
        form = FoodSearchForm()
        foods = []

    return render_to_response("food_search.html", {
            "search_text": search_text,
            "form": form,
            "foods": foods})
