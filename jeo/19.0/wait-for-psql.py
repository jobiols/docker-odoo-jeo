#!/usr/bin/env python3
# En un archivo nuevo llamado: wait-for-psql-debug.py

import argparse
import sys
import time

# --- LOG MEJORADO: Capturar error de importación ---
try:
    import psycopg2
except ImportError:
    print("ERROR CRITICO: La librería 'psycopg2' no está instalada.", file=sys.stderr)
    sys.exit(1)
# ---------------------------------------------------

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--db_host", required=True)
    arg_parser.add_argument("--db_port", required=True)
    arg_parser.add_argument("--db_user", required=True)
    arg_parser.add_argument("--db_password", required=True)
    arg_parser.add_argument("--timeout", type=int, default=30) # Aumentado el timeout por si acaso

    args = arg_parser.parse_args()

    start_time = time.time()
    error = ""
    while (time.time() - start_time) < args.timeout:
        try:
            conn = psycopg2.connect(
                user=args.db_user,
                host=args.db_host,
                port=args.db_port,
                password=args.db_password,
                dbname="postgres",
                connect_timeout=3 # Timeout para el intento de conexión
            )
            error = ""
            break
        except psycopg2.OperationalError as e:
            error = str(e).strip()
            print(f"[WAIT-FOR-PSQL] Intento fallido: {error}", flush=True)
        time.sleep(1)

    if error:
        print(f"[WAIT-FOR-PSQL] ERROR: No se pudo conectar a la base de datos después de {args.timeout} segundos.", file=sys.stderr)
        print(f"[WAIT-FOR-PSQL] Último error: {error}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)