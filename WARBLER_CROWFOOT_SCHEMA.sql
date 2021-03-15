-- Exported from QuickDBD: https://www.quickdatabasediagrams.com/
-- Link to schema: https://app.quickdatabasediagrams.com/#/d/3KEjdd
-- NOTE! If you have used non-SQL datatypes in your design, you will have to change these here.

-- This code created the DB schema diagram for the warbler app.
-- This app has 4 tables users, follows, messages and likes

CREATE TABLE "User" (
    "UserID" int   NOT NULL,
    "Email" string   NOT NULL,
    "Username" string   NOT NULL,
    "Image_Url" string   NULL,
    "Header_Image_Url" string   NULL,
    "Bio" string   NULL,
    "Location" string   NULL,
    "Password" string   NOT NULL,
    CONSTRAINT "pk_User" PRIMARY KEY (
        "UserID"
     ),
    CONSTRAINT "uc_User_Email" UNIQUE (
        "Email"
    ),
    CONSTRAINT "uc_User_Username" UNIQUE (
        "Username"
    )
);

CREATE TABLE "Message" (
    "MessageID" int   NOT NULL,
    "Text" varchar(140)   NOT NULL,
    "Timestamp" datetime   NOT NULL,
    "UserID" int   NOT NULL,
    CONSTRAINT "pk_Message" PRIMARY KEY (
        "MessageID"
     )
);

CREATE TABLE "Follows" (
    "User_Being_Followed_ID" int   NOT NULL,
    "User_Following_ID" int   NOT NULL
);

CREATE TABLE "Likes" (
    "LikesID" int   NOT NULL,
    "UserID" int   NOT NULL,
    "MessageID" int   NOT NULL,
    CONSTRAINT "pk_Likes" PRIMARY KEY (
        "LikesID"
     ),
    CONSTRAINT "uc_Likes_MessageID" UNIQUE (
        "MessageID"
    )
);

ALTER TABLE "Message" ADD CONSTRAINT "fk_Message_UserID" FOREIGN KEY("UserID")
REFERENCES "User" ("UserID");

ALTER TABLE "Follows" ADD CONSTRAINT "fk_Follows_User_Being_Followed_ID" FOREIGN KEY("User_Being_Followed_ID")
REFERENCES "User" ("UserID");

ALTER TABLE "Follows" ADD CONSTRAINT "fk_Follows_User_Following_ID" FOREIGN KEY("User_Following_ID")
REFERENCES "User" ("UserID");

ALTER TABLE "Likes" ADD CONSTRAINT "fk_Likes_UserID" FOREIGN KEY("UserID")
REFERENCES "User" ("UserID");

ALTER TABLE "Likes" ADD CONSTRAINT "fk_Likes_MessageID" FOREIGN KEY("MessageID")
REFERENCES "Message" ("MessageID");

