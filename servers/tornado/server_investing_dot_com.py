#!/usr/bin/env python
# Author   : Vikas Chouhan (presentisgood@gmail.com)
# License  : GPLv2
# @@@
#
# Tornado server interface for investing.com

import tornado.ioloop
import tornado.web
from   tornado.web import RequestHandler, Application, url
from   tornado.ioloop import IOLoop
from   tornado import gen
from   tornado.concurrent import run_on_executor
from   concurrent.futures import ThreadPoolExecutor   # `pip install futures` for python
import sys
import os
from   PIL import Image
import cStringIO as StringIO

sys.path.append("../../scripts")
from   gen_candlestick_investing_dot_com import *
from   scan_investing_dot_com_by_name import *

# Plots directory
plot_dir = 'output'
# Max workers
MAX_WORKERS = 16

def check_plot_dir():
    # If directory already exists, do nothing
    if os.path.isdir(plot_dir):
        return
    # enddef
    # Create directory
    os.mkdir(plot_dir)
# enddef

# Json List to HTML Table
def json_list_2_html_table(json_list, url_prot, url_host):
    if (len(json_list) == 0):
        return 'Error message = Nothing found !!'
    # endif
    j_keys = json_list[0].keys()
    buf = '<table border=1>'
    # Add headers
    for i_this in j_keys:
        buf = buf + '<th> {} </th>'.format(i_this)
    # endfor
    # Add data
    for i_this in json_list:
        buf = buf + '<tr>'
        for j_this in j_keys:
            # Add hyperlink
            if j_this == 'symbol':
                sym = i_this[j_this].split(':')[0]
                bufl = '<td><a href="{}://{}/plota/{}/1W/80"> {} </a></td>'.format(url_prot, url_host, sym, sym)
            else:
                bufl = '<td> {} </td>'.format(i_this[j_this])
            # endif
            buf = buf + bufl
        # endfor
        buf = buf + '</tr>'
    # endfor
    return buf
# enddef

# Derived class for worker tasks
class RequestHandlerDerv(RequestHandler):
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    @run_on_executor
    def bg_task_plot(self, sym, res, plot_dir, plot_period, plot_volume):
        return gen_candlestick_wrap(sym, res=res, plot_dir=plot_dir, plot_period=plot_period, plot_volume=plot_volume)
    # enddef
    @run_on_executor
    def bg_task_search(self, name, exchg):
        return scan_securities(name=name, exchange=exchg)
    # enddef
# endclass

# Main page Handler
class MainHandler(RequestHandlerDerv):
    def get(self):
        buf = '<table border=1>'
        buf = buf + '<tr><td> /                                                 </td><td> Help                                    </td></tr>'
        buf = buf + '<tr><td> /symbol/{symbol}/{resolution}/{nbars}             </td><td> Plot candlestick chart with only price. </td></tr>'
        buf = buf + '<tr><td> /plot/{symbol}/{resolution}/{nbars}               </td><td> Same as above !!                        </td></tr>'
        buf = buf + '<tr><td> /plota/{symbol}/{resolution}/{nbars}              </td><td> Plot both price and volume.             </td></tr>'
        buf = buf + '<tr><td> /search/{pattern}/{exchange}                      </td><td> Search symbols with pattern & exchange. </td></tr>'
        buf = buf + '<br>'
        buf = buf + '<header><h5> Copyright Vikas Chouhan (presentisgood@gmail.com) 2017-2018. </h5></header>'
        self.write(buf)
    # enddef
# endclass

# Symbol Handler
class SymbolHandler(RequestHandlerDerv):
    @gen.coroutine
    def get(self, **db):
        resolution = db['resolution'] if db['resolution'] else '1D'
        try:
            nbars      = int(db['nbars']) if db['nbars'] else 40
        except ValueError as e:
            self.write('Error message = {}'.format(e.message))
            return
        # endtry
        
        file_name = yield self.bg_task_plot(db['symbol'], res=resolution, plot_dir=plot_dir, plot_period=nbars, plot_volume=False)
        if os.path.isfile(file_name):
            with open(file_name, 'rb') as im_out:
                self.set_header('Content-type', 'image/png')
                self.write(im_out.read())    
        else:
            self.write('Error message = {}'.format(file_name))
    # enddef
# endclass

class SymbolHandler2(RequestHandlerDerv):
    @gen.coroutine
    def get(self, **db):
        resolution = db['resolution'] if db['resolution'] else '1D'
        try:
            nbars      = int(db['nbars']) if db['nbars'] else 40
        except ValueError as e:
            self.write('Error message = {}'.format(e.message))
            return
        # endtry
        
        file_name = yield self.bg_task_plot(db['symbol'], res=resolution, plot_dir=plot_dir, plot_period=nbars, plot_volume=True)
        if os.path.isfile(file_name):
            with open(file_name, 'rb') as im_out:
                self.set_header('Content-type', 'image/png')
                self.write(im_out.read())    
        else:
            self.write('Error message = {}'.format(file_name))
    # enddef
# endclass

# Search Handler
class SearchHandler(RequestHandlerDerv):
    @gen.coroutine
    def get(self, **db):
        exchg  = db['exchange'] if db['exchange'] else ''
        j_data = yield self.bg_task_search(name=db['name'], exchg=exchg)
        if isinstance(j_data, str):
            self.write('Message = {}'.format(j_data))
        else:
            self.write(json_list_2_html_table(j_data, self.request.protocol, self.request.host))
        # endif
    # enddef
# endclass

# App routing control
def make_app():
    return Application([
            url(r'/', MainHandler),
            url(r'/symbol/(?P<symbol>[^\/]+)/?(?P<resolution>[^\/]+)?/?(?P<nbars>[^\/]+)?', SymbolHandler),
            url(r'/plot/(?P<symbol>[^\/]+)/?(?P<resolution>[^\/]+)?/?(?P<nbars>[^\/]+)?', SymbolHandler),
            url(r'/plota/(?P<symbol>[^\/]+)/?(?P<resolution>[^\/]+)?/?(?P<nbars>[^\/]+)?', SymbolHandler2),
            url(r'/search/(?P<name>[^\/]+)/?(?P<exchange>[^\/]+)?', SearchHandler),
        ])
# enddef

# Main function
if __name__ == '__main__':
    check_plot_dir()
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
# endif
