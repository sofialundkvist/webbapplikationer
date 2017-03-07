CREATE TABLE program_user(
    id int auto_increment primary key,
    email varchar(50) NOT NULL,
    password text NOT NULL,
    reset_url text,
    url_time datetime,
    auth_level int DEFAULT 1,
    authenticated boolean DEFAULT FALSE,
    session_token text
);

CREATE TABLE exhibitor(
    id int primary key,
    company_name varchar(50),
    last_logged_in datetime,
    CONSTRAINT id_user FOREIGN KEY (id) REFERENCES program_user(id)
    ON DELETE CASCADE
);

CREATE TABLE label(
    id int auto_increment primary key,
    exhibitor_id int,
    label varchar(50),
    color varchar(10),
    CONSTRAINT belongs_to FOREIGN KEY (exhibitor_id) REFERENCES exhibitor(id)
    ON DELETE CASCADE
);

CREATE TABLE attendant(
    id int auto_increment primary key,
    front_end_id varchar(10),
    email varchar(50),
    first_name varchar(50),
    surname varchar(50),
    birth_month int,
    birth_day int,
    school varchar(50),
    commune varchar(50),
    profession varchar(50),
    qr varchar(50)
);

CREATE TABLE subjects(
    id int auto_increment primary key,
    attendant_id int,
    subject varchar(50),
    CONSTRAINT belongs_to_attendant FOREIGN KEY (attendant_id) REFERENCES attendant(id)
    ON DELETE CASCADE
);

CREATE TABLE teaching_year(
    id int auto_increment primary key,
    attendant_id int,
    year varchar(50),
    CONSTRAINT teaching_year_constraint FOREIGN KEY (attendant_id) REFERENCES attendant(id)
    ON DELETE CASCADE
);

CREATE TABLE connection(
    id int auto_increment primary key,
    exhibitor int,
    attendant_id int,
    comment text,
    CONSTRAINT to_exhibitor FOREIGN KEY (exhibitor) REFERENCES exhibitor(id)
    ON DELETE CASCADE,
    CONSTRAINT to_attendant FOREIGN KEY (attendant_id) REFERENCES attendant(id)
    ON DELETE CASCADE
);

CREATE TABLE label_to_connection (
    label_id int,
    connection_id int,
    PRIMARY KEY(label_id, connection_id),
    CONSTRAINT to_connection FOREIGN KEY (connection_id) REFERENCES connection(id)
    ON DELETE CASCADE,
    CONSTRAINT to_label FOREIGN KEY (label_id) REFERENCES label(id)
    ON DELETE CASCADE
);
