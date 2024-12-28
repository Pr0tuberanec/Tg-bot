import aiosqlite

DB_NAME = "training_data.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS training (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                training_type TEXT NOT NULL,
                duration REAL NOT NULL,
                heart_rate_zones TEXT NOT NULL,
                cadence INTEGER,
                distance REAL,
                date TEXT NOT NULL,
                recommendations TEXT NOT NULL
            )
            """
        )
        await db.commit()

async def add_training(user_id, training_type, duration, heart_rate_zones, cadence, distance, date, recommendations):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO training (user_id, training_type, duration, heart_rate_zones, cadence, distance, date, recommendations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, training_type, duration, heart_rate_zones, cadence, distance, date, recommendations)
        )
        await db.commit()

async def get_training_by_date(user_id, date):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT * FROM training
            WHERE user_id = ? AND date = ?
            """,
            (user_id, date)
        )
        rows = await cursor.fetchall()
        return rows
