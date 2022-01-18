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
import pymysql

# -----------------------------------------------------------
# Getter functions for a product
# -----------------------------------------------------------

def get_product(conn, product_name, brand):
    '''
    Returns whether or not the product already exists.
    Also used to return the product id.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''select * from products 
             where product_name = %s and brand = %s'''
    curs.execute(sql, [product_name, brand])
    return curs.fetchone()

def get_product_by_id(conn, product_id):
    '''
    Returns product details in the database based 
    on product id. Also used to return the product_name for a product.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''select * from products where product_id = %s'''
    curs.execute(sql, [product_id])
    return curs.fetchone()

def get_key_ingredients(conn, product_id):
    '''
    Returns key ingredients based on the product_id
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''select * from ingredients
            inner join product_contents using (ingredients_id)
            inner join products using (product_id)
            where products.product_id = %s'''
    curs.execute(sql, [product_id])
    return curs.fetchall()

def get_products(conn): 
    '''
    Returns all products in the database.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''select * from products'''
    curs.execute(sql)
    return curs.fetchall()

# -----------------------------------------------------------
# Getter functions for insert and search forms
# -----------------------------------------------------------

def get_brands(conn):
    '''
    Returns brand type from list of products.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''select brand
             from brands'''
    curs.execute(sql)
    return curs.fetchall()

def get_types(conn):
    '''
    Returns product type from list of products.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''select `type`
             from types'''
    curs.execute(sql)
    return curs.fetchall()

def get_ingredients(conn):
    '''
    Returns key ingredients from list of products.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''select ingredient
             from ingredients'''
    curs.execute(sql)
    return curs.fetchall()

def get_ingredients_id(conn, ingredient):
    '''
    Returns ingredients id from list of ingredients.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''select ingredients_id
             from ingredients where ingredient = %s'''
    curs.execute(sql, [ingredient])
    return curs.fetchone()

# -----------------------------------------------------------
# Getter functions for routines
# -----------------------------------------------------------

def get_routines(conn, name_id):
    '''
    Returns the list of routines that a user has created.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''select *
            from routines
            where name_id = %s'''
    curs.execute(sql, [name_id])
    return curs.fetchall()

def get_routine_content(conn, name_id, routine_id):
    '''
    Returns the products within a routine that a user has added.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''select products.product_id, products.product_name, products.brand,
            routines.routine_name from products 
            inner join routine_contents using (product_id)
            inner join routines using (routine_id)
            where routines.name_id = %s and routines.routine_id = %s'''
    curs.execute(sql, [name_id, routine_id])
    return curs.fetchall()


# -----------------------------------------------------------
# Additional getter functions
# -----------------------------------------------------------

def get_reviews(conn, product_id, uid):
    '''
    Returns the reviews for a product that aren't the given by the user.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''select * from reviews 
             where product_id = %s and addedby != %s'''
    curs.execute(sql, [product_id, uid])
    return curs.fetchall()

def get_user_info(conn, name_id):
    '''
    Given the name_id, returns the user's profile information
    from the users table.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''select * from users 
             where name_id = %s'''
    curs.execute(sql, [name_id])
    return curs.fetchone()

def get_user_review(conn, product_id, uid):
    '''
    Returns the user review given the product and the user's ID.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''select * from reviews 
             where product_id = %s and addedby = %s'''
    curs.execute(sql, [product_id, uid])
    return curs.fetchone()

# -----------------------------------------------------------
# Functions for inserting, updating, and deleting products
# -----------------------------------------------------------

def insert_product(conn, product_type, product_name,
                   brand, url, addedby):
    '''
    Inserts new product into database according 
    to information entered by users.
    '''
    curs = dbi.dict_cursor(conn)
    try:
        sql = '''insert into products (product_type, 
                product_name, brand, url, addedby)
                values (%s, %s, %s, %s, %s)'''
        nr = curs.execute(sql, [product_type, product_name,
                    brand, url, addedby])
        conn.commit()
        return nr == 1
    except pymysql.IntegrityError as err:
        print('unable to insert {} due to {}'.format(product_name, repr(err)))
        return False

def update_product(conn, product_type, product_name, brand,
                   url, product_id):
    '''
    Updates product in the database based on product id. This
    excludes adding in ingredients, which is a separate query.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''update products
             set product_type = %s,
             product_name = %s, brand = %s, url = %s
             where product_id = %s'''
    curs.execute(sql, [product_type, product_name, brand, 
                       url, product_id])
    conn.commit()

def delete_ingredients(conn, product_id):
    '''
    Updates ingredients for specified product
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''delete from product_contents
             where product_id = %s'''
    curs.execute(sql, [product_id])
    conn.commit()

def insert_ingredients(conn, ingredients_id, product_id):
    '''
    Updates ingredients for specified product
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''insert into product_contents (ingredients_id, 
             product_id) values (%s, %s)'''
    curs.execute(sql, [ingredients_id, product_id])
    conn.commit()

def delete_product(conn, product_id):
    '''
    Deletes product in the database based on product id.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''delete from products
             where product_id = %s''' 
    curs.execute(sql, [product_id])
    conn.commit()

# -----------------------------------------------------------
# Functions for inserting, updating, and deleting reviews
# -----------------------------------------------------------
    
def insert_review(conn, product_id, addedby, rating, comment):
    '''
    Given the addedby id, comment, and rating, inserts the 
    user's rating into the reviews table.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''insert into reviews (product_id, addedby, rating, 
            comment) values (%s, %s, %s, %s) on duplicate key 
            update rating = %s, comment = %s'''
    curs.execute(sql, [product_id, addedby, rating, 
                        comment, rating, comment])
    conn.commit()

def delete_review(conn, product_id, addedby):
    '''
    Given the addedby id, comment, and rating, deletes the 
    user's rating into the reviews table.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''delete from reviews
             where product_id = %s and addedby = %s''' 
    curs.execute(sql, [product_id, addedby])
    conn.commit()

# -----------------------------------------------------------
# Functions for user account creation
# -----------------------------------------------------------

def add_user_info(conn, name, email, skin_concern, skin_type):
    '''
    Input: connection, name, email, skin_concern, skin_type
    Adds the name, email, skin concern, & skin type to the 
    user table. Returns: name_id
    '''
    try:
        curs = dbi.dict_cursor(conn)
        sql = '''insert into users(`name`, email, skin_concern, skin_type)
                values(%s, %s, %s, %s)'''
        nr = curs.execute (sql, [name, email, skin_concern, skin_type])
        conn.commit()
        return nr == 1
    except Exception as err:
        print("inserting user info gave an error: {}".format(err))
        return False

def add_user(conn, username, password):
    '''
    Input: connection, username and password 
    Adds the username, password into the logins table
    '''
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
        stored = hashed.decode('utf-8')
        curs = dbi.dict_cursor(conn)
        sql = '''insert into logins(username, password)
                values(%s,%s)'''
        nr = curs.execute(sql, [username, stored])
        conn.commit()
        return nr == 1
    except Exception as err:
        print("inserting user gave an error: {}".format(err))
        return False

def delete_user_info(conn, email):
    '''
    Deletes user info given an email.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''delete from users
             where email = %s'''
    curs.execute(sql, [email])
    conn.commit()

def log_in(conn, password, username): 
    '''
    Input: connection, username and password 
    Logs in the user if the given usernames and password are correct.
    Otherwise, it displays an error
    '''
    curs = dbi.cursor(conn)
    curs.execute('''SELECT password FROM logins 
                    WHERE username = %s''',[username])
    row = curs.fetchone()
    if not row:
        return (False, "No such user :(" )
    hashed = row[0]
    hashed2_bytes = bcrypt.hashpw(password.encode('utf-8'),
                                  hashed.encode('utf-8'))
    hashed2 = hashed2_bytes.decode('utf-8')
    return hashed == hashed2

def get_user_id_from_users(conn, email):
    '''
    Given an email, gets the name_id in users table. For setting
    session. 
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''select name_id from users where email = %s''' 
    curs.execute(sql, [email])
    user_id = curs.fetchone()
    return user_id

def get_user_id_from_logins(conn, username):
    '''
    Given an username, gets the user_id in logins table. 
    For setting session. 
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''select uid from logins where username = %s''' 
    curs.execute(sql, [username])
    user_id = curs.fetchone()
    return user_id

def update_profile (conn, name, skin_concern, skin_type, name_id): 
    '''
    Input: connection, name, skin_concern, skin_type, name_id
    Updates the name, skin concern, & skin type to the 
    user table.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''update users 
             set `name` = %s, skin_concern = %s, skin_type = %s
             where name_id = %s'''
    curs.execute (sql, [name, skin_concern, skin_type, name_id])
    conn.commit()


# -----------------------------------------------------------
# Functions for routines
# -----------------------------------------------------------

def insert_routine_into_routines_db(conn, name_id, routine_name):
    '''
    Inserts new playlist name into database.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''insert into routines (name_id, routine_name) 
             values (%s, %s)'''
    curs.execute(sql, [name_id, routine_name])
    conn.commit()

def insert_products_into_routine_contents_db(conn, routine_id, product_id):
    '''
    Inserts new playlist products into database according 
    to information entered by user.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''insert into routine_contents (routine_id, product_id) 
             values (%s, %s)'''
    curs.execute(sql, [routine_id, product_id])
    conn.commit()

def delete_products_into_routine_contents_db(conn, routine_id, product_id):
    '''
    Deletes playlist products in database according 
    to information entered by user.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''delete from routine_contents
             where routine_id=%s and product_id=%s'''
    curs.execute(sql, [routine_id, product_id])
    conn.commit()

def find_routine_id(conn, name_id, routine_name):
    '''
    Returns the routine_id value for a routine name 
    for a specific user
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''select routine_id from routines 
             where name_id = %s and routine_name=%s'''
    curs.execute(sql, [name_id, routine_name])
    fetch = curs.fetchone()
    return fetch

def find_routine_name(conn, routine_id):
    '''
    Returns the routine_name value for a routine name 
    for a specific user
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''select routine_name from routines 
             where routine_id=%s'''
    curs.execute(sql, [routine_id])
    fetch = curs.fetchone()
    return fetch

def delete_routine_contents(conn, routine_id):
    '''
    Deletes products in routine_contents based on routine id.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''delete from routine_contents
             where routine_id = %s'''
    curs.execute(sql, [routine_id])
    conn.commit()

def delete_routine(conn, routine_id):
    '''
    Deletes routine in routines based on routine id.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''delete from routines
             where routine_id = %s'''
    curs.execute(sql, [routine_id])
    conn.commit()

def rename_routine(conn, user_id, routine_name, routine_id):
    '''
    Renames routine based on routine id.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''insert into routines (name_id, routine_name, routine_id) 
            values (%s, %s, %s) on duplicate key 
            update routine_name = %s'''
    curs.execute(sql, [user_id, routine_name, routine_id, routine_name])
    conn.commit()
# -----------------------------------------------------------
# Functions for searching
# -----------------------------------------------------------

def basic_search(conn, name):
    '''
    Returns a list of products that has a
    product_name that includes what word was searched
    ''' 
    curs = dbi.dict_cursor(conn)
    sql = '''select * from products 
             where product_name like %s'''
    curs.execute(sql, ['%' + name + '%'])
    fetch = curs.fetchall()
    return fetch

def advanced_search(conn, name, brand, type, is_exact):
    '''
    Returns a list of products that include either 
    part of the product_name, brand, or product_type
    ''' 
    curs = dbi.dict_cursor(conn)

    # part of sql string with or logic dependent on empty fields
    product_mappings = {"brand": brand, "product_type": type}
    other_attributes = ""
    inputs = []
    for attribute, search in product_mappings.items():
        other_attributes += " or {} = %s".format(attribute)
        inputs.append(search)

    if is_exact:   # selecting exact phrase finds an exact match
        sql = '''select * from products 
                where product_name = %s''' + other_attributes
        curs.execute(sql, [name] + inputs)
    else:
        sql = '''select * from products 
                where product_name like %s''' + other_attributes
        curs.execute(sql, ['%' + name + '%'] + inputs)

    fetch = curs.fetchall()
    return fetch

# -----------------------------------------------------------
# Functions for file upload
# -----------------------------------------------------------
def pfp_upload(conn, uid, filename):
    '''
    Inserts a photo into the picfile table. 
    ''' 
    curs = dbi.dict_cursor(conn)
    sql =  '''insert into picfile values (%s, %s)
              on duplicate key update filename = %s''' 
    curs.execute( sql, [uid, filename, filename])
    conn.commit()

def get_pfp(conn, uid):
    '''
    Given a uid, gets corresponding pfp from the picfile table. 
    ''' 
    curs = dbi.dict_cursor(conn)
    numrows = curs.execute('''select filename from picfile where uid = %s''', [uid])
    if numrows == 0:
        flash('No picture for {}'.format(uid))
        return redirect(url_for('profile'))
    row = curs.fetchone()
    return (row['filename'])
