CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  avatar_url TEXT,
  age INTEGER,
  gender TEXT CHECK(gender IN ('male', 'female', 'other')),
  height_cm REAL,
  weight_kg REAL,
  activity_level TEXT CHECK(activity_level IN ('sedentary', 'light', 'moderate', 'active', 'very_active')),
  dietary_preferences TEXT NOT NULL DEFAULT '[]',
  allergies TEXT NOT NULL DEFAULT '[]',
  medical_conditions TEXT NOT NULL DEFAULT '[]',
  daily_calorie_goal INTEGER,
  locusgraph_bootstrapped INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
