# Author : Vikas Chouhan (presentisgood@gmail.com)
import re
from   colorama import Fore
import sys
from   .utils import cint, parse_dict_file, parse_csv_file, coloritb

# Function to populate sec csv file in mentioned format to symbol list
def parse_security_file(sfile, ret_type):
    l_ctr         = 0
    file_type     = None
    file_type_l   = ['nse_eqlist', 'nse_eqlist_m', 'bse_eqlist', 'nse_fo_mktlots', 'sym_name_list']
    
    if ret_type not in ['list', 'dict']:
        print('ret_type should be either "list" or "dict"')
        sys.exit(-1)
    # endif

    # Return supported file types if no file passed
    if sfile == None:
        return file_type_l
    # endif

    if ret_type == 'list':
        sec_db = []
    elif ret_type == 'dict':
        sec_db = {}
    # endif

    def add_data(data, key=None):
        if ret_type == 'list':
            sec_db.append(data)
        elif ret_type == 'dict':
            assert key != None
            sec_db[key] = data
        # endif
    # enddef

    with open(sfile, 'r', encoding='ISO-8859-1') as file_h:
        for l_this in file_h:
            l_ctr = l_ctr + 1
            if l_ctr == 1:
                # Get file_type header (1st line)
                file_type = l_this.replace('\n', '').replace('\r', '').replace(' ', '')
                if file_type in file_type_l:
                    print(Fore.MAGENTA + 'File type seems to be {} !!'.format(file_type) + Fore.RESET)
                else:
                    print(Fore.MAGENTA + 'Unsupported file type {}. Ensure that first line of csv file specifies file_type !!'.format(file_type) + Fore.RESET)
                    sys.exit(-1)
                # endif
                continue
            # endif
            if re.match('^\s*#', l_this):
                continue
            # endif

            if file_type == 'bse_eqlist':
                s_arr = l_this.replace('\n', '').split(',')
                add_data({
                             'code' : s_arr[0],
                             'name' : s_arr[2],
                         }, s_arr[0])
            elif file_type == 'nse_eqlist':
                s_arr = l_this.replace('\n', '').split(',')
                add_data({
                             'code' : s_arr[2],
                             'name' : s_arr[0],
                         }, s_arr[2])
            elif file_type == 'nse_eqlist_m':
                s_arr = l_this.replace('\n', '').split(',')
                add_data({
                             'code' : s_arr[0],
                             'name' : s_arr[1],
                         }, s_arr[0])
            elif file_type == 'nse_fo_mktlots':
                if re.match('UNDERLYING', l_this) or re.match('Derivatives in', l_this):
                    continue
                # endif
                s_arr = l_this.replace('\n', '').split(',')
                s_code = s_arr[1].replace(' ', '')
                s_lsize = cint(s_arr[2])
                add_data({
                             'code' : s_code,
                             'name' : s_arr[0],
                             'lsize': s_lsize, 
                         }, s_code)
            elif file_type == 'sym_name_list':
                s_arr = l_this.replace('\n', '').split(',')
                s_code = s_arr[0].replace(' ', '')
                add_data({
                             'code' : s_code,
                             'name' : s_arr[1],
                         }, s_code)
            elif file_type == None:
                continue
            # endif
        # endfor
    # endwith
    return sec_db
# enddef

def populate_sec_list(sfile):
    return parse_security_file(sfile, ret_type='list')
# enddef
def populate_sec_dict(sfile):
    return parse_security_file(sfile, ret_type='dict')
# enddef

def populate_sym_list(invs_dict_file, sec_list):
    # Convert inv_dot_com_db_list to dict:
    inv_dot_com_db_dict = parse_dict_file(invs_dict_file)
    # Generate nse dict
    nse_dict = {}
    for item_this in inv_dot_com_db_dict.values():
        if u'nse_code' in item_this and item_this[u'nse_code']:
            nse_dict[item_this[u'nse_code']] = item_this
        # endif
    # endfor
    # Generate bse dict
    bse_dict = {}
    for item_this in inv_dot_com_db_dict.values():
        if u'bse_code' in item_this and item_this[u'bse_code']:
            bse_dict[item_this[u'bse_code']] = item_this
        # endif
    # endfor

    # code list
    nse_keys = nse_dict.keys()
    bse_keys = [x for x in bse_dict.keys()]

    # Search for tickers
    sec_dict = {}
    not_f_l  = []
    for sec_this in sec_list:
        sec_code = sec_this['code']
        sec_name = sec_this['name']
        sec_lsize = sec_this['lsize'] if 'lsize' in sec_this else None
        # Search
        if sec_code in nse_keys:
            sec_dict[sec_code] = {
                                     'ticker'    : nse_dict[sec_code][u'ticker'],
                                     'name'      : nse_dict[sec_code][u'description'],
                                     'exchange'  : nse_dict[sec_code][u'exchange'],
                                     'full_name' : nse_dict[sec_code][u'full_name'],
                                     'isin'      : nse_dict[sec_code][u'isin'],
                                     'symbol'    : nse_dict[sec_code][u'symbol'],
                                     'lot_size'  : sec_lsize,
                                 }
        elif sec_code in bse_keys:
            sec_dict[sec_code] = {
                                     'ticker'    : bse_dict[sec_code][u'ticker'],
                                     'name'      : bse_dict[sec_code][u'description'],
                                     'exchange'  : bse_dict[sec_code][u'exchange'],
                                     'full_name' : bse_dict[sec_code][u'full_name'],
                                     'isin'      : bse_dict[sec_code][u'isin'],
                                     'symbol'    : bse_dict[sec_code][u'symbol'],
                                     'lot_size'  : sec_lsize,
                                 }
        else:
            not_f_l.append(sec_this)
        # endif
    # endfor
    print(coloritb('{} not found in investing.com db'.format(not_f_l), 'red'))

    return sec_dict
# enddef

def populate_sym_list_kite(kite_csv_file, sec_list):
    kite_csv_rows = parse_csv_file(kite_csv_file)
    # Two dicts. One mapping symbol name to entry,
    # other mapping exchange code to entry
    symb_dict = {x[2]:x for x in kite_csv_rows}
    code_dict = {x[1]:x for x in kite_csv_rows}

    # Search for tickers
    sec_dict = {}
    not_f_l  = []
    for sec_this in sec_list:
        sec_code = sec_this['code']
        sec_name = sec_this['name']
        sec_lsize = sec_this['lsize'] if 'lsize' in sec_this else None
        # Search
        if sec_code in symb_dict:
            sec_dict[sec_code] = {
                                     'ticker'    : symb_dict[sec_code][0],
                                     'name'      : sec_name,
                                     'name_aux'  : symb_dict[sec_code][3],
                                     'symbol'    : symb_dict[sec_code][1],
                                     'lot_size'  : sec_lsize,
                                 }
        elif sec_code in code_dict:
            sec_dict[sec_code] = {
                                     'ticker'    : code_dict[sec_code][0],
                                     'name'      : sec_name,
                                     'name_aux'  : code_dict[sec_code][3],
                                     'symbol'    : code_dict[sec_code][1],
                                     'lot_size'  : sec_lsize,
                                 }
        else:
            not_f_l.append(sec_this)
        # endif
    # endfor
    print(coloritb('{} not found in investing.com db'.format(not_f_l), 'red'))

    return sec_dict
# enddef

def populate_sym_list_from_sec_file(invs_file, sec_file):
    sec_list   = populate_sec_list(sfile=sec_file)

    print('Found {} securities.'.format(len(sec_list)))
    sec_tick_d = populate_sym_list(invs_file, sec_list)
    print('Found {} securities in investing_com database.'.format(len(sec_tick_d)))

    return sec_tick_d
# enddef

def populate_sym_list_from_sec_file_kite(kite_csv_file, sec_file):
    sec_list   = populate_sec_list(sfile=sec_file)

    print('Found {} securities.'.format(len(sec_list)))
    sec_tick_d = populate_sym_list_kite(kite_csv_file, sec_list)
    print('Found {} securities in kite instruments database.'.format(len(sec_tick_d)))

    return sec_tick_d
# enddef
