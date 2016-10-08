# Django imports.
from django.contrib import admin

# Local imports.
from .models import Recipe, Ingredient, Food, Product, Measurement, MeasurementConversion

__author__ = 'Jason Parent'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    fields = ('nk', 'title', 'subtitle', 'desc', 'instructions')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    fields = ('nk', 'recipe', 'food', 'desc', 'amount', 'measurement', 'rank')


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    fields = ('nk', 'name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    fields = ('nk', 'food', 'name', 'price', 'amount', 'measurement')


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    fields = ('nk', 'name', 'abbreviation', 'type', 'unit')


@admin.register(MeasurementConversion)
class MeasurementConversionAdmin(admin.ModelAdmin):
    fields = ('nk', 'food', 'weight', 'weight_measurement', 'volume', 'volume_measurement')
