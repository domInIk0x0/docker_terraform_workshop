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


# 2. Virutal env
uv init --python=3.13 (biblioteka)
uv add pandas pyarrow --link-mode=copy