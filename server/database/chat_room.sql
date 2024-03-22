PRAGMA foreign_keys = OFF;
-- ----------------------------
-- Table structure for chat_history
-- ----------------------------
DROP TABLE
IF
	EXISTS "chat_history";
CREATE TABLE "chat_history" (
	"user_id" TEXT,
	"target_id" TEXT,
	"target_type" INTEGER,
	"datas" BLOB,
	"sent" INTEGER,
	"padding_n" INTEGER
);
-- ----------------------------
-- Table structure for friends
-- ----------------------------
DROP TABLE
IF
	EXISTS "friends";
CREATE TABLE "friends" ( "from_user_id" TEXT NOT NULL, "to_user_id" TEXT NOT NULL, "accepted" INTEGER NOT NULL, PRIMARY KEY ( "from_user_id" ASC, "to_user_id" ) );
-- ----------------------------
-- Table structure for rooms
-- ----------------------------
DROP TABLE
IF
	EXISTS "rooms";
CREATE TABLE "rooms" ( "id" TEXT NOT NULL, "room_name" TEXT NOT NULL, PRIMARY KEY ( "id" ) );
-- ----------------------------
-- Table structure for room_user
-- ----------------------------
DROP TABLE
IF
	EXISTS "room_user";
CREATE TABLE "room_user" ( "room_id" TEXT NOT NULL, "user_id" TEXT NOT NULL, "room_manager" INTEGER NOT NULL );
-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE
IF
	EXISTS "users";
CREATE TABLE "users" ( "id" TEXT NOT NULL, "username" TEXT NOT NULL, "password" TEXT NOT NULL, PRIMARY KEY ( "id" ASC ) );