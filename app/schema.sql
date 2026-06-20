CREATE TABLE IF NOT EXISTS "posts"( 
    "id" INTEGER PRIMARY KEY AUTOINCREMENT, 
    "user_id" INTEGER, 
    "title" VARCHAR(30) NOT NULL, 
    "content" VARCHAR(300) NOT NULL, 
    "is_published" INTEGER DEFAULT 1 CHECK("is_published" IN (0,1)), 
    "created_at" TEXT DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE SET NULL 
 );

CREATE TABLE IF NOT EXISTS "users"( 
    "id" INTEGER PRIMARY KEY AUTOINCREMENT, 
    "email" TEXT NOT NULL UNIQUE, 
    "password_hash" TEXT NOT NULL,
    "created_at" TEXT DEFAULT CURRENT_TIMESTAMP 
);


CREATE TABLE IF NOT EXISTS "likes"(
    "user_id" INTEGER, 
    "post_id" INTEGER, 
    UNIQUE ("user_id","post_id"), 
    FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE,
    FOREIGN KEY ("post_id") REFERENCES "posts"("id") ON DELETE CASCADE
);

