FROM python:3.14-slim
ENV POETRY_VIRTUALENV_CREATE=false

WORKDIR app/


# copia primeiro as pastas de dependencias, pois elas mudam raramente.
# se elas mudam, as instrucoes sao rodadas por seguranca. Se elas nao mudam, as instrucoes
# nao serao rodadas pois o Docker entende q se elas nao mudam as instrucoes nao mudaram
COPY pyproject.toml poetry.lock ./ 

RUN pip install poetry 
RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi --no-root --without dev

# por isso se coloca os aruqivos.py aqui, se nao ele sempre iria rodar as instrucoes pois esses arquivos sempre mudam
COPY . .

EXPOSE 8000