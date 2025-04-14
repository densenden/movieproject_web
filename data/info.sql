BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "categories" (
	"id"	INTEGER NOT NULL,
	"name"	VARCHAR(50),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "movie_categories" (
	"movie_id"	INTEGER NOT NULL,
	"category_id"	INTEGER NOT NULL,
	PRIMARY KEY("movie_id","category_id"),
	FOREIGN KEY("category_id") REFERENCES "categories"("id"),
	FOREIGN KEY("movie_id") REFERENCES "movies"("id")
);
CREATE TABLE IF NOT EXISTS "movie_platforms" (
	"movie_id"	INTEGER NOT NULL,
	"platform_id"	INTEGER NOT NULL,
	PRIMARY KEY("movie_id","platform_id"),
	FOREIGN KEY("movie_id") REFERENCES "movies"("id"),
	FOREIGN KEY("platform_id") REFERENCES "streaming_platforms"("id")
);
CREATE TABLE IF NOT EXISTS "movies" (
	"id"	INTEGER NOT NULL,
	"name"	VARCHAR(100),
	"director"	TEXT,
	"year"	INTEGER,
	"rating"	REAL,
	"category_id"	INTEGER,
	"genre"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("category_id") REFERENCES "categories"("id")
);
CREATE TABLE IF NOT EXISTS "streaming_platforms" (
	"id"	INTEGER NOT NULL,
	"name"	VARCHAR(50),
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "user_favorites" (
	"user_id"	INTEGER NOT NULL,
	"movie_id"	INTEGER NOT NULL,
	"watched"	BOOLEAN,
	"comment"	TEXT,
	"rating"	FLOAT,
	PRIMARY KEY("user_id","movie_id"),
	FOREIGN KEY("movie_id") REFERENCES "movies"("id"),
	FOREIGN KEY("user_id") REFERENCES "users"("id")
);
CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER NOT NULL,
	"name"	VARCHAR(100),
	"whatsapp_number"	VARCHAR(20),
	"avatar_url"	TEXT,
	PRIMARY KEY("id")
);
INSERT INTO "users" VALUES (1,'Louise','+49 162 7933737',NULL);
INSERT INTO "users" VALUES (2,'Jörg','+49 176 24301783',NULL);
INSERT INTO "users" VALUES (3,'Chris','+49 1590 4891419',NULL);
INSERT INTO "users" VALUES (4,'Stefanos','+49 1517 2689928',NULL);
INSERT INTO "users" VALUES (5,'Spunky','+49 163 6654561',NULL);
INSERT INTO "users" VALUES (6,'Jon-Mark','+44 7710 047279',NULL);
INSERT INTO "users" VALUES (7,'Remo','+49 177 1637200',NULL);
INSERT INTO "users" VALUES (8,'Alex','+49 176 62048607',NULL);
INSERT INTO "users" VALUES (9,'Lisa','+49 176 30524940',NULL);
INSERT INTO "users" VALUES (10,'Stella','+49 1515 0650183',NULL);
COMMIT;
