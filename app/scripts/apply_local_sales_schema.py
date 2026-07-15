"""Apply the explicit MySQL schema for the Venda Local module.

Run once from the project root:
    .\\.venv\\Scripts\\python.exe app/scripts/apply_local_sales_schema.py
"""

from pathlib import Path

from sqlalchemy import inspect, text

from app.core.database import engine


def main():
    schema_path = Path(__file__).parent / "sql" / "local_sales_tables.sql"
    contents = schema_path.read_text(encoding="utf-8")
    statements = []
    current = []
    for line in contents.splitlines():
        if line.strip().startswith("--"):
            continue
        current.append(line)
    for statement in "\n".join(current).split(";"):
        statement = statement.strip()
        if statement:
            statements.append(statement)

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))

        # Existing marketplace rows become explicitly classified.  The
        # conditional inspection keeps this safe on databases already updated.
        inspector = inspect(connection)
        if "sales" in inspector.get_table_names():
            columns = {column["name"] for column in inspector.get_columns("sales")}
            if "channel_key" not in columns:
                connection.execute(text(
                    "ALTER TABLE sales ADD COLUMN channel_key VARCHAR(50) NOT NULL DEFAULT 'mercado_livre'"
                ))
                connection.execute(text("CREATE INDEX idx_sales_channel_key ON sales (channel_key)"))
            connection.execute(text(
                "UPDATE sales SET channel_key = 'mercado_livre' WHERE channel_key IS NULL OR channel_key = ''"
            ))
    print(f"Venda Local: {len(statements)} instruções aplicadas com sucesso.")


if __name__ == "__main__":
    main()
