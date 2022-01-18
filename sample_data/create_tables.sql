use crap_db;

drop table if exists reviews;
drop table if exists routine_contents;
drop table if exists routines;
drop table if exists product_contents;
drop table if exists products;
drop table if exists logins;
drop table if exists picfile;
drop table if exists users; 
drop table if exists brands; 
drop table if exists types; 
drop table if exists ingredients; 

create table brands (
     brand varchar(50),
     primary key(brand)
)
ENGINE = InnoDB;

create table types (
     `type` varchar(50),
     primary key(`type`)
)
ENGINE = InnoDB;

create table ingredients (
     ingredients_id int not null auto_increment,
     ingredient varchar(50),
     primary key (ingredients_id, ingredient)
)
ENGINE = InnoDB;


create table users (
    name_id int not null auto_increment,
    `name` varchar(30),
    email varchar(30),
    skin_concern varchar(20),
    skin_type varchar(20),
    unique(email),
    primary key (name_id)
)
ENGINE = InnoDB;

create table picfile (
    uid int auto_increment not null primary key,
    filename varchar(50),
    foreign key (uid) references users(name_id) 
        on delete cascade on update cascade
)
ENGINE = InnoDB;


create table logins (
     uid int auto_increment not null primary key,
     username varchar(60) not null,
     password char(60) not null,
     unique(username),
     index(uid),
     foreign key (uid) references users(name_id)
          on update cascade
          on delete cascade
)
ENGINE = InnoDB;

create table products (
     product_id int not null auto_increment,
     product_type varchar(50),
     product_name varchar(50),
     brand varchar(50),
     `url` varchar(500),
     addedby int,
     unique(product_type, product_name, brand),
     primary key (product_id),
     foreign key (addedby) references users(name_id) 
         on delete cascade
         on update cascade,
     foreign key (product_type) references types(`type`)
         on delete cascade
         on update cascade,
     foreign key (brand) references brands(brand)
         on delete cascade
         on update cascade
)
ENGINE = InnoDB;

create table product_contents (
     product_id int,
     ingredients_id int,
     foreign key (product_id) references products(product_id)
         on delete cascade
         on update cascade,
     foreign key (ingredients_id) references ingredients(ingredients_id) 
         on delete cascade
         on update cascade
)
ENGINE = InnoDB;

create table routines ( 
    name_id int, 
    routine_name varchar(50),
    routine_id int not null auto_increment,
    primary key (routine_id),
    foreign key (name_id) references users(name_id) 
         on delete cascade
         on update cascade
)
ENGINE = InnoDB;

create table routine_contents (
     routine_id int, 
     product_id int,
     foreign key (routine_id) references routines(routine_id)
         on delete cascade
         on update cascade,
    foreign key (product_id) references products(product_id) 
         on delete cascade
         on update cascade
)
ENGINE = InnoDB;

create table reviews ( 
    product_id int,
    addedby int,
    rating int,
    comment varchar(1000),
    primary key (product_id, addedby),
    foreign key (product_id) references products(product_id) 
          on delete cascade
          on update cascade,
    foreign key (addedby) references users(name_id) 
          on update cascade
          on delete cascade
)
ENGINE = InnoDB;