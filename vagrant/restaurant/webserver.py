from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer 
from sqlalchemy.engine import create_engine 
from sqlalchemy.orm import sessionmaker 
from database_setup import Base, MenuItem, Restaurant
import cgi 

engine = create_engine('sqlite:///restaurantmenu.db') 

Base.metadata.bind = engine 
DBSession = sessionmaker( bind = engine) 

session = DBSession()

class webserverHandler(BaseHTTPRequestHandler): 
    def do_GET(self): 
        try:   
            if self.path.endswith('/restaurants'):
                self.send_response(200) 
                self.send_header('Content-type', 'text/html')
                self.end_headers() 

                restaurants = session.query(Restaurant).all()

                output = ''
                output += '<html><body><h1> Restaurants </h1>'

                output += '<p><a href="/new"> New </a></p>' 
                
                for restaurant in restaurants: 
                    output += '<p> %s </p>' % restaurant.name 
                    output += '<a href="/%s/edit"> Edit </a> ' % restaurant.id   
                    output += '<a href="/%s/delete"> Delete </a>' % restaurant.id

                output += '</body> </html>'
                self.wfile.write(output) 
                return 

            if self.path.endswith('/new'): 
                self.send_response(200) 
                self.send_header('Content-type', 'text/html') 
                self.end_headers() 
                
                output = '' 
                output += '<html><body>' 
                output += '<h2> New restaurant: </h2>'  

                output += '<form method="POST" enctype="multipart/form-data" action="/restaurants"><h2> Restaurant`s name: </h2><input name="restaurant_name" type="text"><input type="submit" value="Create"></form>' 
                output += '</body></html>'
                self.wfile.write(output)
                return 
            
            if self.path.endswith('/edit'): 
                self.send_response(200) 
                self.send_header('Content-type', 'text/html') 
                self.end_headers() 

                restaurant_id = self.path.split('/')[1] 

                restaurant = session.query(Restaurant).filter_by( id = int(restaurant_id)).one()
                
                output = '' 
                output += '<html><body>' 
                output += '<h2> Edit restaurant: %s </h2>' % restaurant.name 

                output += '<form method="POST" enctype="multipart/form-data" action="/restaurants" ><input type="hidden" name="restaurant_id" value="%s"><input name="restaurant_name" type="text"><input type="submit" value="Rename"></form>' % restaurant_id
                output += '</body></html>'
                self.wfile.write(output)
                return
            
            if self.path.endswith('/delete'): 
                self.send_response(200) 
                self.send_header('Content-type', 'text/html') 
                self.end_headers() 

                restaurant_id = self.path.split('/')[1] 

                restaurant = session.query(Restaurant).filter_by( id = int(restaurant_id)).one()
                
                output = '' 
                output += '<html><body>' 
                output += '<h2> Delete restaurant: %s </h2>' % restaurant.name 

                output += '<form method="POST" enctype="multipart/form-data" action="/restaurants" ><input type="hidden" name="restaurant_id" value="%s"><input type="submit" value="Delete"></form>' % restaurant_id
                output += '</body></html>'
                self.wfile.write(output)
                return

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path) 

    def do_POST(self):
        try:    
            self.send_response(301) 
            self.send_header('Location', '')
            self.end_headers() 
            
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type')) 

            if ctype == 'multipart/form-data': 
                fields = cgi.parse_multipart(self.rfile, pdict) 
                restaurant_name = fields.get('restaurant_name')
                restaurant_id = fields.get('restaurant_id')

                if restaurant_id[0] != None: 
                    restaurant = session.query(Restaurant).filter_by( id = int(restaurant_id[0])).one() 
                    
                    if restaurant_name != None:      
                        restaurant.name = restaurant_name[0] 
                        session.add(restaurant)
                    else: 
                        session.delete(restaurant)
                else: 
                    restaurant = Restaurant( name = restaurant_name[0]) 
                    session.add(restaurant)
                 
                session.commit()
                
                
        except: 
            pass

def main():
    try: 
        port = 8080 
        server = HTTPServer(('', port), webserverHandler) 
        print "Web server running on port %s" % port 
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..." 
        server.socket.close()


if __name__ == '__main__':
    main()