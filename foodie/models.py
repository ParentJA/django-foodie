# Standard library imports.
import decimal

# Django imports.
from django.db import models

__author__ = 'Jason Parent'

QUANTITY = 'QUANTITY'
WEIGHT = 'WEIGHT'
VOLUME = 'VOLUME'

TEASPOON = 'TEASPOON'
TABLESPOON = 'TABLESPOON'
CUP = 'CUP'
PINT = 'PINT'
QUART = 'QUART'
GALLON = 'GALLON'
OUNCE = 'OUNCE'
POUND = 'POUND'


class NKField(models.CharField):
    """A unique natural key."""

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 255
        kwargs['unique'] = True

        super(NKField, self).__init__(*args, **kwargs)


class NKMixin(object):
    def natural_key(self):
        return [getattr(self, 'nk')]


class NKManager(models.Manager):
    def get_by_natural_key(self, nk):
        return self.get(nk=nk)


class RecipeManager(NKManager):
    def allergens(self, allergens):
        # Find all ingredients that contain allergens.
        food_x_allergen_qs = FoodXAllergen.objects.select_related('food').filter(allergen__in=allergens)
        foods = set([food_x_allergen.food for food_x_allergen in food_x_allergen_qs])
        ingredient_qs = Ingredient.objects.select_related('recipe').filter(food__in=foods)

        # Find all recipes that do not have ingredients the contain allergens.
        return self.exclude(nk__in=[ingredient.recipe for ingredient in ingredient_qs]).distinct()


class Recipe(models.Model, NKMixin):
    """A set of instructions that describes how to prepare a culinary dish."""

    objects = RecipeManager()

    nk = NKField()

    title = models.CharField(max_length=255)

    subtitle = models.CharField(max_length=255, null=True, blank=True)

    desc = models.TextField(null=True, blank=True)

    instructions = models.TextField(null=True, blank=True)

    class Meta(object):
        app_label = 'foodie'

    def __unicode__(self):
        return self.nk


class Ingredient(models.Model, NKMixin):
    """A food that forms part of a recipe."""

    objects = NKManager()

    nk = NKField(help_text='e.g. {recipe.nk}$${food.nk}')

    recipe = models.ForeignKey('foodie.Recipe')

    food = models.ForeignKey('foodie.Food')

    desc = models.TextField()

    amount = models.DecimalField(decimal_places=3, max_digits=6, null=True, blank=True)

    measurement = models.ForeignKey('foodie.Measurement', null=True, blank=True)

    rank = models.IntegerField(default=0)

    class Meta(object):
        app_label = 'foodie'
        default_related_name = 'ingredients'

    def __unicode__(self):
        return self.nk


class Food(models.Model, NKMixin):
    """A substance consumed to provide nutritional support for the body."""

    objects = NKManager()

    nk = NKField()

    name = models.CharField(max_length=255)

    class Meta(object):
        app_label = 'foodie'

    def __unicode__(self):
        return self.nk


class Product(models.Model, NKMixin):
    """A food item for sale."""

    objects = NKManager()

    nk = NKField()

    food = models.ForeignKey('foodie.Food')

    name = models.CharField(max_length=255)

    price = models.DecimalField(decimal_places=2, max_digits=6)

    amount = models.DecimalField(decimal_places=3, max_digits=6)

    measurement = models.ForeignKey('foodie.Measurement')

    class Meta(object):
        app_label = 'foodie'
        default_related_name = 'products'

    def __unicode__(self):
        return self.nk

    @property
    def price_per_unit(self):
        return self.price / self.amount


class Measurement(models.Model, NKMixin):
    """A unit of measure."""

    TYPE = (
        (QUANTITY, QUANTITY),
        (WEIGHT, WEIGHT),
        (VOLUME, VOLUME)
    )
    UNIT = (
        (TEASPOON, TEASPOON),
        (TABLESPOON, TABLESPOON),
        (CUP, CUP),
        (PINT, PINT),
        (QUART, QUART),
        (GALLON, GALLON),
        (OUNCE, OUNCE),
        (POUND, POUND)
    )

    objects = NKManager()

    nk = NKField()

    name = models.CharField(max_length=255)

    abbreviation = models.CharField(max_length=255, null=True, blank=True)

    type = models.CharField(max_length=255, choices=TYPE)

    unit = models.CharField(max_length=255, choices=UNIT)

    class Meta(object):
        app_label = 'foodie'

    def __unicode__(self):
        return self.nk


class MeasurementConversion(models.Model, NKMixin):
    """A table mapping quantity, weight, and volume measurements to a specific food."""

    WEIGHT_CONVERSION = {
        POUND: decimal.Decimal(16.0),
        OUNCE: decimal.Decimal(1.0)
    }

    VOLUME_CONVERSION = {
        GALLON: decimal.Decimal(768.0),
        QUART: decimal.Decimal(192.0),
        PINT: decimal.Decimal(96.0),
        CUP: decimal.Decimal(48.0),
        TABLESPOON: decimal.Decimal(3.0),
        TEASPOON: decimal.Decimal(1.0)
    }

    CONVERSION_TABLE = {
        WEIGHT: WEIGHT_CONVERSION,
        VOLUME: VOLUME_CONVERSION
    }

    objects = NKManager()

    nk = NKField()

    food = models.ForeignKey('foodie.Food')

    weight = models.DecimalField(decimal_places=3, max_digits=6)

    weight_measurement = models.ForeignKey('foodie.Measurement', related_name='weight_measurement_conversions')

    volume = models.DecimalField(decimal_places=3, max_digits=6)

    volume_measurement = models.ForeignKey('foodie.Measurement', related_name='volume_measurement_conversions')

    class Meta(object):
        app_label = 'foodie'
        default_related_name = 'measurement_conversions'

    def __unicode__(self):
        return self.nk

    def convert_measurement(self, amount, measurement_1, measurement_2):
        """
        Converts the specified amount from one measurement to another, using a conversion table.
        :param amount: the amount of a Food
        :param measurement_1: the Measurement converted from
        :param measurement_2: the Measurement converted to
        :return: the amount converted to the specified measurement
        """

        # If the measurements have the same units, return the amount. No conversion necessary.
        if measurement_1.unit == measurement_2.unit:
            return decimal.Decimal(amount)

        # If the measurements are the same type, convert using the table and return the amount.
        if measurement_1.type == measurement_2.type:
            conversion_table = self.CONVERSION_TABLE[measurement_1.type]
            return decimal.Decimal(amount) * conversion_table[measurement_1.unit] / conversion_table[measurement_2.unit]

        else:
            # Convert measurement 1 unit to measurement conversion unit.
            amount = self.convert_measurement(
                amount,
                measurement_1=measurement_1,
                measurement_2=self.get_measurement_by_type(measurement_1.type)
            )

            # Convert measurement 1 type to measurement 2 type.
            amount *= (self.get_amount_by_type(measurement_2.type) /
                       self.get_amount_by_type(measurement_1.type))

            # Convert amount back to measurement 2 unit.
            return self.convert_measurement(
                amount,
                measurement_1=self.get_measurement_by_type(measurement_2.type),
                measurement_2=measurement_2
            )

    def get_measurement_by_type(self, measurement_type):
        """Returns the Measurement by the type."""

        return {
            WEIGHT: self.weight_measurement,
            VOLUME: self.volume_measurement
        }[measurement_type]

    def get_amount_by_type(self, measurement_type):
        """Returns the amount by the type."""

        return {
            WEIGHT: decimal.Decimal(self.weight),
            VOLUME: decimal.Decimal(self.volume)
        }[measurement_type]


class Allergen(models.Model, NKMixin):
    """A food allergen."""

    objects = NKManager()

    nk = NKField()

    name = models.CharField(max_length=255)

    class Meta(object):
        app_label = 'foodie'

    def __unicode__(self):
        return self.nk


class FoodXAllergen(models.Model, NKMixin):
    """Through table between Food and Allergen."""

    objects = NKManager()

    nk = NKField(help_text='e.g. {food.nk}$${allergen.nk}')

    food = models.ForeignKey('foodie.Food')

    allergen = models.ForeignKey('foodie.Allergen')

    rank = models.IntegerField(default=0, help_text='Controls the display order in the UI.')

    class Meta(object):
        app_label = 'foodie'

    def __unicode__(self):
        return self.nk
