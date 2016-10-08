# Django imports.
from django.db.models import Prefetch

# Local imports.
from .models import Ingredient, Product, MeasurementConversion

__author__ = 'Jason Parent'


def calc_recipe_cost(recipe_nk):
    """
    Calculates the cost of a recipe.
    :param recipe_nk: Recipe NK value
    :return: a cost
    """

    ingredient_qs = Ingredient.objects.select_related('food', 'measurement').prefetch_related(
        Prefetch('food__products', queryset=Product.objects.select_related('measurement'))
    ).filter(recipe__nk=recipe_nk)

    # Get measurement conversions for the foods in this recipe.
    measurement_conversion_qs = MeasurementConversion.objects.select_related(
        'food', 'weight_measurement', 'volume_measurement').filter(
        food_id__in=[ingredient.food_id for ingredient in ingredient_qs]
    )
    measurement_conversion_by_food_nk = {
        measurement_conversion.food.nk: measurement_conversion
        for measurement_conversion in measurement_conversion_qs
    }

    cost = 0

    for ingredient in ingredient_qs:
        measurement_conversion = measurement_conversion_by_food_nk[ingredient.food.nk]

        # Find cheapest product.
        cheapest_product = calc_cheapest_product_by_price_per_unit(
            ingredient.food.products.all(),
            measurement_conversion=measurement_conversion
        )

        # Convert product measurement to ingredient measurement.
        amount = measurement_conversion.convert_measurement(
            cheapest_product.amount,
            measurement_1=cheapest_product.measurement,
            measurement_2=ingredient.measurement
        )

        # Calculated the prorated cost of the ingredient.
        cost += (ingredient.amount / amount) * cheapest_product.price

    return float(cost)


def calc_cheapest_product_by_price_per_unit(products, measurement_conversion):
    """
    Calculates the cheapest product by price per unit.
    :param products: a collection of Products
    :param measurement_conversion: a MeasurementConversion
    :return: a Product
    """

    cheapest_product = None
    cheapest_price_per_unit = None

    for product in products:
        if cheapest_product is None:
            cheapest_product = product
            cheapest_price_per_unit = product.price_per_unit

        else:
            product_price_per_unit = measurement_conversion.convert_measurement(
                product.price_per_unit,
                measurement_1=product.measurement,
                measurement_2=cheapest_product.measurement
            )

            if product_price_per_unit < cheapest_price_per_unit:
                cheapest_product = product
                cheapest_price_per_unit = product_price_per_unit

    return cheapest_product
