import os
from collections import OrderedDict
# import psycopg2
# from database.pgsql import Database


# file_list = ['benfleet.txt', 'braintree.txt', 'colchester.txt', 'romford.txt', 'southend.txt']




def load_urls(file_path, db):
    table = "urls"
    file = open(file_path, "r").read().splitlines()
    data_hold = list()
    for line in file:
        data = OrderedDict()
        elements = line.split("&")
        for element in elements:
            key, value = element.split("=")
            new_value = value.replace(r"%5E", "^").replace("%2C", ",")
            if new_value:
                # Add additional quotes to maintain the columns case values.
                key = f'"{key}"'
                data[key] = new_value
        data["description"] = "Chelmsford Test Url"
        cols = ",".join((list(data.keys())))
        values = [tuple(data.values())]
        # values = [tuple(x.values()) for x in data_hold]
        # Insert 
        # print(cols)
        # print(values)
        db.insert_urls(table, cols, values)
        
    

# def main():

#     load_urls("urls.txt")
#     # file = open("test.txt", "r").read().splitlines()
#     # data_hold = list()
#     # for line in file:
#     #     data = OrderedDict()
#     #     elements = line.split("&")
#     #     for element in elements:
#     #         key, value = element.split("=")
#     #         # value = unescape(value)
#     #         # print(type(value))
#     #         new_value = value.replace(r"%5E", "^").replace("%2C", ",")
#     #         # print(new_value)
#     #         data[key] = new_value
#     #         data_hold.append(data)
        

#     # for d in data_hold:
#     #     # print(d.keys())
#     #     for k, v in d.items():
#     #         print(f"{k} = {v}")


# if __name__ == "__main__":
#     main()