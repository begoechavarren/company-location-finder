from clean import companies, coord_list
from functions_filter import *
from functions_menu import *


# tengo que definir que si no me dan el tipo de input que busco me de error o que vuelva a preguntar!
#!!!!!!!!!!!!!! tengo que hacer una funcion para convertir la categoría de los eventosen numero!!!!!!!!
# my_df tambien!

# API PARA BUSCAR LA UBICACIÓN DE MI UBICACION FINAL!
# Y DE TODAS SUS COSAS!!!!!!!!

# tiene sentido que los displays los haga todos al principio o que esten intercalados con la ejecución del programa?


def main():
    display_M1()
    cat_regex = categories_builder(input())
    display_M2()
    min_money_raised = input()
    display_M3()
    hostelry = input()
    display_M4()
    services = input()
    display_M5()
    event_category = input()
    display_M6(hostelry, services, event_category)
    ranking = [int(x) for x in input().split(",")]
    display_M7()
    my_df = filter_categories(companies, coord_list,
                              min_money_raised, cat_regex)
    my_df = filter_maps(my_df, hostelry, services)
    my_df = filter_meetup(event_category, my_df)
    my_df = normalize_df(my_df)
    final_location = punctuation(
        my_df, ranking[0], ranking[1], ranking[2], ranking[3])
    getCompaniesNear(lat, long, max_meters=2000)
    return final_location


if __name__ == '__main__':
    print(main())
