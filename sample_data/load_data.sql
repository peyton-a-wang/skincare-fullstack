use crap_db;

load data local infile 'product_brands.csv'
into table brands
fields terminated by ',' 
lines terminated by '\n';

load data local infile 'product_type.csv'
into table types
fields terminated by ',' 
lines terminated by '\n';

load data local infile 'product_ingredients.csv'
into table ingredients
fields terminated by ',' 
lines terminated by '\n';

load data local infile 'users.csv' 
into table users
fields terminated by ',' 
lines terminated by '\n';

load data local infile 'logins.csv'
into table logins
fields terminated by ',' 
lines terminated by '\n';

load data local infile 'products.csv'  
into table products
fields terminated by ',' 
lines terminated by '\n';

load data local infile 'product_contents.csv'
into table product_contents
fields terminated by ',' 
lines terminated by '\n';

load data local infile 'routines.csv' 
into table routines
fields terminated by ',' 
lines terminated by '\n';

load data local infile 'routine_contents.csv' 
into table routine_contents
fields terminated by ',' 
lines terminated by '\n';

load data local infile 'review.csv' 
into table reviews
fields terminated by ',' 
lines terminated by '\n';
