CREATE TABLE Users (
    Id   INTEGER PRIMARY KEY ASC ON CONFLICT FAIL AUTOINCREMENT,
    Name TEXT    NOT NULL
);

CREATE TABLE AuthTokens (
    UserId     INTEGER REFERENCES Users (Id) 
                       NOT NULL
                       PRIMARY KEY,
    TokenHash  TEXT,
    ExpiryDate INTEGER
);


CREATE TABLE TGAuth (
    TgUserId INTEGER PRIMARY KEY
                     NOT NULL,
    UserId   INTEGER REFERENCES Users (Id) 
                     NOT NULL
);

CREATE TABLE TGIntake (
    UserId      INTEGER NOT NULL
                        REFERENCES Users (Id),
    TgChannelId INTEGER NOT NULL
);


CREATE TABLE VKAuth (
    VkId   INTEGER NOT NULL
                   PRIMARY KEY,
    UserId INTEGER REFERENCES Users (Id) 
                   NOT NULL
);

CREATE TABLE VKIntake (
    UserId INTEGER PRIMARY KEY
                 REFERENCES Users (Id) 
                 NOT NULL
);
