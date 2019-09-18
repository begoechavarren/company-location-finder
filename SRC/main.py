from clean import companies, coord_list
from functions_filter import *


cat_regex = "(?i)tech|(?i)web|(?i)design|(?i)code|(?i)mobile|(?i)advertising"
min_money_raised = 1000000
category = "562"
b_near_companies = 1
b_hostelry = 2
b_services = 4
b_events = 3

# en main tengo que meter como parametros los argumentos no?


def main():
    my_df = filter_categories(companies, coord_list,
                              min_money_raised, cat_regex)
    my_df = filter_maps(my_df)
    my_df = filter_meetup(category, my_df)
    my_df = normalize_df(my_df)
    final_location = punctuation(
        my_df, b_near_companies, b_hostelry, b_services, b_events)
    return final_location


print(main())

if __name__ == '__main__':
    main()
