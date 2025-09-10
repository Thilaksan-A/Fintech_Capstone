# 🛠️ Migration Troubleshooting Guide

If you're encountering migration or DB schema issues, here are some common problems and how to resolve them:

---

#### Error: `No migrations found`

```bash
No migrations found
```

Make sure you've initialized the migrations folder:

```bash
flask db init
```

---

#### Error: DB connection issues

Ensure your `.env` contains the correct `LOCAL_DATABASE_URL`:

```env
LOCAL_DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/main
```

Check that your Postgres service is running:

```bash
docker compose ps
```

---

#### Error: `table "user" does not exist`

```bash
sqlalchemy.exc.ProgrammingError: table "user" does not exist
```

This usually means:

- Alembic is referencing a table that wasn’t created
- You manually renamed or deleted a model/table
- A migration tries to `DROP` a non-existent table

To resolve this, you can:

1. Check Migration History

    Inspect `migrations/versions/` to verify the order, content, and presence of your migration files.

2. Reset the Development Database (Dev only!)

    ```bash
    docker compose exec postgres dropdb -U postgres main
    docker compose exec postgres createdb -U postgres main
    flask db upgrade
    ```

3. Force Reset Migration State (⚠️ Use as last resort)

    ```bash
    flask db stamp head
    flask db migrate -m "Reset migrations"
    flask db upgrade
    ```

    This resets the Alembic version tracking and regenerates a clean migration.
