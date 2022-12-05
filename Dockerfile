ARG PYTHON_VERSION=3.10-slim-bullseye

# define an alias for the specfic python version used in this file.
FROM python:${PYTHON_VERSION} as python

# Python build stage
FROM python as python-build-stage

# ARG BUILD_ENVIRONMENT=local
# ARG BUILD_DEPS="gcc"
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Install required system dependencies
# RUN apt-get update && \
#     apt-get install --no-install-recommends -y ${BUILD_DEPS} && \
#     # cleaning up unused files
#     apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
#     apt-get autoremove --purge -y && \
#     apt-get clean && \
#     rm -rf /tmp/* /var/lib/apt/lists/* /var/tmp/ 

# Requirements are installed here to ensure they will be cached.
COPY ./requirements.txt .

# Create Python Dependency and Sub-Dependency Wheels.
RUN pip install --upgrade pip && \
    pip wheel --wheel-dir /usr/src/app/wheels -r requirements.txt


# Python 'run' stage
FROM python as python-run-stage

ARG APP_HOME=/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR ${APP_HOME}

# All absolute dir copies ignore workdir instruction. All relative dir copies are wrt to the workdir instruction
# copy python dependency wheels from python-build-stage
COPY --from=python-build-stage /usr/src/app/wheels  /wheels/

# use wheels to install python dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
    && rm -rf /wheels/

COPY ./scripts /
# COPY ./scripts/entrypoint.sh /entrypoint
# COPY ./scripts/start-streamlit.sh /start-streamlit
# COPY ./scripts/start-worker.sh /start-worker
# COPY ./scripts/start-flower.sh /start-flower

RUN sed -i 's/\r$//g' /entrypoint.sh && \
    sed -i 's/\r$//g' /start-streamlit.sh && \
    sed -i 's/\r$//g' /start-worker.sh && \
    sed -i 's/\r$//g' /start-flower.sh && \
    chmod +x /entrypoint.sh && \
    chmod +x /start-streamlit.sh && \
    chmod +x /start-worker.sh && \
    chmod +x /start-flower.sh

# copy application code to WORKDIR
# COPY ./src ${APP_HOME}

ENTRYPOINT ["/entrypoint.sh"]