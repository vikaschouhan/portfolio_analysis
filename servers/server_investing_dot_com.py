#!/usr/bin/env python
# Author   : Vikas Chouhan (presentisgood@gmail.com)
# License  : GPLv2
# @@@
#
# Tornado server interface for investing.com

import tornado.ioloop
import tornado.web
from   tornado.web import RequestHandler, Application, url
import sys
import os
from   PIL import Image
import cStringIO as StringIO

sys.path.append("../scripts")
from   gen_candlestick_investing_dot_com import *
from   scan_investing_dot_com_by_name import *

# Plots directory
plot_dir = 'output'

def check_plot_dir():
    # If directory already exists, do nothing
    if os.path.isdir(plot_dir):
        return
    # enddef
    # Create directory
    os.mkdir(plot_dir)
# enddef

# Json List to HTML Table
def json_list_2_html_table(json_list):
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
            buf = buf + '<td> {} </td>'.format(i_this[j_this])
        # endfor
        buf = buf + '</tr>'
    # endfor
    return buf
# enddef

# Main page Handler
class MainHandler(RequestHandler):
    def get(self):
        buf = '<table border=1>'
        buf = buf + '<tr><td> /                                                 </td><td> Help                                    </td></tr>'
        buf = buf + '<tr><td> /symbol/{symbol}/{resolution}/{nbars}             </td><td> symbol_name,resolution,nbars            </td></tr>'
        buf = buf + '<tr><td> /search/{pattern}/{exchange}                      </td><td> search_pattern,exchange                 </td></tr>'
        self.write(buf)
    # enddef
# endclass

# Symbol Handler
class SymbolHandler(RequestHandler):
    def get(self, **db):
        resolution = db['resolution'] if db['resolution'] else '1D'
        try:
            nbars      = int(db['nbars']) if db['nbars'] else 40
        except ValueError as e:
            self.write('Error message = {}'.format(e.message))
            return
        # endtry
        
        file_name = gen_candlestick_wrap(db['symbol'], res=resolution, plot_dir=plot_dir, plot_period=nbars)
        if os.path.isfile(file_name):
            with open(file_name, 'rb') as im_out:
                self.set_header('Content-type', 'image/png')
                self.write(im_out.read())    
        else:
            self.write('Error message = {}'.format(file_name))
    # enddef
# endclass

# Search Handler
class SearchHandler(RequestHandler):
    def get(self, **db):
        exchg  = db['exchange'] if db['exchange'] else ''
        j_data = scan_securities(name=db['name'], exchange=exchg)
        if isinstance(j_data, str):
            self.write('Message = {}'.format(j_data))
        else:
            self.write(json_list_2_html_table(j_data))
        # endif
    # enddef
# endclass

# App routing control
def make_app():
    return Application([
            url(r'/', MainHandler),
            url(r'/symbol/(?P<symbol>[^\/]+)/?(?P<resolution>[^\/]+)?/?(?P<nbars>[^\/]+)?', SymbolHandler),
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
