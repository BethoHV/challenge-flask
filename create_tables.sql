CREATE TABLE user (
        id INTEGER NOT NULL, 
        username VARCHAR(20) NOT NULL, 
        password VARCHAR(80) NOT NULL, 
        fullname VARCHAR(50) NOT NULL, 
        created_at DATETIME, 
        active BOOLEAN, 
        PRIMARY KEY (id)
);
CREATE TABLE user_session (
        id INTEGER NOT NULL, 
        user_id INTEGER NOT NULL, 
        session VARCHAR(50) NOT NULL, 
        created_at DATETIME, 
        valid BOOLEAN, 
        PRIMARY KEY (id), 
        FOREIGN KEY(user_id) REFERENCES user (id)
);
CREATE TABLE category (
        id INTEGER NOT NULL, 
        name VARCHAR(20) NOT NULL, 
        description VARCHAR(50) NOT NULL, 
        "order" INTEGER, 
        created_at DATETIME, 
        deleted BOOLEAN, 
        PRIMARY KEY (id)
);
CREATE TABLE product (
        id INTEGER NOT NULL, 
        name VARCHAR(20) NOT NULL, 
        description VARCHAR(50) NOT NULL, 
        "order" INTEGER, 
        price INTEGER, 
        category_id INTEGER NOT NULL, 
        deleted BOOLEAN, 
        PRIMARY KEY (id), 
        FOREIGN KEY(category_id) REFERENCES category (id)
);