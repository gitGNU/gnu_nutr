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

from django.conf.urls.defaults import *
from django.conf import settings

from nutr.nutrition.selected_food_view import selected_food
from nutr.nutrition.food_search_view import food_search
from nutr.nutrition.menu_view import menu
from nutr.nutrition.recipe_view import create_recipe
from nutr.nutrition.ingredient_search_view import add_ingredient
from nutr.nutrition.daily_plan_view import daily_plan
from nutr.nutrition.plan_add_food_view import plan_add_food
from nutr.nutrition.plan_add_recipe_view import plan_add_recipe
from nutr.nutrition.nutrient_search_view import nutrient_search
from nutr.nutrition.nutrient_search_result_view import nutrient_search_result
from nutr.nutrition.search_recipe_view import search_recipe, search_edit_recipe
from nutr.nutrition.selected_recipe_view import selected_recipe
from nutr.nutrition.set_rdi_view import set_rdi
from nutr.nutrition.register import register
from django.contrib.auth.views import login, logout


urlpatterns = \
    patterns('',
             (r'^menu/$', menu),
             (r'^accounts/login/$', login),
             (r'register/$', register),
             (r'set_rdi/$', set_rdi),
             (r'food_search/$', food_search),
             (r'create_recipe/$', create_recipe),
             (r'create_recipe/(?P<food_id>\d+)/$', create_recipe),
             (r'food_search/food_id/(?P<food_id>\d+)/measure/(?P<measure>\d+)/num_measures/(?P<num_measures>(\b[0-9]{0,5}?\.[0-9]*\b|\b[0-9]{0,5}?\b|\.[0-9]*\b))$', selected_food),
             (r'add_ingredient/$', add_ingredient),
             (r'food_search/food_id/(?P<food_id>\d+)/$', selected_food),
             (r'nutrient_search_result/food_id/(?P<food_id>\d+)/$', selected_food),
             (r'search_recipe/recipe_id/(?P<recipe_id>\d+)/$', selected_recipe),
             (r'search_recipe/$', search_recipe),
             (r'nutrient_search/$', nutrient_search),
             (r'nutrient_search_result/$', nutrient_search_result),
             (r'edit_recipe/recipe_id/(?P<recipe_id>\d+)/$', create_recipe),
             (r'search_edit_recipe/$', search_edit_recipe),
             (r'daily_plan/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', daily_plan),
             (r'daily_plan/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/food_id/(?P<food_id>\d+)/$', daily_plan),
             (r'daily_plan/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/recipe_id/(?P<recipe_id>\d+)/$', daily_plan),
#             (r'daily_plan/food_id/(?P<food_id>\d+)/$', daily_plan),
#             (r'daily_plan/recipe_id/(?P<recipe_id>\d+)/$', daily_plan),
             (r'daily_plan/\d{4}/\d{1,2}/\d{1,2}/add_food/$', plan_add_food),
             (r'daily_plan/\d{4}/\d{1,2}/\d{1,2}/add_recipe/$', plan_add_recipe),
             (r'daily_plan/$', daily_plan))

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
