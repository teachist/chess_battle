DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS player;
DROP TABLE IF EXISTS score;
DROP TABLE IF EXISTS setting;
DROP TABLE IF EXISTS battlelist;


CREATE TABLE user(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE player(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    school TEXT,
    age INTEGER
);

CREATE TABLE score(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    score INTEGER NOT NULL,
    round INTEGER NOT NULL,
    FOREIGN KEY (player_id) REFERENCES player(id),
    FOREIGN KEY (round) REFERENCES gemeinfo(id)
);

CREATE TABLE setting(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL DEFAULT 'Not set',
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE battlelist(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    round INTEGER NOT NULL,
    player_a INTEGER NOT NULL,
    player_b INTEGER NOT NULL,
    FOREIGN KEY (round) REFERENCES gameinfo(id),
    FOREIGN KEY (player_a) REFERENCES player(player_id),
    FOREIGN KEY (player_b) REFERENCES player(player_id)
);


INSERT INTO player(username, school, age) VALUES('Player A', 'Unknow School', 12);
INSERT INTO player(username, school, age) VALUES('Player b', 'Unknow School', 12);
INSERT INTO player(username, school, age) VALUES('Player c', 'Unknow School', 12);
INSERT INTO player(username, school, age) VALUES('Player d', 'Unknow School', 15);
INSERT INTO player(username, school, age) VALUES('Player e', 'Unknow School', 12);
INSERT INTO player(username, school, age) VALUES('Player f', 'Unknow School', 11);
INSERT INTO player(username, school, age) VALUES('Player g', 'Unknow School', 12);
INSERT INTO player(username, school, age) VALUES('Player h', 'Unknow School', 12);
INSERT INTO player(username, school, age) VALUES('Player i', 'Unknow School', 12);
INSERT INTO player(username, school, age) VALUES('Player j', 'Unknow School', 12);
INSERT INTO player(username, school, age) VALUES('Player k', 'Unknow School', 12);
INSERT INTO player(username, school, age) VALUES('Player l', 'Unknow School', 12);
INSERT INTO player(username, school, age) VALUES('Player m', 'Unknow School', 12);
INSERT INTO player(username, school, age) VALUES('Player n', 'Unknow School', 12);
INSERT INTO player(username, school, age) VALUES('Player o', 'Unknow School', 12);
INSERT INTO player(username, school, age) VALUES('Player p', 'Unknow School', 12);
INSERT INTO player(username, school, age) VALUES('Player q', 'Unknow School', 12);
INSERT INTO player(username, school, age) VALUES('Player s', 'Unknow School', 11);
INSERT INTO player(username, school, age) VALUES('Player t', 'Unknow School', 12);
INSERT INTO player(username, school, age) VALUES('Player u', 'Unknow School', 12);
INSERT INTO player(username, school, age) VALUES('Player v', 'Unknow School', 12);
INSERT INTO player(username, school, age) VALUES('Player w', 'Unknow School', 11);
