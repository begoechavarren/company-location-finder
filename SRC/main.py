from clean import companies, coord_list
from functions_filter import *
from functions_process import *
from functions_menu import *


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
    final_df = create_plot_df(
        hostelry, services, event_category, final_location)
    map_folium = create_folium(final_df, final_location)
    map_folium = create_legend(map_folium, services, event_category, hostelry)
    display_M8(final_location)
    open_folium_browser("map_folium")
    return "A tab in your browser should have opened.\nYou should see an interactive map with the perfect location\nfor your company and all its requirements displayed. \n\n\n\n"


if __name__ == '__main__':
    print(main())
