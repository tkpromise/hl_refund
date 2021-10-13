DROP TABLE IF EXISTS user;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uuid TEXT UNIQUE NOT NULL,
  meb_name TEXT NOT NULL,
  phone_num TEXT UNIQUE NOT NULL,
  bank_name TEXT NOT NULL,
  bank_address TEXT NOT NULL,
  bank_number TEXT NOT NULL,
  state TEXT,
  id_name TEXT NOT NULL
);
