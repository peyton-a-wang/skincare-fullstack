'''
CRAP Skincare Fall 2021
Carol, Rachel, Allie, Peyton
'''
from flask import (Flask, render_template, make_response, url_for, 
                   request, redirect, flash, session, 
                   send_from_directory, jsonify)
from werkzeug.utils import secure_filename
import cs304dbi as dbi
import bcrypt
import imghdr
import sys, os, random 
from queries import *

app = Flask(__name__)

app.secret_key = 'your secret here'
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

# new for file upload
app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB


@app.route('/', methods=['GET'])
def index():
    '''
    The home page of the web application that displays all the products.
    '''
    conn = dbi.connect()
    products = get_products(conn)
    results_string = "Displaying All Products ({} results):".format(len(products))
    return render_template('home.html', 
                    results_string=results_string, 
                    products=products)


@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product(product_id):
    '''
    Displays the product information and allows users 
    to update or delete the product. Users can review the product, 
    as well as update or delete their review.
    '''
    conn = dbi.connect()
    user_id = session.get('user_id')

    product_info = get_product_by_id(conn, product_id)
    # product_id = get_product_by_id(conn, product_id).get(product_id)
    ingredients = get_key_ingredients(conn, product_id)
    product_name = product_info.get('product_name')
    routines = get_routines(conn, user_id)
    user_review = get_user_review(conn, product_id, user_id)
    reviews = get_reviews(conn, product_id, user_id)

    if request.method == 'POST':
        # editing and deleting a product
        if request.form.get('submit') == 'Edit Product':
            return redirect(url_for('edit', product_id=product_id))
        
        elif request.form.get('submit') == 'Delete Product':
            delete_product(conn, product_id)
            flash('The product: {} was successfully deleted!'.format(product_name))
            return redirect(url_for('index'))
        
        # adding product to a routine
        elif request.form.get('submit') == 'Add':
            routine_name = request.form.get('routine-name')
            routine_id = find_routine_id(conn, user_id, routine_name).get('routine_id')
            insert_products_into_routine_contents_db(conn, routine_id, product_id)
            flash('Product {} successfully added to routine {}'
                    .format(product_name, routine_name))

        # adding and deleting a review
        elif request.form.get('submit') == 'Submit Review':
            comment = request.form.get('comment')
            rating = request.form.get('rate')
            insert_review(conn, product_id, user_id, rating, comment)
            # update the review if the user already reviewed the product
            if user_review:
                flash('You updated your review for {}!'.format(product_name))
            else: 
                flash('Thanks for leaving a review for {}!'.format(product_name))
        
        elif request.form.get('submit') == 'Delete':
            delete_review(conn, product_id, user_id)
            flash('Deleted review for {}!'.format(product_name))

    # renders with GET if loading into page and renders updated information from POST
    # checks for updated reviews so that the render will catch the 
    # new or edited review once submitted
    user_review = get_user_review(conn, product_id, user_id)
    return render_template('product.html', 
                            product_id=product_id, 
                            routines=routines, 
                            user_review=user_review, 
                            reviews=reviews,
                            product=product_info,
                            ingredients=ingredients)


# -----------------------------------------------------------
# Routes for inserting and editing products
# -----------------------------------------------------------

@app.route('/insert/', methods=['GET', 'POST'])
def insert():
    '''
    Allows users to insert a product into the database, 
    then redirects to the product page.
    '''
    conn = dbi.connect()

    if request.method == 'GET':
        type_list = get_types(conn)
        brand_list = get_brands(conn)
        ingredient_list = get_ingredients(conn)
        return render_template('add-product.html', 
                                types=type_list, 
                                brands=brand_list, 
                                ingredients=ingredient_list)
   
    elif request.method == 'POST':
        name = request.form.get('product-name')
        type = request.form.get('product-type')
        brand = request.form.get('product-brand')
        ingredients = request.form.getlist('product-ingredients')
        url = request.form.get('product-url')
        addedby = session.get('user_id')
        
        # inserts product if it doesn't already exist in the database
        is_inserted = insert_product(conn, type, name, brand, url, addedby)

        if is_inserted:
            product_id = get_product(conn, name, brand).get('product_id')
            
            for ingredient in ingredients:
                ingredients_id = get_ingredients_id(conn, ingredient).get('ingredients_id')
                insert_ingredients(conn, ingredients_id, product_id)

            flash('Product {} inserted'.format(name)) 
            return redirect(url_for('product', product_id=product_id))

        else:
            flash('The product {} already exists'.format(name))
            return redirect(url_for('insert'))

@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit(product_id):
    '''
    Allows users to edit information on an existing product.
    '''
    conn = dbi.connect()

    if request.method == 'GET':
        type_list = get_types(conn)
        brand_list = get_brands(conn)
        product_info = get_product_by_id(conn, product_id)
        ingredients_info = get_key_ingredients(conn, product_id)
        ingredient_list = get_ingredients(conn)
        return render_template('edit.html', 
                                product=product_info,
                                ingredients_info=ingredients_info,
                                types=type_list, 
                                brands=brand_list, 
                                ingredients=ingredient_list)
    
    elif request.method == "POST":
        name = request.form.get('product-name')
        brand = request.form.get('product-brand')
        type = request.form.get('product-type')
        ingredients = request.form.getlist('product-ingredients')
        url = request.form.get('product-url')
        if request.form['submit'] == 'submit':
            if ingredients != []:
                #deletes the existing list of ingredients that are stored
                #update was not used because the # of key ingredients
                #may change so we want to fully clear the list of 
                #ingredients that were last chosen and add in the new ones
                delete_ingredients(conn, product_id)
                #updates parts of the product that are not ingredients related
                update_product(conn, type, name, brand, url, product_id)
                i = 0
                #goes through the list of ingredients that were selected in the
                #drop down and adds each one into the products_content list
                while i < len(ingredients):
                    ingredients_id = get_ingredients_id \
                                    (conn, ingredients[i]).get('ingredients_id')
                    insert_ingredients(conn, ingredients_id, product_id)
                    i=i+1
            flash('The product: {} was successfully updated!'.format(name))
            return redirect(url_for('product', product_id=product_id))


# -----------------------------------------------------------
# Routes for routines
# -----------------------------------------------------------

@app.route('/routine_contents/<int:user_id>/<int:routine_id>', methods=['GET','POST'])
def routine_contents(user_id, routine_id):
    '''
    Displays the list of products in a selected routine.
    '''
    conn = dbi.connect()

    is_self = user_id == session.get('user_id')
    routine = get_routine_content(conn, user_id, routine_id)
    routine_name = find_routine_name(conn, routine_id).get('routine_name')
    products = get_products(conn)
    message = ('')

    if not routine:
        message = ('No products have been added to this routine!')

    if request.method == "POST":            
        if request.form['submit'] == 'rename playlist':
            routine_name = request.form.get('playlist-name')
            rename_routine(conn, user_id, routine_name, routine_id)
            flash("This routine has been renamed to {}.".format(routine_name))
        if request.form['submit'] == 'delete playlist':
            delete_routine_contents(conn, routine_id)
            delete_routine(conn, routine_id)
            return redirect(url_for('profile'))
        if request.form['submit'] == 'add':
            product_id = request.form.get('product')
            if product_id != '':
                insert_products_into_routine_contents_db(conn, routine_id, product_id)
                product_name = get_product_by_id(conn, product_id).get('product_name')
                flash("Product {} added to routine {}.".format(product_name, routine_name))
            else:
                flash("Please choose a product to add.")
        
        if request.form['submit'] == 'delete':
            product_id = request.form.get('selectedProduct')
            if product_id != '':
                product_name = get_product_by_id(conn, product_id).get('product_name')
                delete_products_into_routine_contents_db(conn, routine_id, product_id)
                flash("Product {} has been removed.".format(product_name, routine_name))
            else:
                flash("Please choose a product to delete.")

    #renders to the same location for both GET and POST
    routine = get_routine_content(conn, user_id, routine_id)
    routine_name = find_routine_name(conn, routine_id).get('routine_name')
    products = get_products(conn)

    return render_template('routines.html',
                            is_self=is_self,
                            msg=message,
                            products=products,
                            routine=routine,
                            user_id=user_id,
                            routine_id=routine_id,
                            routine_name=routine_name)


@app.route('/routine_form/', methods=['GET','POST'])
def routine_form():
    '''
    Allows users to create a new routine playlist, starting with adding one product.
    '''
    conn = dbi.connect()
    user_id = session.get("user_id")

    products = get_products(conn)
    if request.method == "GET":
        return render_template('create-routines.html', products=products)

    elif request.method == "POST":
        name = request.form.get('routine-name')
        product_id = request.form.get('product')
        if product_id != '':
            insert_routine_into_routines_db(conn, user_id, name)
            routine_id = find_routine_id(conn, user_id, name).get('routine_id')
            insert_products_into_routine_contents_db(conn, routine_id, product_id)
            flash("Routine {} added.".format(name))

        else:
            flash("Please choose a product.") 
            return render_template('create-routines.html', 
                                    products=products, 
                                    routine_name = name)
        
        return redirect(url_for('profile'))
# -----------------------------------------------------------
# Routes for account creation, login, and profile
# -----------------------------------------------------------

@app.route('/join/', methods = ['GET','POST'])
def join():
    ''' 
    Allows new users to create an account.
    '''
    conn = dbi.connect()
   
    if request.method == 'GET': 
        return render_template('join.html')
    
    elif request.method == 'POST':
        password = request.form.get('password')
        username = request.form.get('username')
        name = request.form.get('name')
        email = request.form.get('email')
        skin_concern = request.form.get('skin_concern')
        skin_type = request.form.get('skin_type') 
        #checking if upload is correct format of .jpg, .jpeg, or .png
        pfp = request.files['pic']
        user_filename = pfp.filename
        ext = user_filename.split('.')[-1]
        fname = user_filename.split('.')[0]
        check = secure_filename('{}.{}'.format(fname,ext))
        pathname = os.path.join(app.config['UPLOADS'],check)
        pfp.save(pathname)
        filetype = imghdr.what(pathname)
        if filetype == 'jpeg' or filetype == 'jpg' or filetype == 'png': 
            inserted_user_info = add_user_info(conn, name, email, skin_concern, skin_type)
                
            if not inserted_user_info: 
                flash('An account has already been created with your email.')        
                return render_template('join.html', 
                                        username=username,
                                        password=password, 
                                        name=name,
                                        email=email,
                                        skin_concern=skin_concern,
                                        skin_type=skin_type)

            inserted_user = add_user(conn, username, password)
                
            if not inserted_user: 
                delete_user_info(conn, email) 
                flash('Sorry, this username is already taken.')
                return render_template('join.html', 
                                        username=username,
                                        password=password, 
                                        name=name,
                                        email=email,
                                        skin_concern=skin_concern,
                                        skin_type=skin_type)
            else:
                add_user_info(conn, name, email, skin_concern, skin_type)
                add_user(conn, username, password)
                user_id = get_user_id_from_users(conn, email)
                session['user_id'] = user_id.get('name_id')
                uid = session.get('user_id')
                pfp_upload(conn, uid, check)
                flash('Your account was successfully created!')
                return redirect(url_for('index')) 
        else:    
            flash('Please upload a .jpeg, .jpg, or .png file.')
            return redirect(url_for('join')) 

       
        
        
@app.route('/login/', methods=['GET','POST'])
def login():
    ''' 
    Allows existing users to log in when 
    they provide the correct username and password.
    '''
    conn = dbi.connect()
    
    if request.method == 'GET':
        return render_template('login.html')
    
    elif request.method == 'POST':
        password = request.form.get('password')
        username = request.form.get('username')
        
        # lets the user log in if their credentials are correct
        if log_in(conn, password, username):
            user_id = get_user_id_from_logins(conn, username)
            if user_id:
                session['user_id'] = user_id.get('uid')
                return redirect(url_for('index'))
            else:
                flash('No account exists with the username {}'.format(username))
        else: 
            flash('Sorry, your password is incorrect :(')
        return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    "Logs the user out."
    session['user_id'] = False
    return redirect(url_for('login')) 

@app.route ('/profile_pic/<int:user_id>')
def get_profile_pic(user_id):
    '''
    Gets the user's profile picture based on their id
    '''
    conn = dbi.connect()
    filename = get_pfp(conn,user_id)
    return send_from_directory(app.config['UPLOADS'], filename)

@app.route('/profile', methods=['GET','POST'])
def profile():
    '''
    Allows users to view their profile, 
    which displays their basic information and routines.
    '''
    conn = dbi.connect()
    user_id = session.get('user_id')
    
    if request.method == 'GET':
        user_info = get_user_info(conn, user_id)
        routines = get_routines(conn, user_id)
        src = url_for('get_profile_pic', user_id = user_id)

        # displays whether or not a user has routines
        if not routines:
            message = ('You do not have any routines yet!')
            return render_template('profile.html', 
                                    is_self=True,
                                    msg=message,
                                    user=user_info,
                                    src=src)   
        else:
            return render_template('profile.html',
                                    is_self=True,
                                    routines=routines,
                                    user=user_info,
                                    src=src)
    else: 
        return redirect(url_for('edit_profile'), user_id = user_id)

@app.route('/edit_profile/<int:user_id>', methods=['GET','POST'])
def edit_profile(user_id):
    '''
    Allows the user to update their profile information
    '''
    conn = dbi.connect()
    user_info = get_user_info(conn, user_id)
    if request.method == 'GET':
        return render_template('edit-profile.html', user= user_info)
    else: 
        new_name = request.form.get('name')
        new_skin_concern = request.form.get('skin_concern')
        new_skin_type = request.form.get('skin_type') 
        update_profile(conn, new_name, new_skin_concern, new_skin_type, user_id)
        flash('Profile for user {} was successfully updated!'.format(user_id))
        return redirect(url_for('profile'))

@app.route('/profile/<int:user_id>', methods=['GET'])
def other_profile(user_id):
    '''
    Allows users to view other public users.
    '''
    conn = dbi.connect()
    user_info = get_user_info(conn, user_id)
    routines = get_routines(conn, user_id)
    src = url_for('get_profile_pic', user_id = user_id)
    is_self = user_id == session.get('user_id')

    return render_template('profile.html',
                            is_self=is_self,
                            routines=routines,
                            user=user_info,
                            src= src)

# -----------------------------------------------------------
# Routes for searching
# -----------------------------------------------------------

@app.route('/search/', methods=['GET'])
def search():
    '''
    Allows users to search for products by name in the database.
    '''
    conn = dbi.connect()
    name = request.args.get('name')
    search_list = basic_search(conn, name)
    results_string = "Displaying {} Search Result(s):".format(len(search_list))
    return render_template('home.html', 
                        results_string=results_string, 
                        products=search_list)


@app.route('/advsearch/', methods=['GET', 'POST'])
def adv_search():
    '''
    Allows users to search on other product attributes in the database.
    '''
    conn = dbi.connect()
    
    if request.method == 'GET':
        type_list = get_types(conn)
        brand_list = get_brands(conn)
        ingredient_list = get_ingredients(conn)
        return render_template('adv_search.html', 
                        types=type_list, 
                        brands=brand_list, 
                        ingredients=ingredient_list)
    
    elif request.method == 'POST':
        name = request.form.get('name')
        type = request.form.get('type')
        brand = request.form.get('brand')
        is_exact = request.form.get('submit') == 'with the exact phrase'
        search_list = advanced_search(conn, name, brand, type, is_exact)
        results_string = '''Displaying {} Search 
                            Result(s):'''.format(len(search_list))
        return render_template('home.html', 
                        results_string=results_string, 
                        products=search_list)
    

@app.before_first_request
def startup():
    '''
    Sets the correct database and caching information. 
    '''
    dbi.cache_cnf()
    dbi.use('crap_db')

@app.before_request
def check_logged_in():
    '''
    Ensures that the user is logged in before the page is loaded each time.
    '''
    user_id = session.get('user_id')

    if not user_id and request.endpoint not in ['login', 'join']:
        return redirect(url_for('login'))

if __name__ == '__main__':
    import os
    user_id = os.getuid()
    app.debug = True
    app.run('0.0.0.0',user_id)