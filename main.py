from flask import Flask, render_template, request
from flask import redirect, url_for, flash, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from dataBase_setup import Base, Cat, Item, User
from flask import json
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)

CLIENT_ID = json.loads(open(
    'client_secrets.json', 'r').read())['web']['client_id']

# connect to the database and create a session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# login rout

@app.route('/login')
def login():
    state = ''.join(random.choice(
        string.ascii_uppercase+string.digits
        )for x in xrange(32))
    login_session["state"] = state
    return render_template('login.html', STATE=state)


# logout rout
@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("you have logged out successfully.")
        return redirect(url_for('index'))
    else:
        flash("please log in first")
        return redirect(url_for('index'))


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON routes
@app.route('/categories/JSON')
def Jgeneral():
    cats = session.query(Cat).all()
    return jsonify(cats=[i.serialize for i in cats])


@app.route('/categories/<int:cat_id>/JSON')
def Jcats(cat_id):
    cats = session.query(Cat).filter_by(id=cat_id).one()
    items = session.query(Item).filter_by(cat_id=cat_id).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/categories/<int:cat_id>/<int:item_id>/JSON')
def Jitems(cat_id, item_id):
    items = session.query(Item).filter_by(id=item_id).one()
    return jsonify(items=items.serialize)


# show the home page
@app.route('/')
@app.route('/categories')
def index():
    cats = session.query(Cat).all()
    items = session.query(Item).order_by(asc(Item.time)).limit(5)
    if 'username' not in login_session:
        return render_template('publicindex.html', cats=cats, items=items)
    return render_template("index.html", cats=cats, items=items)


# show categories

@app.route('/categories/<int:cat_id>')
def showCategory(cat_id):
    cat = session.query(Cat).filter_by(id=cat_id).first()
    if not cat:
        return render_template('addcat.html')
    else:
        cats = session.query(Cat).all()
        items = session.query(Item).filter_by(cat_id=cat_id)
        if 'username' not in login_session:
            return render_template(
                'catDetails.html', mycat=cat, cats=cats, items=items)
        else:
            return render_template(
                'logCatDetails.html', mycat=cat, cats=cats, items=items)


# show item

@app.route('/categories/<int:cat_id>/<int:item_id>')
def showItem(cat_id, item_id):
    my_item = session.query(Item).filter_by(id=item_id, cat_id=cat_id).one()
    if 'username' not in login_session:
        return render_template('itemDetails.html', item=my_item, cat_id=cat_id)
    else:
        return render_template(
            'logItemDetails.html', item=my_item, cat_id=cat_id)


# add new category

@app.route('/categories/add', methods={"GET", "POST"})
def addCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == "GET":
        return render_template("addcat.html")
    elif request.method == "POST":
        name = request.form['name']
        if not name:
            flash("Please enter all inputs")
            return render_template("addcat.html")
        else:
            cate = session.query(Cat).filter_by(name=name).first()
            if cate:
                flash("this categories already exists")
                return render_template("addcat.html")
            else:
                newCat = Cat(name=request.form['name'])
                session.add(newCat)
                session.commit()
                flash("category added successful")
                return redirect(url_for('index'))


# add new item
@app.route('/categories/<int:cat_id>/add', methods={"GET", "POST"})
def addItem(cat_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == "POST":
        newItem = Item(
            name=request.form['name'],
            user_id=login_session['user_id'],
            description=request.form['description'],
            price=request.form['price'],
            cat_id=cat_id)
        session.add(newItem)
        session.commit()
        flash("item is added successfully")
        return redirect(url_for('index'))
    else:
        return render_template("addItem.html", cat_id=cat_id)


# edit item

@app.route('/categories/<int:cat_id>/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(cat_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Item).filter_by(id=item_id, cat_id=cat_id).one()
    if editedItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert( 'You are not authorized to edit this restaurant./Please create your own restaurant in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
            if request.form['name']:
                print "name"
                editedItem.name = request.form['name']
            if request.form['description']:
                print "des"
                editedItem.description = request.form['description']
            if request.form['price']:
                print "price"
                editedItem.price = request.form['price']
            session.commit()
            flash("the item is updated successfully")
            return redirect(url_for(
                'showItem', cat_id=cat_id, item_id=item_id))
    else:
        return render_template(
            'editeitem.html', cat_id=cat_id, item=editedItem)


# delete item

@app.route('/categories/<int:cat_id>/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(cat_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    deletedItem = session.query(Item).filter_by(id=item_id).one()
    if editedItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this restaurant. Please create your own restaurant in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'GET':
        return render_template('deleteItem.html', item=deletedItem)
    else:
        flash("item deleted")
        session.delete(deletedItem)
        session.commit()
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.secret_key = "ThisISSECRET"
    app.debug = True
    app.run(port=5001, host="0.0.0.0")
