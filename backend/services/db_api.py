import psycopg

from psycopg.rows import dict_row
from psycopg import sql

from config import DATABASE_URL


ALLOWED_TABLES = {
    "users",
    "factories",
    "reporting_periods",
    "materials",
    "material_alternatives",
    "factory_material_usage",
    "energy_usage",
    "waste_streams",
    "logistics",
    "emission_factors",
    "ml_pipeline_runs",
    "carbon_results",
    "emission_sources",
    "interventions",
    "recommendations",
    "simulations",
    "carbon_credit_results",
    "audit_logs",
}


def check_table(resource: str):
    if resource not in ALLOWED_TABLES:
        raise ValueError(
            f"Invalid database resource: {resource}"
        )


async def get_connection():
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not configured"
        )

    return await psycopg.AsyncConnection.connect(
        DATABASE_URL,
        row_factory=dict_row
    )


async def get_resource(resource: str):

    check_table(resource)

    connection = await get_connection()

    try:

        async with connection.cursor() as cursor:

            query = sql.SQL(
                "SELECT * FROM {}"
            ).format(
                sql.Identifier(resource)
            )

            await cursor.execute(query)

            return await cursor.fetchall()

    finally:
        await connection.close()


async def get_resource_by_id(
    resource: str,
    item_id
):

    check_table(resource)

    connection = await get_connection()

    try:

        async with connection.cursor() as cursor:

            query = sql.SQL(
                "SELECT * FROM {} WHERE id = %s"
            ).format(
                sql.Identifier(resource)
            )

            await cursor.execute(
                query,
                (item_id,)
            )

            result = await cursor.fetchone()

            if result is None:
                raise KeyError(
                    f"{resource} record not found"
                )

            return result

    finally:
        await connection.close()


async def create_resource(
    resource: str,
    data: dict
):

    check_table(resource)

    if not data:
        raise ValueError(
            "No data supplied"
        )

    columns = list(data.keys())
    values = list(data.values())

    connection = await get_connection()

    try:

        async with connection.cursor() as cursor:

            query = sql.SQL(
                """
                INSERT INTO {}
                ({})
                VALUES ({})
                RETURNING *
                """
            ).format(

                sql.Identifier(resource),

                sql.SQL(", ").join(
                    map(
                        sql.Identifier,
                        columns
                    )
                ),

                sql.SQL(", ").join(
                    sql.Placeholder()
                    for _ in values
                )
            )

            await cursor.execute(
                query,
                values
            )

            result = await cursor.fetchone()

            await connection.commit()

            return result

    except Exception:

        await connection.rollback()
        raise

    finally:

        await connection.close()


async def update_resource(
    resource: str,
    item_id,
    data: dict
):

    check_table(resource)

    if not data:
        raise ValueError(
            "No data supplied"
        )

    connection = await get_connection()

    try:

        async with connection.cursor() as cursor:

            assignments = sql.SQL(", ").join(

                sql.SQL("{} = {}").format(
                    sql.Identifier(column),
                    sql.Placeholder()
                )

                for column in data.keys()
            )

            query = sql.SQL(
                """
                UPDATE {}
                SET {}
                WHERE id = %s
                RETURNING *
                """
            ).format(
                sql.Identifier(resource),
                assignments
            )

            values = list(data.values())
            values.append(item_id)

            await cursor.execute(
                query,
                values
            )

            result = await cursor.fetchone()

            if result is None:
                raise KeyError(
                    f"{resource} record not found"
                )

            await connection.commit()

            return result

    except Exception:

        await connection.rollback()
        raise

    finally:

        await connection.close()


async def delete_resource(
    resource: str,
    item_id
):

    check_table(resource)

    connection = await get_connection()

    try:

        async with connection.cursor() as cursor:

            query = sql.SQL(
                """
                DELETE FROM {}
                WHERE id = %s
                RETURNING id
                """
            ).format(
                sql.Identifier(resource)
            )

            await cursor.execute(
                query,
                (item_id,)
            )

            deleted = await cursor.fetchone()

            if deleted is None:
                raise KeyError(
                    f"{resource} record not found"
                )

            await connection.commit()

            return True

    except Exception:

        await connection.rollback()
        raise

    finally:

        await connection.close()