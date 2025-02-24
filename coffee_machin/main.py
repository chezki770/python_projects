from menu import Menu, MenuItem
from coffee_maker import CoffeeMaker
from money_machine import MoneyMachine


money_machin = MoneyMachine()
coffee_maker = CoffeeMaker()
menu = Menu()

is_on = True


while is_on:
    options = menu.get_items()
    choice = input(f"what would you like {options}: ")
    if choice == "off":
        is_on = False
    elif choice == "report":
        money_machin.report()
        coffee_maker.report()
    else:
        drink = menu.find_drink(choice)
        if coffee_maker.is_resource_sufficient(drink) and money_machin.make_payment(drink.cost):
            coffee_maker.make_coffee(drink)
