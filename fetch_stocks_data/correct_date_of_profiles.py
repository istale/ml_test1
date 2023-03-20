import os
import sys
import glob
from scipy import stats

def get_list_file_path( path_representation ):
    #list = glob.glob('/home/raohongfu/*.php')
    list_return = glob.glob( path_representation  )
    #for this_path in list_return:
    #    print(this_path)
    return list_return

def get_list_symbol_from_outputs():
    file_path = './outputs/tw/*'
    list_symbol_path = get_list_file_path( file_path  )

    list_return = []
    for this_path in list_symbol_path:
        list_temp = this_path.split('/')
        list_return.append( list_temp[-1] )

    return sorted(list_return)


def read_csv_to_dict( input_table ):
    list_return = []

    list_header = []

    with open(input_table, 'r') as f:
        run_flag = 0

        for line in f:
            run_flag = run_flag + 1

            line = line.strip()

            if run_flag == 1:
                list_header = line.split(',')

            else:
                list_row_data = line.split(',')

                dict_row_data = {}
                for i in range(len(list_header)):
                    dict_row_data[ list_header[i] ] = list_row_data[i]

                list_return.append( dict_row_data )

    return list_return

def write_dict_to_csv( list_of_dict_data, input_header, file_path ):

    # create full path, will judge if need to create
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w') as f:
        f.write(input_header + '\n')

        list_header = input_header.split(',')
        for this_item in list_of_dict_data:

            list_this_item = []
            for this_header in list_header:
                list_this_item.append(this_item[this_header])
                
            f.write(','.join(list_this_item) + '\n')

def get_list_Profile_qty_price_of_this_day( this_symbol, this_day ):
    list_return = []

    file_path = './outputs/tw/' + this_symbol + '/' + 'profile_qty_price.csv'
    if not os.path.isfile(file_path):
        return []

    list_all_data = read_csv_to_dict( file_path )

    for this_row in list_all_data:
        if this_row['date'] == this_day:
            list_return.append(this_row)

    return list_return

def correct_profile_qty_price_files_iterately( ):

    new_date = '20180531'

    dict_correct_date_symbol_qty_price_row_count = {}

    list_symbol = get_list_symbol_from_outputs()
    for this_symbol in list_symbol:
        file_path = './outputs_correct_date_0530/tw/' + this_symbol + '/' + 'profile_qty_price.csv'
        if not os.path.isfile(file_path):
            print(file_path + '\t not found correct')
            dict_correct_date_symbol_qty_price_row_count[this_symbol] = 99999999
            continue

        list_all_data = read_csv_to_dict( file_path )
        dict_correct_date_symbol_qty_price_row_count[this_symbol] = len(list_all_data)

    for this_symbol in list_symbol:
        file_path = './outputs_wrong_date_0531/tw/' + this_symbol + '/' + 'profile_qty_price.csv'
        if not os.path.isfile(file_path):
            print(file_path + '\t not found wrong')
            continue

        list_all_data = read_csv_to_dict( file_path )
        correct_date_symbol_qty_price_row_count = dict_correct_date_symbol_qty_price_row_count[this_symbol]

        for i in range(len(list_all_data)):
            if i + 1 > correct_date_symbol_qty_price_row_count:
                list_all_data[i]['date'] = new_date

        output_file_path = './outputs_correct_date_0531/tw/' + this_symbol + '/' + 'profile_qty_price.csv'
        write_dict_to_csv(list_all_data, 'date,symbol,qty,price', output_file_path)
        print( 'done..' + output_file_path  )

def correct_profile_daily_summary_files_iterately( ):

    new_date = '20180531'

    list_symbol = get_list_symbol_from_outputs()

    for this_symbol in list_symbol:
        file_path = './outputs_wrong_date_0531/tw/' + this_symbol + '/' + 'profile_daily_summary.csv'
        if not os.path.isfile(file_path):
            print(file_path + '\t not found wrong')
            continue

        list_all_data = read_csv_to_dict( file_path )
        list_all_data[-1]['date'] = new_date
        
        output_file_path = './outputs_correct_date_0531/tw/' + this_symbol + '/' + 'profile_daily_summary.csv'
        write_dict_to_csv(list_all_data, 'date,symbol,open_price,close_price,high_price,low_price,offset_price,offset_percent,qty', output_file_path)
        print( 'done..' + output_file_path  )


if __name__ == '__main__':
    correct_profile_qty_price_files_iterately()
    correct_profile_daily_summary_files_iterately()
    print('\n\nDone~~\n\n')
