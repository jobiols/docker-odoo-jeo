#!/usr/bin/env python3
import argparse
import psycopg2
import sys
import time


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--db_host", required=True)
    arg_parser.add_argument("--db_port", required=True)
    arg_parser.add_argument("--db_user", required=True)
    arg_parser.add_argument("--db_password", required=True)
    arg_parser.add_argument("--timeout", type=int, default=5)

    args = arg_parser.parse_args()

    start_time = time.time()
    while (time.time() - start_time) < args.timeout:
        try:
            conn = psycopg2.connect(
                user=args.db_user,
                host=args.db_host,
                port=args.db_port,
                password=args.db_password,
                dbname="postgres",
            )

            # Esto deberia hacerlo odoo pero no lo hace habria que ver porque
            # sql = """
            #     -- From PostgreSQL's point of view, making 'unaccent' immutable is incorrect
            #     -- because it depends on external data - see
            #     -- https://www.postgresql.org/message-id/flat/201012021544.oB2FiTn1041521@wwwmaster.postgresql.org#201012021544.oB2FiTn1041521@wwwmaster.postgresql.org
            #     -- But in the case of Odoo, we consider that those data don't
            #     -- change in the lifetime of a database. If they do change, all
            #     -- indexes created with this function become corrupted!
            #     CREATE EXTENSION IF NOT EXISTS unaccent;
            #     ALTER FUNCTION unaccent(text) IMMUTABLE;
            # """

#            print(sql)

            # cr = conn.cursor()
            # cr.execute(sql)
            # conn.commit()

            error = ""
            break
        except psycopg2.OperationalError as e:
            error = str(e)

            print(
                "Trying to connect to",
                args.db_user,
                args.db_host,
                args.db_port,
                args.db_password,
                error
            )
        time.sleep(1)

    if error:
        print("Database connection failure: %s" % error, file=sys.stderr)
        sys.exit(1)
