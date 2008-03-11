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
    name = models.CharField(max_length=60)

    def __unicode__(self):
        return u'%d, %s' % (self.group_id, self.name)

    class Admin:
        pass

def get_food_groups():
    return Food_Group.objects.all().order_by('group_id')

# ------------------------------------------------------------

class Food(models.Model):
    food_id = models.PositiveIntegerField(primary_key=True)
    group = models.ForeignKey(Food_Group, to_field='group_id')
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%d, %d, %s, %s' % (self.food_id, self.group_id, self.name,
                                    self.group.name)

    class Admin:
        pass

def get_food_from_food_str(food_str, gp_id):
    if gp_id == 0:
        return Food.objects.filter(name__icontains = food_str)
    else:
        return Food.objects.filter(
            group__group_id = gp_id).filter(name__icontains = food_str)

def food_id_2_name(food_id):
    o = Food.objects.get(food_id=food_id)
    if o:
        return o.name

# ------------------------------------------------------------

class Nutrient_Definition(models.Model):
    nutrient_id = models.PositiveIntegerField(primary_key=True)
    unit_of_measure = models.CharField(max_length=7)
    name = models.CharField(max_length=60)

    def __unicode__(self):
        return u'%d, %s, %s' % (self.nutrient_id, self.unit_of_measure, self.name)

    class Admin:
        pass

# ------------------------------------------------------------

class Nutrient_Data(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    food_id = models.PositiveIntegerField(db_index=True)
    nutrient = models.ForeignKey(Nutrient_Definition, to_field='nutrient_id')
    value = models.FloatField()

    def __unicode__(self):
        return u'%d, %d, %s, %s, %f' % (self.food_id, self.nutrient.nutrient_id,
                                        self.nutrient.unit_of_measure,
                                        self.nutrient.name, self.value)

    class Admin:
        pass

def get_calories(food_id, selected_measure_id, num_measures):
    value = Nutrient_Data.objects.filter(food_id=food_id).filter(nutrient__nutrient_id=208).get().value
    grams = Measure.objects.filter(food_id=food_id).filter(id=selected_measure_id).get().grams
    calories = value * num_measures * grams / 100.0
    return calories

def get_ingredient_calories(ingredient_form, food_id):
    food_id = int(food_id)
    if ingredient_form.is_valid():
        ingredient_form_data = ingredient_form.cleaned_data
        print 'ingredient_form_data = ', ingredient_form_data
        num_measures = float(ingredient_form_data['num_measures'])
        measure = int(ingredient_form_data['measure'])
        return get_calories(food_id, measure, num_measures)
    else:
        return 0.0

# ------------------------------------------------------------

class Measure(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    food_id = models.PositiveIntegerField(db_index=True)
    measure_id = models.PositiveSmallIntegerField(db_index=True)
    amount = models.FloatField()
    name = models.CharField(max_length=80)
    grams = models.FloatField()

    def __unicode__(self):
        return u'%d, %d, %f, %s, %f' % (self.food_id, self.measure_id, self.amount,
                                        self.name, self.grams)

    class Admin:
        pass

def get_measures(food_id):
    return Measure.objects.filter(food_id=food_id).order_by('measure_id')

# ------------------------------------------------------------

class Nutrient:
    def __init__(self, id, desc, value, unit, percent):
        self.nutr_id = id
        self.nutr_desc = desc
        self.nutr_value = value
        self.unit_of_measure = unit
        self.percent_rdi = percent

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
    nutrient = Nutrient_Container()
    nutrient.general = []
    for nutr_id, unit_of_measure, nutr_desc in tracked_nutrient.general:
        nutrient.general.append(Nutrient(nutr_id,
                                         nutr_desc,
                                         nutr_dict[nutr_id],
                                         unit_of_measure,
                                         percent_rdi(nutr_id, nutr_dict, rdi_dict)))
    nutrient.vitamins = []
    for nutr_id, unit_of_measure, nutr_desc in tracked_nutrient.vitamins:
        nutrient.vitamins.append(Nutrient(nutr_id,
                                          nutr_desc,
                                          nutr_dict[nutr_id],
                                          unit_of_measure,
                                          percent_rdi(nutr_id, nutr_dict, rdi_dict)))
    nutrient.minerals = []
    for nutr_id, unit_of_measure, nutr_desc in tracked_nutrient.minerals:
        nutrient.minerals.append(Nutrient(nutr_id,
                                          nutr_desc,
                                          nutr_dict[nutr_id],
                                          unit_of_measure,
                                          percent_rdi(nutr_id, nutr_dict, rdi_dict)))
    nutrient.amino_acids = []
    for nutr_id, unit_of_measure, nutr_desc in tracked_nutrient.amino_acids:
        nutrient.amino_acids.append(Nutrient(nutr_id,
                                             nutr_desc,
                                             nutr_dict[nutr_id],
                                             unit_of_measure,
                                             percent_rdi(nutr_id, nutr_dict, rdi_dict)))
    nutrient.fats = []
    for nutr_id, unit_of_measure, nutr_desc in tracked_nutrient.fats:
        nutrient.fats.append(Nutrient(nutr_id,
                                      nutr_desc,
                                      nutr_dict[nutr_id],
                                      unit_of_measure,
                                      percent_rdi(nutr_id, nutr_dict, rdi_dict)))
    return nutrient

def get_food_nutrient_data(food_id, amount, selected_measure_id, user):
    nutr_dict = {}
    rdi_dict = {}
    rdis = get_user_rdis(user.id)
    for item in rdis:
        rdi_dict[item.nutrient_id] = item.min_nutrient_value
        nutr_dict[item.nutrient_id] = 0.0

    food_data = Nutrient_Data.objects.filter(food_id = food_id)
    measure = get_measures(food_id)
    grams = measure.filter(id=selected_measure_id).get().grams

    for item in food_data:
        if item.nutrient.nutrient_id in rdi_dict:
            nutr_dict[item.nutrient.nutrient_id] = item.value * amount * grams / 100.0

    nutrients = populate_nutrient_values(nutr_dict, rdi_dict)

    return nutrients


def get_food_database_data(food_id_list):
    all_food_data = list(Nutrient_Data.objects.filter(food_id__in=food_id_list))
    all_measures = list(Measure.objects.filter(food_id__in=food_id_list))
    return all_food_data, all_measures

def get_recipe_database_data(recipe_order):
    all_recipe_data = list(Recipe_Nutrient_Data.objects.filter(recipe__id__in=recipe_order))
    return all_recipe_data

def get_recipe_food_data(food_id, ingredient_form_data, all_food_data, all_measures):
    food_id = int(food_id)
    num_measures = float(ingredient_form_data['num_measures'])
    food_data = [(elm.nutrient_id, elm.value) for elm in all_food_data if elm.food_id == food_id]
    measure = int(ingredient_form_data['measure'])
    for elm in all_measures:
        if elm.id == measure:
            grams = elm.grams
            break
    return food_data, num_measures, grams

def get_plan_food_data(food_id, food_form, all_food_data, all_measures):
    food_id = int(food_id)
    num_measures = float(food_form['num_measures'])
    food_data = [(elm.nutrient_id, elm.value) for elm in all_food_data if elm.food_id == food_id]
    measure = int(food_form['measure'])
    for elm in all_measures:
        if elm.id == measure:
            grams = elm.grams
            break
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
            nutr_dict[nutrient_id] += nutr_val
            if nutrient_id == 208:
                calorie_list[i] = nutr_val
    return nutr_dict, calorie_list

def calculate_plan_nutrient_total(plan_form_list, plan_order):
    nutr_dict = {}
    for id in all_nutrient_ids:
        nutr_dict[id] = 0.0

    food_list = []
    food_form_list = []
    recipe_list = []
    recipe_form_list = []

    for i in range(0, len(plan_order)):
        type, id = plan_order[i]
        if type == 'food':
            food_list.append(id)
            food_form_list.append(plan_form_list[i])
        if type == 'recipe':
            recipe_list.append(id)
            recipe_form_list.append(plan_form_list[i])

    all_food_data, all_measures = get_food_database_data(food_list)
    all_recipe_data = get_recipe_database_data(recipe_list)

    for i in range(0, len(food_list)):
        food_data, num_measures, grams = get_plan_food_data(food_list[i],
                                                            food_form_list[i],
                                                            all_food_data,
                                                            all_measures)
        for nutrient_id, value in food_data:
            nutr_dict[nutrient_id] += value * num_measures * grams / 100.0

    for i in range(0, len(recipe_list)):
        recipe_data, num_measures = get_plan_recipe_data(recipe_list[i],
                                                         recipe_form_list[i],
                                                         all_recipe_data)
        for nutrient_id, value in recipe_data:
            nutr_dict[nutrient_id] += value * num_measures
    return nutr_dict

def set_user_rdis_dict(user):
    rdi_dict = {}
    rdis = get_user_rdis(user.id)
    for item in rdis:
        rdi_dict[item.nutrient_id] = item.min_nutrient_value
    return rdi_dict

def calculate_plan_nutrient_data(user, plan_form_list, plan_order):
    rdi_dict = set_user_rdis_dict(user)
    nutr_dict = calculate_plan_nutrient_total(plan_form_list, plan_order)
    nutrients = populate_nutrient_values(nutr_dict, rdi_dict)
    return nutrients

def calculate_recipe_nutrient_data(user, ingredient_form_list, num_servings):
    rdi_dict = set_user_rdis_dict(user)
    ingredient_form_data_list = []
    food_id_list = []
    for i in range(0, len(ingredient_form_list)):
        ingredient_form_data = ingredient_form_list[i].cleaned_data
        food_id = ingredient_form_data['food_id']
        food_id_list.append(food_id)
        ingredient_form_data_list.append(ingredient_form_data)
    nutr_dict, calorie_list = calculate_recipe_nutrient_total(ingredient_form_data_list,
                                                             food_id_list, num_servings)
    nutrients = populate_nutrient_values(nutr_dict, rdi_dict)
    return nutrients, calorie_list

class RDI_Data:
    def __init__(self, id, desc, min_value, max_value, unit):
        self.nutr_id = id
        self.nutr_desc = desc
        self.min_nutr_value = min_value
        self.max_nutr_value = max_value
        self.unit_of_measure = unit

def get_default_rdi():
    nutrient = Nutrient_Container()
    nutrient.general = []
    for id, unit, desc, min, max in rdi_default.general:
        nutrient.general.append(RDI_Data(id, desc, min, max, unit))
    nutrient.minerals = []
    for id, unit, desc, min, max in rdi_default.minerals:
        nutrient.minerals.append(RDI_Data(id, desc, min, max, unit))
    nutrient.vitamins = []
    for id, unit, desc, min, max in rdi_default.vitamins:
        nmutrient.vitamins.append(RDI_Data(id, desc, min, max, unit))
    mutrient.amino_acids = []
    for id, unit, desc, min, max in rdi_default.amino_acids:
        nutrient.amino_acids.append(RDI_Data(id, desc, min, max, unit))
    nutrient.fats = []
    for id, unit, desc, min, max in rdi_default.fats:
        nutrient.fats.append(RDI_Data(id, desc, min, max, unit))
    return nutrient

# ------------------------------------------------------------

class Recipe_Category(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return u'%d, %s' % (self.id, self.name)

def get_recipe_categories():
    return Recipe_Category.objects.all().order_by('id')

def get_recipe_category(id):
    return Recipe_Category.objects.get(id=id)

# ------------------------------------------------------------

class Recipe(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Recipe_Category, to_field='id')
    number_servings = models.PositiveSmallIntegerField()

    def __unicode__(self):
        return u'%d, %s, %s, %f' % (self.user.id, self.name,
                                    self.category.name,
                                    self.number_servings)

def get_recipes_matching(text, id):
    if id == '0' or id == 0:
        return Recipe.objects.filter(name__icontains=text)
    else:
        return Recipe.objects.filter(category__id=id).filter(name__icontains=text)

def get_recipes_matching_owned_by_user(user, text, id):
    if id == '0' or id == 0:
        return Recipe.objects.filter(user=user).filter(name__icontains=text)
    else:
        return Recipe.objects.filter(user=user).filter(category__id=id).filter(name__icontains=text)

def get_recipe(id):
    return Recipe.objects.filter(id=id).get()

def get_recipe_name(id):
    return Recipe.objects.filter(id=id).get().name

# ------------------------------------------------------------

class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe)
    food = models.ForeignKey(Food, to_field='food_id')
    order = models.PositiveSmallIntegerField()
    measure = models.ForeignKey(Measure)
    number_measures = models.FloatField()

    def __unicode__(self):
        return u'%d, %d, %d, %f, %s, %f' % (self.recipe_id, self.order,
                                            self.measure.food_id,
                                            self.measure.amount,
                                            self.measure.name,
                                            self.number_measures)

def get_ingredients(id):
    return Ingredient.objects.filter(recipe__id=id).order_by('order')


# ------------------------------------------------------------

class Recipe_Nutrient_Data(models.Model):
    recipe = models.ForeignKey(Recipe)
    nutrient = models.ForeignKey(Nutrient_Definition, to_field='nutrient_id')
    value = models.FloatField()

    def __unicode__(self):
        return u'%d, %d, %s, %s, %f' % (self.recipe.id, self.nutrient.nutrient_id,
                                        self.nutrient.unit_of_measure,
                                        self.nutrient.name, self.value)

def get_recipe_nutrient_data(id):
    return Recipe_Nutrient_Data.objects.filter(recipe__id=id)

# ------------------------------------------------------------

# class recipe_preparation(models.Model):
#     recipe = models.PositiveIntegerField(primary_key=True)
#     preparation_desc = models.TextField()

@transaction.commit_on_success
def save_recipe_to_database(user, recipe_form, ingredient_form_list):
    recipe_form_data = recipe_form.cleaned_data
    old_recipes = Recipe.objects.filter(user=user).filter(name=recipe_form_data['name'])
    for o in old_recipes:
        Ingredient.objects.filter(recipe__id=o.id).delete()
        Recipe_Nutrient_Data.objects.filter(recipe__id=o.id).delete()
        o.delete()
    num_servings = recipe_form_data['num_servings']
    r = Recipe(user=user, name=recipe_form_data['name'], category_id=recipe_form_data['category'],
               number_servings=num_servings)
    r.save()
    ingredient_form_data_list = []
    food_id_list = []
    for i in range(0, len(ingredient_form_list)):
        ingredient_form_data = ingredient_form_list[i].cleaned_data
        food_id = ingredient_form_data['food_id']
        food_id_list.append(food_id)
        ingredient_form_data_list.append(ingredient_form_data)
        ing = Ingredient(order=i, measure_id=ingredient_form_data['measure'],
                         food_id=food_id,
                         number_measures=ingredient_form_data['num_measures'],
                         recipe_id=r.id)
        ing.save()
    nutr_dict, calorie_list = calculate_recipe_nutrient_total(ingredient_form_data_list,
                                                              food_id_list,
                                                              num_servings)
    for key, val in nutr_dict.items():
        d = Recipe_Nutrient_Data(recipe_id = r.id, nutrient_id=key, value=val)
        d.save()

# -----------------------------------------------------------------

class User_Rdi(models.Model):
    user = models.ForeignKey(User, to_field='id')
    nutrient_id = models.PositiveIntegerField()
    min_nutrient_value = models.FloatField()
    max_nutrient_value = models.FloatField()

    def __unicode__(self):
        return u'%d, %d, %f, %f' % (self.user.id, self.nutrient_id,
                                    self.min_nutrient_value, self.max_nutrient_value)


def get_user_rdis(id):
    return User_Rdi.objects.filter(user__id=id)

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
    for n in range(len(tracked_nutrient.general)):
        nutr_id, unit, desc = tracked_nutrient.general[n]
        data = nutrients.general[n].cleaned_data
        r = User_Rdi(user=user, nutrient_id=nutr_id, min_nutrient_value = data['min'],
                     max_nutrient_value = data['max'])
        r.save()
    for n in range(len(tracked_nutrient.minerals)):
        nutr_id, unit, desc = tracked_nutrient.minerals[n]
        data = nutrients.minerals[n].cleaned_data
        r = User_Rdi(user=user, nutrient_id=nutr_id, min_nutrient_value = data['min'],
                     max_nutrient_value = data['max'])
        r.save()
    for n in range(len(tracked_nutrient.vitamins)):
        nutr_id, unit, desc = tracked_nutrient.vitamins[n]
        data = nutrients.vitamins[n].cleaned_data
        r = User_Rdi(user=user, nutrient_id=nutr_id, min_nutrient_value = data['min'],
                     max_nutrient_value = data['max'])
        r.save()
    for n in range(len(tracked_nutrient.amino_acids)):
        nutr_id, unit, desc = tracked_nutrient.amino_acids[n]
        data = nutrients.amino_acids[n].cleaned_data
        r = User_Rdi(user=user, nutrient_id=nutr_id, min_nutrient_value = data['min'],
                     max_nutrient_value = data['max'])
        r.save()
    for n in range(len(tracked_nutrient.fats)):
        nutr_id, unit, desc = tracked_nutrient.fats[n]
        data = nutrients.fats[n].cleaned_data
        r = User_Rdi(user=user, nutrient_id=nutr_id, min_nutrient_value = data['min'],
                     max_nutrient_value = data['max'])
        r.save()

# -----------------------------------------------------------------

class Nutrient_Score(models.Model):
    food = models.ForeignKey(Food, to_field='food_id', primary_key=True)
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
    nutrient = models.ForeignKey(Nutrient_Definition, to_field='nutrient_id', primary_key=True)
    avg = models.FloatField()
    max = models.FloatField()

def get_max_dict():
    dict = {}
    objs = Nutrient_Score_Max.objects.all()
    for o in objs:
        dict[o.nutrient_id] = o.max
    return dict

# -----------------------------------------------------------------

class Plan(models.Model):
    user = models.ForeignKey(User, to_field='id')
    plan_date = models.DateField(db_index=True)
    item_type = models.CharField(max_length=1)
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
            measure = plan_data['measure'],
        else:
            item_type = 'R'
            measure = 0
        o = Plan(order=i, user=user, plan_date=plan_date, measure=measure,
                 item_id=item_id, item_type=item_type,
                 num_measures=plan_data['num_measures'],
                 name=plan_data['name'])
        o.save()

def get_user_plan(user, year, month, day):
    plan_date = datetime.date(int(year), int(month), int(day))
    plan_list = Plan.objects.filter(user=user).filter(plan_date=plan_date).order_by('order')
    return plan_list
