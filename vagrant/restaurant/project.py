from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from sqlalchemy.engine import create_engine 
from sqlalchemy.orm import sessionmaker 
from database_setup import Base, MenuItem, Restaurant

engine = create_engine('sqlite:///restaurantmenu.db') 

Base.metadata.bind = engine 
DBSession = sessionmaker( bind = engine) 

session = DBSession()

app = Flask(__name__)

@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id): 
    restaurant = session.query(Restaurant).filter_by( id = restaurant_id).one()
    items = session.query(MenuItem).filter_by( restaurant_id = restaurant.id).all()
    return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id): 
    item = session.query(MenuItem).filter_by( id = menu_id ).one() 
    return jsonify(MenuItem=item.serialize)

@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/') 
def restaurantMenu(restaurant_id): 
    restaurant = session.query(MenuItem).filter_by( id = restaurant_id).one()
    items = session.query(MenuItem).filter_by( restaurant_id = restaurant.id ) 

    return render_template('menu.html', restaurant=restaurant, items = items)



# Task 1: Create route for newMenuItem function here

@app.route('/restaurants/<int:restaurant_id>/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST': 
        newItem = MenuItem( name = request.form['name'], restaurant_id = restaurant_id)
        session.add(newItem)
        session.commit()
        flash('New menu item created!')
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    
    else: 
        return render_template('newmenuitem.html', restaurant_id = restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    newItem = session.query(MenuItem).filter_by( id = menu_id ).one()
    if request.method == 'POST':
        if request.form['name']: 
            newItem.name = request.form['name']
        session.add(newItem)
        session.commit()
        flash('Menu item has been edited!')
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else: 
        return render_template('editmenuitem.html', restaurant_id = restaurant_id, menu_item = newItem )

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    deletedItem = session.query(MenuItem).filter_by( id = menu_id).one() 
    if request.method == 'POST': 
        session.delete(deletedItem) 
        session.commit() 
        flash('Menu item has been deleted!')
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id )) 
         
    else:
        return render_template('deletemenuitem.html', restaurant_id = restaurant_id, menu_item = deletedItem) 


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True 
    app.run( host = '0.0.0.0', port = 5000)