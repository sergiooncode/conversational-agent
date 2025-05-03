FROM python:3.13.3 as base

ARG APP_ENV=production
ARG PYTEST_ADDOPTS=""
ARG GITHUB_TOKEN=""

ENV APP_ENV=$APP_ENV
ENV PYTHONPATH=/opt/orbio
ENV PYTHONUNBUFFERED=1
ENV PYTHONBREAKPOINT=ipdb.set_trace
ENV PYTEST_ADDOPTS=$PYTEST_ADDOPTS

RUN addgroup orbio && useradd -u 1000 orbio -g orbio

COPY --chown=orbio:orbio ./requirements /opt/requirements

RUN apt-get update --yes && \
    apt-get upgrade --yes && \
    apt-get install --no-install-recommends --yes postgresql-client && \
    pip install --no-cache-dir --disable-pip-version-check pip-tools && \
    pip-sync /opt/requirements/base.txt --pip-args '--no-cache-dir --no-deps --disable-pip-version-check' && \
    rm -rf /var/lib/apt/lists/*

FROM base

RUN echo $APP_ENV

RUN if [ $APP_ENV = 'production' ] ; \
    then \
    pip-sync /opt/requirements/base.txt --pip-args '--no-cache-dir --no-deps --disable-pip-version-check' ; \
    fi

RUN if ! [ $APP_ENV = 'production' ] ; \
    then \
    pip-sync /opt/requirements/base.txt /opt/requirements/test.txt /opt/requirements/linting.txt --force /opt/requirements/base.txt --pip-args '--no-cache-dir --no-deps --disable-pip-version-check'; \
    fi

ENV PYCURL_SSL_LIBRARY=openssl
RUN pip uninstall pycurl && \
  pip install pycurl --compile --global-option="--with-openssl" --no-cache-dir

COPY --chown=orbio:orbio . /opt/orbio/

RUN chmod 775 -R /opt/orbio/

RUN mkdir /home/orbio
RUN chmod 775 -R /home/orbio/
RUN chown orbio:orbio -R /home/orbio/

USER orbio

WORKDIR /opt/orbio/src

ARG APP_VERSION
ENV APP_VERSION=$APP_VERSION

EXPOSE 8004

CMD gunicorn -c ./agent/gunicorn_conf.py -k agent.uvicorn.UvicornWorker agent.asgi:application
