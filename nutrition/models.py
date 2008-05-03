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

from django.db import models
from constants import *
from django.contrib.auth.models import *
from django.db import transaction, connection
import datetime

class Food_Group(models.Model):
    group_id = models.PositiveIntegerField(primary_key=True)
    group_name = models.CharField(max_length=60)

    def __unicode__(self):
        return u'%d, %s' % (self.group_id, self.group_name)

    class Admin:
        pass

def get_food_groups():
    return Food_Group.objects.all().order_by('group_id')

# ------------------------------------------------------------

class Food(models.Model):
    food_id = models.PositiveIntegerField(primary_key=True)
    group_id = models.PositiveIntegerField()
    food_name = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%d, %d, %s' % (self.food_id, self.group_id, self.food_name)

    class Admin:
        pass

def get_food_from_food_str(food_str, group_id):
    if group_id == 0:
        return Food.objects.filter(food_name__icontains = food_str)
    else:
        return Food.objects.filter(group_id = group_id).filter(food_name__icontains = food_str)

def food_id_2_name(food_id):
    return Food.objects.get(food_id=food_id).food_name

def get_foods_from_food_id_list(food_id_list):
    return Food.objects.filter(food_id__in=food_id_list)

def get_food_from_food_list(food_list, food_id):
    for food in food_list:
        if food.food_id == int(food_id):
            return food
    return None

# ------------------------------------------------------------

# class Nutrient_Definition(models.Model):
#     nutrient_id = models.PositiveIntegerField(primary_key=True)
#     unit_of_measure = models.CharField(max_length=7)
#     nutrient_name = models.CharField(max_length=60)

#     def __unicode__(self):
#         return u'%d, %s, %s' % (self.nutrient_id, self.unit_of_measure, self.name)

#     class Admin:
#         pass

# ------------------------------------------------------------

class Nutrient_Data(models.Model):
    nutrient_data_id = models.PositiveIntegerField(primary_key=True)
    food_id = models.PositiveIntegerField(db_index=True)
    nutrient_id = models.PositiveIntegerField()
    value = models.FloatField()

    def __unicode__(self):
        return u'%d, %d, %g' % (self.food_id, self.nutrient_id,
                                self.value)

    class Admin:
        pass

def get_calories_per_100gm(food_id):
    return Nutrient_Data.objects.filter(food_id=food_id).filter(nutrient_id=208).get().value

def get_nutrient_data_for_food(food_id):
    return Nutrient_Data.objects.filter(food_id=food_id)

# ------------------------------------------------------------

class Measure(models.Model):
    measure_id = models.PositiveIntegerField(primary_key=True)
    food_id = models.PositiveIntegerField(db_index=True)
    measure_name = models.CharField(max_length=80)
    grams = models.FloatField()

    def __unicode__(self):
        return u'%d, %d, %s, %f' % (self.food_id, self.measure_id,
                                    self.measure_name, self.grams)

    class Admin:
        pass

def get_measures(food_id):
    return Measure.objects.filter(food_id=food_id).order_by('measure_id')

def get_food_list_measures(food_id_list):
    return Measure.objects.filter(food_id__in=food_id_list).order_by('measure_id')

def get_measure_from_measure_list(measure_list, measure_id):
    for m in measure_list:
        if m.measure_id == measure_id:
            return m
    return None

def get_grams_per_measure(food_id, measure_id):
    return Measure.objects.filter(food_id=food_id).filter(measure_id=measure_id).get().grams

# ------------------------------------------------------------

def get_calories(food_id, measure_id, num_measures):
    calories_per_100gm = get_calories_per_100gm(food_id)
    grams_per_measure = get_grams_per_measure(food_id, measure_id)
    return calories_per_100gm * num_measures * grams_per_measure / 100.0

def get_ingredient_calories(ingredient_form, food_id):
    food_id = int(food_id)
    if ingredient_form.is_valid():
        ingredient_form_data = ingredient_form.cleaned_data
        num_measures = float(ingredient_form_data['num_measures'])
        measure = int(ingredient_form_data['measure'])
        return get_calories(food_id, measure, num_measures)
    else:
        return 0.0

# ------------------------------------------------------------

class Nutrient:
    def __init__(self, id, desc, value, unit, percent):
        self.nutr_id = id
        self.nutr_desc = desc
        self.nutr_value = value
        self.unit_of_measure = unit
        self.percent_rdi = percent
        if percent > 100.0:
            self.width = 100
        else:
            self.width = percent

def value_or_zero(dict, key):
    if key in dict:
        return dict[key]
    else:
        return 0.0

def percent_rdi(key, nutr_dict, rdi_dict):
    if rdi_dict[key] != 0.0:
        return 100.0 * nutr_dict[key] / rdi_dict[key]
    else:
        return 0.0

class Nutrient_Container:
    pass

def populate_nutrient_values(nutr_dict, rdi_dict):
    nutrient = {}
    nutr_groups = ['general', 'vitamins', 'minerals', 'amino_acids', 'fats']
    for group in nutr_groups:
        nutrient[group] = []
        for nutr_id, unit_of_measure, nutr_desc, min_val, max_val in tracked_nutrient[group]:
            nutrient[group].append(Nutrient(nutr_id,
                                           nutr_desc,
                                           nutr_dict[nutr_id],
                                           unit_of_measure,
                                           percent_rdi(nutr_id, nutr_dict, rdi_dict)))
    return nutrient

def get_food_nutrient_data(food_id, num_measures, measure_id, user):
    nutr_dict = {}
    rdi_dict = {}
    rdis = get_user_rdis(user)
    for item in rdis:
        rdi_dict[item.nutrient_id] = item.min_nutrient_value
        nutr_dict[item.nutrient_id] = 0.0

    nutrient_data_list = get_nutrient_data_for_food(food_id)
    grams = get_grams_per_measure(food_id, measure_id)

    for o in nutrient_data_list:
        if o.nutrient_id in rdi_dict:
            nutr_dict[o.nutrient_id] = o.value * num_measures * grams / 100.0

    nutrients = populate_nutrient_values(nutr_dict, rdi_dict)

    return nutrients


def get_food_database_data(food_id_list):
    # We perform just one query of the database to get all the necessary data.
    all_food_data = list(Nutrient_Data.objects.filter(food_id__in=food_id_list))
    all_measures = list(Measure.objects.filter(food_id__in=food_id_list))
    return all_food_data, all_measures

def get_recipe_database_data(recipe_order):
    all_recipe_data = list(Recipe_Nutrient_Data.objects.filter(recipe_id__in=recipe_order))
    return all_recipe_data

def get_grams_from_measure_list(measure_list, measure_id):
    for o in measure_list:
        if o.measure_id == measure_id:
            return o.grams
    return None

def get_recipe_food_data(food_id, ingredient_form_data, all_food_data, all_measures):
    food_id = int(food_id)
    num_measures = float(ingredient_form_data['num_measures'])
    food_data = [(elm.nutrient_id, elm.value) for elm in all_food_data if elm.food_id == food_id]
    grams = get_grams_from_measure_list(all_measures, int(ingredient_form_data['measure']))
    return food_data, num_measures, grams

# -----------------------------------------------------------------
def get_plan_food_data(food_id, food_form, all_food_data, all_measures):
    food_id = int(food_id)
    num_measures = float(food_form['num_measures'])
    food_data = [(elm.nutrient_id, elm.value) for elm in all_food_data if elm.food_id == food_id]
    measure_id = int(food_form['measure'])
    grams = get_grams_from_measure_list(all_measures, measure_id)
    return food_data, num_measures, grams

def get_plan_recipe_data(recipe_id, recipe_form, all_recipe_data):
    recipe_id = int(recipe_id)
    num_measures = float(recipe_form['num_measures'])
    recipe_data = [(elm.nutrient_id, elm.value) for elm in all_recipe_data \
                       if elm.recipe_id == recipe_id]
    return recipe_data, num_measures

def calculate_recipe_nutrient_total(ingredient_form_data_list, food_id_list, num_servings):
    nutr_dict = {}
    calorie_list = []
    for id in food_id_list:
        calorie_list.append(0.0)
    for id in all_nutrient_ids:
        nutr_dict[id] = 0.0
    all_food_data, all_measures = get_food_database_data(food_id_list)
    for i in range(0, len(food_id_list)):
        food_data, num_measures, grams = \
            get_recipe_food_data(food_id_list[i], ingredient_form_data_list[i],
                                 all_food_data, all_measures)
        for nutrient_id, value in food_data:
            nutr_val = value * num_measures * grams / (100.0 * float(num_servings))
            if nutrient_id in all_nutrient_ids:
                nutr_dict[nutrient_id] += nutr_val
            if nutrient_id == 208:
                calorie_list[i] = nutr_val
    return nutr_dict, calorie_list

def calculate_plan_nutrient_total(plan_form_data_list, plan_order):
    nutr_dict = {}
    for id in all_nutrient_ids:
        nutr_dict[id] = 0.0

    calorie_dict = {}
    food_list = []
    food_form_data_list = []
    recipe_list = []
    recipe_form_data_list = []

    for i in range(0, len(plan_order)):
        type, id = plan_order[i]
        if type == 'food':
            food_list.append(id)
            food_form_data_list.append(plan_form_data_list[i])
        if type == 'recipe':
            recipe_list.append(id)
            recipe_form_data_list.append(plan_form_data_list[i])
    all_food_data, all_measures = get_food_database_data(food_list)
    all_recipe_data = get_recipe_database_data(recipe_list)

    for i in range(0, len(food_list)):
        food_data, num_measures, grams = get_plan_food_data(food_list[i],
                                                            food_form_data_list[i],
                                                            all_food_data,
                                                            all_measures)
        for nutrient_id, value in food_data:
            nutr_val = value * num_measures * grams / 100.0
            if nutrient_id in all_nutrient_ids:
                nutr_dict[nutrient_id] += nutr_val
            if nutrient_id == 208:
                calorie_dict['%s_food' % food_list[i]] = nutr_val

    for i in range(0, len(recipe_list)):
        recipe_data, num_measures = get_plan_recipe_data(recipe_list[i],
                                                         recipe_form_data_list[i],
                                                         all_recipe_data)
        for nutrient_id, value in recipe_data:
            nutr_val = value * num_measures
            if nutrient_id in all_nutrient_ids:
                nutr_dict[nutrient_id] += nutr_val
            if nutrient_id == 208:
                calorie_dict['%s_recipe' % recipe_list[i]] = nutr_val
    return nutr_dict, calorie_dict

# -----------------------------------------------------------------

def set_user_rdis_dict(user):
    rdi_dict = {}
    rdis = get_user_rdis(user)
    for item in rdis:
        rdi_dict[item.nutrient_id] = item.min_nutrient_value
    return rdi_dict

def calculate_plan_nutrient_data(user, plan_form_data_list, plan_order):
    rdi_dict = set_user_rdis_dict(user)
    nutr_dict, calorie_dict = calculate_plan_nutrient_total(plan_form_data_list, plan_order)
    nutrients = populate_nutrient_values(nutr_dict, rdi_dict)
    return nutrients, calorie_dict

def calculate_recipe_nutrient_data(user, ingredient_form_list, num_servings, food_id_list):
    rdi_dict = set_user_rdis_dict(user)
    ingredient_form_data_list = []
    for i in range(0, len(ingredient_form_list)):
        ingredient_form_data = ingredient_form_list[i].cleaned_data
        ingredient_form_data_list.append(ingredient_form_data)
    nutr_dict, calorie_list = calculate_recipe_nutrient_total(ingredient_form_data_list,
                                                             food_id_list, num_servings)
    nutrients = populate_nutrient_values(nutr_dict, rdi_dict)
    return nutrients, calorie_list

class RDI_Data:
    def __init__(self, nutrient_id, min_value, max_value):
        self.nutrient_id = nutrient_id
        self.min_nutrient_value = min_value
        self.max_nutrient_value = max_value

def get_default_rdi():
    rdi_list = []
    nutr_groups = ['general', 'vitamins', 'minerals', 'amino_acids', 'fats']
    for group in nutr_groups:
        for nutr_id, unit, desc, min_val, max_val in rdi_default[group]:
            rdi_list.append(RDI_Data(nutr_id, min_val, max_val))
    return rdi_list

# ------------------------------------------------------------

class Recipe_Category(models.Model):
    category_id = models.PositiveIntegerField(primary_key=True)
    category_name = models.CharField(max_length=50)

    def __unicode__(self):
        return u'%d, %s' % (self.category_id, self.category_name)

def get_recipe_categories():
    return Recipe_Category.objects.all().order_by('category_id')

def get_recipe_category(category_id):
    return Recipe_Category.objects.get(category_id=category_id)

# ------------------------------------------------------------

class Recipe(models.Model):
    recipe_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    recipe_name = models.CharField(max_length=100)
    category_id = models.PositiveIntegerField()
    category_name = models.CharField(max_length=50)
    number_servings = models.PositiveSmallIntegerField()

    def __unicode__(self):
        return u'%d, %s, %s, %f' % (self.user.id, self.recipe_name,
                                    self.category_id,
                                    self.number_servings)

def get_recipes_matching(text, category_id):
    if category_id == '0' or category_id == 0:
        return Recipe.objects.filter(recipe_name__icontains=text)
    else:
        return Recipe.objects.filter(category_id=category_id).filter(recipe_name__icontains=text)

def get_recipes_matching_owned_by_user(user, text, category_id):
    if category_id == '0' or category_id == 0:
        return Recipe.objects.filter(user=user).filter(recipe_name__icontains=text)
    else:
        return Recipe.objects.filter(user=user).filter(category_id=category_id).filter(recipe_name__icontains=text)

def get_recipe_exact_match_owned_by_user(user, recipe_name):
    o = Recipe.objects.filter(user=user).filter(recipe_name=recipe_name)
    if o:
        return o[0]
    return None

def get_recipe(recipe_id):
    return Recipe.objects.filter(recipe_id=recipe_id).get()

def get_recipe_name(recipe_id):
    return Recipe.objects.filter(recipe_id=recipe_id).get().recipe_name

# ------------------------------------------------------------

class Ingredient(models.Model):
    ingredient_id = models.AutoField(primary_key=True)
    recipe_id = models.PositiveIntegerField(db_index=True)
    food_id = models.PositiveIntegerField()
    food_name = models.CharField(max_length=200)
    order = models.PositiveSmallIntegerField()
    measure_id = models.PositiveIntegerField()
    measure_name = models.CharField(max_length=80)
    number_measures = models.FloatField()

    def __unicode__(self):
        return u'%d, %d, %d, %d, %f' % (self.recipe_id, self.order,
                                        self.food_id,
                                        self.measure_id,
                                        self.number_measures)

def get_ingredients(recipe_id):
    return Ingredient.objects.filter(recipe_id=recipe_id).order_by('order')

# ------------------------------------------------------------

class Recipe_Nutrient_Data(models.Model):
    recipe_nutrient_id = models.AutoField(primary_key=True)
    recipe_id = models.PositiveIntegerField(db_index=True)
    nutrient_id = models.PositiveIntegerField()
    value = models.FloatField()

    def __unicode__(self):
        return u'%d, %d, %f' % (self.recipe_id, self.nutrient_id, self.value)

def get_recipe_nutrient_data(recipe_id):
    return Recipe_Nutrient_Data.objects.filter(recipe_id=recipe_id)

# ------------------------------------------------------------

# class recipe_preparation(models.Model):
#     recipe = models.PositiveIntegerField(primary_key=True)
#     preparation_desc = models.TextField()

@transaction.commit_on_success
def save_recipe_to_database(user, recipe_form, ingredient_form_list, food_id_list):
    recipe_form_data = recipe_form.cleaned_data

    # TODO: could probably do a search on recipe_id rather than a name search.
    old_recipe = get_recipe_exact_match_owned_by_user(user, recipe_form_data['name'])
    if old_recipe:
        old_recipe_id = old_recipe.recipe_id
        Ingredient.objects.filter(recipe_id=old_recipe_id).delete()
        Recipe_Nutrient_Data.objects.filter(recipe_id=old_recipe_id).delete()
        old_recipe.delete()

    num_servings = recipe_form_data['num_servings']
    category_id = recipe_form_data['category']

    if old_recipe:
        r = Recipe(user=user,
                   recipe_id=old_recipe_id,
                   recipe_name=recipe_form_data['name'],
                   category_id=category_id,
                   category_name=get_recipe_category(category_id).category_name,
                   number_servings=num_servings)
    else:
        r = Recipe(user=user,
                   recipe_name=recipe_form_data['name'],
                   category_id=category_id,
                   category_name=get_recipe_category(category_id).category_name,
                   number_servings=num_servings)
    r.save()
    ingredient_form_data_list = []

    # Avoid a set of queries for each loop, so get all the data before looping
    ingredient_measure_list = get_food_list_measures(food_id_list)
    ingredient_food_list = get_foods_from_food_id_list(food_id_list)

    for i in range(0, len(ingredient_form_list)):
        ingredient_form_data = ingredient_form_list[i].cleaned_data
        food_id = food_id_list[i]
        measure_id = int(ingredient_form_data['measure'])
        m = get_measure_from_measure_list(ingredient_measure_list, measure_id)
        f = get_food_from_food_list(ingredient_food_list, food_id)
        ingredient_form_data_list.append(ingredient_form_data)
        ing = Ingredient(order=i,
                         measure_id=measure_id,
                         measure_name=m.measure_name,
                         food_id=food_id,
                         food_name=f.food_name,
                         number_measures=ingredient_form_data['num_measures'],
                         recipe_id=r.recipe_id)
        ing.save()
    nutr_dict, calorie_list = calculate_recipe_nutrient_total(ingredient_form_data_list,
                                                              food_id_list,
                                                              num_servings)
    for key, val in nutr_dict.items():
        d = Recipe_Nutrient_Data(recipe_id=r.recipe_id, nutrient_id=key, value=val)
        d.save()

# -----------------------------------------------------------------

class User_Rdi(models.Model):
    user = models.ForeignKey(User)
    nutrient_id = models.PositiveIntegerField()
    min_nutrient_value = models.FloatField()
    max_nutrient_value = models.FloatField()

    def __unicode__(self):
        return u'%d, %d, %g, %g' % (self.user.id, self.nutrient_id,
                                    self.min_nutrient_value, self.max_nutrient_value)


def get_user_rdis(user):
    return User_Rdi.objects.filter(user=user)

def get_user_rdis_dict(user):
    dict = {}
    results = User_Rdi.objects.filter(user=user)
    for o in results:
        dict[o.nutrient_id] = o.min_nutrient_value
    return dict

@transaction.commit_on_success
def save_rdi_to_database(user, nutrients):
    old_rdis = User_Rdi.objects.filter(user=user)
    for o in old_rdis:
        o.delete()
    nutr_groups = ['general', 'vitamins', 'minerals', 'amino_acids', 'fats']
    for group in nutr_groups:
        for n in range(len(tracked_nutrient[group])):
            nutr_id, unit, desc, min_val, max_val = tracked_nutrient[group][n]
            data = nutrients[group][n].cleaned_data
            r = User_Rdi(user=user, nutrient_id=nutr_id, min_nutrient_value = data['min'],
                         max_nutrient_value = data['max'])
            r.save()

# -----------------------------------------------------------------

class Nutrient_Score(models.Model):
    food_id = models.PositiveIntegerField(primary_key=True)
    food_name = models.CharField(max_length=200)
    group_id = models.PositiveIntegerField()
    value_203 = models.FloatField()
    value_204 = models.FloatField()
    value_205 = models.FloatField()
    value_291 = models.FloatField()
    value_209 = models.FloatField()
    value_269 = models.FloatField()
    value_221 = models.FloatField()
    value_255 = models.FloatField()
    value_262 = models.FloatField()
    value_301 = models.FloatField()
    value_303 = models.FloatField()
    value_304 = models.FloatField()
    value_305 = models.FloatField()
    value_306 = models.FloatField()
    value_307 = models.FloatField()
    value_309 = models.FloatField()
    value_312 = models.FloatField()
    value_315 = models.FloatField()
    value_317 = models.FloatField()
    value_318 = models.FloatField()
    value_319 = models.FloatField()
    value_321 = models.FloatField()
    value_322 = models.FloatField()
    value_334 = models.FloatField()
    value_337 = models.FloatField()
    value_338 = models.FloatField()
    value_404 = models.FloatField()
    value_405 = models.FloatField()
    value_406 = models.FloatField()
    value_410 = models.FloatField()
    value_415 = models.FloatField()
    value_417 = models.FloatField()
    value_418 = models.FloatField()
    value_401 = models.FloatField()
    value_324 = models.FloatField()
    value_323 = models.FloatField()
    value_341 = models.FloatField()
    value_342 = models.FloatField()
    value_343 = models.FloatField()
    value_430 = models.FloatField()
    value_501 = models.FloatField()
    value_502 = models.FloatField()
    value_503 = models.FloatField()
    value_504 = models.FloatField()
    value_505 = models.FloatField()
    value_506 = models.FloatField()
    value_507 = models.FloatField()
    value_508 = models.FloatField()
    value_509 = models.FloatField()
    value_510 = models.FloatField()
    value_511 = models.FloatField()
    value_512 = models.FloatField()
    value_513 = models.FloatField()
    value_514 = models.FloatField()
    value_515 = models.FloatField()
    value_516 = models.FloatField()
    value_517 = models.FloatField()
    value_518 = models.FloatField()
    value_606 = models.FloatField()
    value_645 = models.FloatField()
    value_646 = models.FloatField()
    value_605 = models.FloatField()
    value_601 = models.FloatField()
    value_636 = models.FloatField()
    value_618 = models.FloatField()
    value_675 = models.FloatField()
    value_851 = models.FloatField()
    value_629 = models.FloatField()
    value_621 = models.FloatField()
    value_619 = models.FloatField()
    value_620 = models.FloatField()

def my_custom_sql(query_text):
    cursor = connection.cursor()
    cursor.execute(query_text)
    rows = cursor.fetchall()
    return rows

# -----------------------------------------------------------------

class Nutrient_Score_Max(models.Model):
    nutrient_id = models.PositiveIntegerField(primary_key=True)
    avg_score = models.FloatField()
    max_score = models.FloatField()

def get_max_dict():
    dict = {}
    objs = Nutrient_Score_Max.objects.all()
    for o in objs:
        dict[o.nutrient_id] = o.max_score
    return dict

# -----------------------------------------------------------------

class Plan(models.Model):
    user = models.ForeignKey(User)
    plan_date = models.DateField(db_index=True)
    # item_type 'F' = food, 'R' = recipe
    item_type = models.CharField(max_length=1)
    # contains either food_id or recipe_id
    item_id = models.PositiveIntegerField()
    order = models.PositiveSmallIntegerField()
    measure = models.PositiveIntegerField()
    num_measures = models.FloatField()
    name = models.CharField(max_length=200)

    def get_year(self):
        self.plan_date.strftime('%Y')

    def get_month(self):
        self.plan_date.strftime('%m')

    def get_day(self):
        self.plan_date.strftime('%d')

@transaction.commit_on_success
def save_plan_to_database(user, plan_form_list, plan_order, year, month, day):
    plan_date = datetime.date(int(year), int(month), int(day))
    old_plan = Plan.objects.filter(user=user).filter(plan_date=plan_date)
    for o in old_plan:
        o.delete()
    for i in range(0, len(plan_form_list)):
        plan_data = plan_form_list[i].cleaned_data
        type, item_id = plan_order[i]
        if type == 'food':
            item_type = 'F'
            measure = plan_data['measure']
            name = food_id_2_name(item_id)
        else:
            item_type = 'R'
            measure = 0
            name = get_recipe_name(item_id)
        o = Plan(order=i, user=user, plan_date=plan_date, measure=measure,
                 item_id=item_id, item_type=item_type,
                 num_measures=plan_data['num_measures'],
                 name=name)
        o.save()

def get_user_plan(user, year, month, day):
    plan_date = datetime.date(int(year), int(month), int(day))
    plan_list = Plan.objects.filter(user=user).filter(plan_date=plan_date).order_by('order')
    return plan_list
