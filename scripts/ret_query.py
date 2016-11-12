#!/usr/bin/env python
import pprint
import pymongo
from   pymongo import MongoClient
import tablib

class ScreenerInScreener(object):
    # Ratio name (same as database)
    K_ROE                         = 'return_on_equity'
    K_P2E                         = 'price_to_earning'
    K_P2B                         = 'price_to_book'
    K_D2E                         = 'debt_to_equity'
    K_D2B                         = 'debt_to_book'
    K_CUM_NCF                     = 'cumulative_ncf'
    K_JUNK                        = 'junk'

    GENERATED_SET_LIST        = [ K_ROE, K_P2E, K_P2B, K_D2E, K_CUM_NCF ]

    @classmethod
    def g0(cls, ratio_name):
        if ratio_name in cls.GENERATED_SET_LIST:
            return "generated_set.{}".format(ratio_name)
        else:
            return ratio_name
        # endif
    # enddef
    @classmethod
    def g1(cls, ratio_name):
        if ratio_name in cls.GENERATED_SET_LIST:
            return "{}_cond".format(ratio_name)
        else:
            assert(False)
        # endif
    # enddef
    @classmethod
    def g2(cls, ratio_name):
        return "${}".format(cls.g0(ratio_name))
    # enddef

    def __init__(self):
        self.__mongo_client    = MongoClient()
        self.__db              = self.__mongo_client.fscreener       # Database
        self.__cl              = self.__db.screener_in               # Collection
        self.__and_cond_dict   = {}                                  # Ratio Dictionary
        self.__or_cond_dict    = {}
        self.__sname           = 'screener_in'

        self.set_default_conditions()
    # enddef

    def __del__(self):
        self.__mongo_client.close()

    def __cond_dict(self, op):
        if op == 'AND':
            return self.__and_cond_dict
        elif op == 'OR':
            return self.__or_cond_dict
        else:
            return self.__and_cond_dict
        # endif
    # enddef

    def __g_and_cond_ds(self):
        g_list = []
        for k in self.__and_cond_dict:
            g_list.append({self.g0(k) : self.__and_cond_dict[k]})
        # endfor
        return g_list
    # enddef
    def __g_or_cond_ds(self):
        g_list = []
        for k in self.__or_cond_dict:
            g_list.append({self.g0(k) : self.__and_cond_dict[k]})
        # endfor
        return g_list
    # enddef
    def __g_match_cond_ds(self):
        g_dict = {}
        if len(self.__g_and_cond_ds()) > 0:
            g_dict['$and'] = self.__g_and_cond_ds()
        # endif
        if len(self.__g_or_cond_ds()) > 0:
            g_dict['$or']  = self.__g_or_cond_ds()
        # endif
        return g_dict
    # enddef

    # Add ranges for ratios
    def set_default_conditions(self):
        #self.__cond_dict('AND')[self.K_JUNK] = False
        #self.set_d2e((0, 1))
        #self.set_p2e((60, 100))
        #self.set_roe((10, 1000))
        return self
    def set_d2e(self, rng, op='AND'):
        self.__cond_dict(op)[self.K_D2E] = { '$gte' : rng[0], '$lte' : rng[1] }
        return self
    def set_p2e(self, rng, op='AND'):
        self.__cond_dict(op)[self.K_P2E] = { '$gte' : rng[0], '$lte' : rng[1] }
        return self
    def set_roe(self, rng, op='AND'):
        self.__cond_dict(op)[self.K_ROE] = { '$gte' : rng[0], '$lte' : rng[1] }
        return self
    def set_p2b(self, rng, op='AND'):
        self.__cond_dict(op)[self.K_P2B] = { '$gte' : rng[0], '$lte' : rng[1] }
        return self


    # Generate lists
    def g_list(self, cursor_pos):
        return [ item for item in cursor_pos ]

    def tabulate_query(self, cursor_pos):
        # Get all elements in the list
        ret_list  = self.g_list(cursor_pos)

        # Get all keys directly inside each element
        nk_list   = [ x for x in ret_list[0].keys() if x != 'document' and x[0] != '_' ]

        org_list  = [ x['document']['generated_set'] for x in ret_list ] # Get generated set
        new_list  = [ [ x[k] for k in nk_list ] for x in ret_list ]

        # Deduce some stats
        # Get keys for all string values
        sk_list = []
        ik_list = []
        for i_k in org_list[0].keys():
            if isinstance(org_list[0][i_k], basestring):
                sk_list.append(i_k)
            else:
                ik_list.append(i_k)
            # endif
        # endif

        # New set of original keys
        ck_list = sk_list + ik_list
        # Get old list of list in modified order
        v_list  = [ [ x[k] for k in ck_list ] for x in org_list ]
        # Combined old and calculated keys
        ck_list = ck_list + nk_list
        # Combine old and new list items
        for indx in range(0, len(ret_list)):
            v_list[indx] = v_list[indx] + new_list[indx]
        # endfor

        # tabulate
        data = tablib.Dataset(*v_list, headers=ck_list)
        with open('/tmp/table.xls', 'wb') as f_o:
            f_o.write(data.xls)
        # endwith
    # enddef

    def collection(self):
        return self.__cl
    # enddef

    def magicf0(self):
        return  { '$add' : [ { '$divide' : [100, self.g2(self.K_P2E)] }, self.g2(self.K_ROE) ] }
    # enddef

    def magic_formula(self):
        mfc_pipeline = [
                           {
                               '$match' : self.__g_match_cond_ds(),
                           },
                           {
                               '$project' : {
                                   'magicf'      : self.magicf0(),
                                   'document'    : '$$ROOT',
                               }
                           }
                       ]
        mfc_opts     = {
                           'allowDiskUse' : True
                       }

        query_str = "db.getCollection('{}').aggregate({})".format(self.__sname, mfc_pipeline)
        curs_t  = self.__cl.aggregate(mfc_pipeline)
        self.tabulate_query(curs_t)
    # enddef
# endclass

db_ctxt_0 = ScreenerInScreener()
db_ctxt_0.set_p2e((1, 100)).set_roe((20, 100)).set_d2e((0.0, 1.0))
#query_string = db_ctxt_0.magic_formula()
#print query_string
db_ctxt_0.magic_formula()
