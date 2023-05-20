DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS player;
DROP TABLE IF EXISTS score;
DROP TABLE IF EXISTS setting;
DROP TABLE IF EXISTS battlelist;


CREATE TABLE user(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
     TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE player(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    id_card TEXT NOT NULL,
    project TEXT NOT NULL,
    phone TEXT NOT NULL
);

CREATE TABLE score(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    round INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES player(id)
);

CREATE TABLE setting(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL DEFAULT 'Not set yet',
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE battlelist(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    round INTEGER NOT NULL,
    player_a INTEGER NOT NULL,
    player_b INTEGER NOT NULL,
    FOREIGN KEY (player_a) REFERENCES player(player_id),
    FOREIGN KEY (player_b) REFERENCES player(player_id)
);


INSERT INTO player(name, id_card,project, phone) VALUES('Player A', '511825200010102023X', 'Personal', '1808171123');
INSERT INTO player(name, id_card,project, phone) VALUES('Player B', '511825200010102023X', 'Personal', '1808171123');
INSERT INTO player(name, id_card,project, phone) VALUES('Player C', '511825200010102023X', 'Personal', '1808171123');
INSERT INTO player(name, id_card,project, phone) VALUES('Player D', '511825200010102023X', 'Personal', '1808171123');
INSERT INTO player(name, id_card,project, phone) VALUES('Player E', '511825200010102023X', 'Personal', '1808171123');
INSERT INTO player(name, id_card,project, phone) VALUES('Player F', '511825200010102023X', 'Personal', '1808171123');
INSERT INTO player(name, id_card,project, phone) VALUES('Player H', '511825200010102023X', 'Personal', '1808171123');
INSERT INTO player(name, id_card,project, phone) VALUES('Player J', '511825200010102023X', 'Personal', '1808171123');
INSERT INTO player(name, id_card,project, phone) VALUES('Player K', '511825200010102023X', 'Personal', '1808171123');
INSERT INTO player(name, id_card,project, phone) VALUES('Player L', '511825200010102023X', 'Personal', '1808171123');
INSERT INTO player(name, id_card,project, phone) VALUES('Player M', '511825200010102023X', 'Personal', '1808171123');
INSERT INTO player(name, id_card,project, phone) VALUES('Player N', '511825200010102023X', 'Personal', '1808171123');
INSERT INTO player(name, id_card,project, phone) VALUES('Player O', '511825200010102023X', 'Personal', '1808171123');
INSERT INTO player(name, id_card,project, phone) VALUES('Player P', '511825200010102023X', 'Personal', '1808171123');
INSERT INTO player(name, id_card,project, phone) VALUES('Player Q', '511825200010102023X', 'Personal', '1808171123');
INSERT INTO player(name, id_card,project, phone) VALUES('Player R', '511825200010102023X', 'Personal', '1808171123');
INSERT INTO player(name, id_card,project, phone) VALUES('Player S', '511825200010102023X', 'Personal', '1808171123');
INSERT INTO player(name, id_card,project, phone) VALUES('Player T', '511825200010102023X', 'Personal', '1808171123');
