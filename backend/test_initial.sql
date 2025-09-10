BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 4e7f3d299337

CREATE TABLE "user" (
    id SERIAL NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL,
    risk_score INTEGER NOT NULL,
    PRIMARY KEY (id)
);

INSERT INTO alembic_version (version_num) VALUES ('4e7f3d299337') RETURNING alembic_version.version_num;

COMMIT;
