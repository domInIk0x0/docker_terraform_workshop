# docker_wokrshop

# 1. INTRUDUCTION
## 1 Options with docker run
-i input listening
-t create terminal view


Docker containers are stateless - any changes done inside a container will NOT be saved when the container is killed and started again.
Zmiany żyją tak długo jak dany kontener (zmiany nie są zapisywane w oryginalnym obrazie)


docker run -it ubuntu
docker run -it --rm ubuntu
apt update && apt install python3
python3 -V

docker ps (shows working containers)
docker ps -a (additionaly shows stopped containers)
docker ps -q (shows container ids)

docker stop (id name)
docker kill (id name)
docker rm $(docker ps -aq)
docker rm -f nazwa_kontenera

                    (image):(tag)
docker run -it --rm python:3.9.16-slim
docker run -d python:3.9.16-slim (uruchomienie w tle)
docker run -dt --rm ubuntu


docker run -it \
    --rm \
    --entrypoint=bash \
    python:3.9.16-slim      (--entrypoint  nadpisuje proces ktory ma sie uruchomic po starcie kontenera)



docker run -dt --name nazwa_kontenera python:3.9.16-slim
docker logs nazwa_kontenera (wyswietlenie logow)
docker logs -f nazwa_kontenera (podglad logow na biezaco)

docker run -it \
    --rm \
    -v $(pwd)/test:/app/test \
    --entrypoint=bash \
    python:3.9.16-slim   (opcja -v tworzy wspoldzielony na zywo katalog pomiedzy urzadzeniem a kontenerem)

docker image ls -a
docker image rm (id obrazu)


# 2. Virutal env
uv init --python=3.13 (biblioteka)
uv add pandas pyarrow --link-mode=copy
uv run python pipeline.py 10  


# 3. dockerizing pipeline
FROM (definicja obrazu bazowego) (flaga --from pozwala kopiowac pliki z innego obrazu docker)
RUN (wykonanie polecen ktore odbywaja sie podczas budowy kontenera)
WORKDIR (katalog roboczy w ktorym beda wykonywane komendy)
COPY (kopiowanie plikow z maszyny hosta do obrazu)
ENTRYPOINT (polecenie ktore zostanie uruchomione w momencie uruchomienia kontenera)

docker build -t test:pandas . (-t : Służy do nadania nazwy oraz opcjonalnej wersji obrazowi w formacie nazwa:tag.)
                              (. wskazuje kontekst budowania (aktualny katalog w przypadku .) )

docker build -f Dockerfile.dev -t pipeline:dev . (-f do wybrania konkretnego pliku Dockerfile)

uzycie flagi --no-install-project w uv wymusza dzialanie wylacznie jako srodowisko wykonawcze. 




# 4. postgres docker
Utworzenie bazy postgree poprzez kontener
 docker volume rm ny_taxi_postgres_data (usuwanie wolumenow)

 Named Volume vs Bind Mount
Named volume (name:/path): Managed by Docker, easier
Bind mount (/host/path:/container/path): Direct mapping to host filesystem, more control


docker run -it --rm \
  -e POSTGRES_USER="root" \      (ustawienie zmiennej srodowiskowej wewnatrz kontenera)
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5433:5432 \         (przekierowanie ruchu sieciowego PORT_HOSTA:PORT_KONTENERA)
  --name postgres_db \
  postgres:18


uv add --dev pgcli
uv run pgcli -h localhost -p 5432 -u root -d ny_taxi

Roznica pomiedzy NamedVolumed a bindMount

Named Volume - tworzony i zarzadzany bezposrednio przez dockera w dedykowanym katalogu systemowym, lokalizacja ukryta w strukturze dockera

Bindmount  - bezposrednie podpiecie istniejącego katalogu z dysku hosta.





# 5,6 data ingestion 
uv add --dev jupyter
uv add ipykernel
uv run python -m ipykernel install --user --name pipeline-venv --display-name "Python (.venv)"

uv run jupyter notebook

uv run jupyter nbconvert --to=script notebook.ipynb
mv .\nyc_taxi_notebook.ipynb ingest_data.py


utworzenie skryptu ktora wyczta dane i załaduje je chunkami do postgresa. 

Biblioteka click do podawania parametrow skryptu:
@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default=5433, type=int, help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option(
    '--target-table', default='yellow_taxi_data', help='Target table name'
)
def run(pg_user, pg_pass, pg_host, pg_port, pg_db, target_table):
    pass



# 7. pgadmin

docker network create pg-network

docker run -it -d   -e POSTGRES_USER="root"   -e POSTGRES_PASSWORD="root"   -e POSTGRES_DB="ny_taxi"   -v ny_taxI_postgres_data:/var/lib/postgresql   -p 5433:5432   --network=pg-network   --name pgdatabase   postgres:18

docker run -it -d\
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -v pgadmin_data:/var/lib/pgadmin \
  -p 8085:80 \
  --network=pg-network \
  --name pgadmin \
  dpage/pgadmin4


  # 8 dockerazing ingestion
  docker build -f Dockerfile.ingestion -t pipe:ingestion .
  docker run -it --network=pg-network  pipe:ingestion --pg-host=pgdatabase --pg-po
rt=5432

# 9