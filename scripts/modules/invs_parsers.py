import re
from   colorama import Fore

# Function to populate sec csv file in mentioned format to symbol list
def populate_sec_list(sfile):
    sec_list      = []
    l_ctr         = 0
    file_type     = None
    file_type_l   = ['nse_eqlist', 'nse_eqlist_m', 'bse_eqlist', 'nse_fo_mktlots', 'sym_name_list']

    # Return supported file types if no file passed
    if sfile == None:
        return file_type_l
    # endif

    with open(sfile, 'r') as file_h:
        for l_this in file_h:
            l_ctr = l_ctr + 1
            if l_ctr == 1:
                # Get file_type header (1st line)
                file_type = l_this.replace('\n', '').replace('\r', '').replace(' ', '')
                if file_type in file_type_l:
                    print Fore.MAGENTA + 'File type seems to be {} !!'.format(file_type) + Fore.RESET
                else:
                    print Fore.MAGENTA + 'Unsupported file type {}. Ensure that first line of csv file specifies file_type !!'.format(file_type) + Fore.RESET
                    sys.exit(-1)
                # endif
                continue
            # endif
            if re.match('^\s*#', l_this):
                continue
            # endif

            if file_type == 'bse_eqlist':
                s_arr = l_this.replace('\n', '').split(',')
                sec_list.append({
                                    'code' : s_arr[0],
                                    'name' : s_arr[2],
                               })
            elif file_type == 'nse_eqlist':
                s_arr = l_this.replace('\n', '').split(',')
                sec_list.append({
                                    'code' : s_arr[2],
                                    'name' : s_arr[0],
                               })
            elif file_type == 'nse_eqlist_m':
                s_arr = l_this.replace('\n', '').split(',')
                sec_list.append({
                                    'code' : s_arr[0],
                                    'name' : s_arr[1],
                               })
            elif file_type == 'nse_fo_mktlots':
                if re.match('UNDERLYING', l_this) or re.match('Derivatives in', l_this):
                    continue
                # endif
                s_arr = l_this.replace('\n', '').split(',')
                sec_list.append({
                                    'code' : s_arr[1].replace(' ', ''),
                                    'name' : s_arr[0],
                               })
            elif file_type == 'sym_name_list':
                s_arr = l_this.replace('\n', '').split(',')
                sec_list.append({
                                    'code' : s_arr[0].replace(' ', ''),
                                    'name' : s_arr[1],
                               })
            elif file_type == None:
                continue
            # endif
        # endfor
    # endwith
    return sec_list
# enddef

