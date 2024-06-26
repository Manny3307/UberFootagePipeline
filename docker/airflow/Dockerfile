# Base Image
FROM spark-base:latest
LABEL maintainer="MarcLamberti"

# Arguments that can be set with docker build
ARG AIRFLOW_VERSION=2.0.1
ARG AIRFLOW_HOME=/opt/airflow

# Export the environment variable AIRFLOW_HOME where airflow will be installed
ENV AIRFLOW_HOME=${AIRFLOW_HOME}

# Install dependencies and tools
RUN apt-get update -y && \
    apt-get upgrade -yqq && \
    apt-get install -yqq --no-install-recommends \
    python3-dev \
    wget \
    libczmq-dev \
    curl \
    libssl-dev \
    git \
    inetutils-telnet \
    bind9utils freetds-dev \
    libkrb5-dev \
    libsasl2-dev \
    libffi-dev libpq-dev \
    freetds-bin build-essential \
    default-libmysqlclient-dev \
    apt-utils \
    rsync \
    zip \
    unzip \
    gcc \
    vim \
    netcat \
    && apt-get autoremove -yqq --purge && apt-get clean

COPY ./requirements-python3.7.txt /requirements-python3.7.txt

# Upgrade pip
# Create airflow user 
# Install apache airflow with subpackages
RUN pip install --upgrade "pip==20.2.4" && \
    useradd -ms /bin/bash -d ${AIRFLOW_HOME} airflow && \
    pip install apache-airflow==${AIRFLOW_VERSION} --constraint /requirements-python3.7.txt && \
    pip install apache-airflow-providers-apache-hdfs==1.0.1 && \
    pip install apache-airflow-providers-apache-hive==1.0.2 && \
    pip install apache-airflow-providers-apache-spark==1.0.2 && \
    pip install apache-airflow-providers-slack==3.0.0 && \
    pip install apache-airflow-providers-http==1.1.1

#Install tqdm used for showing progress bar in FTP module
RUN apt-get install nano -y
RUN apt-get update -y
RUN apt-get install -y python-tqdm
RUN pip install tqdm python-dotenv

# Copy the airflow.cfg file (config)
#COPY ./config/airflow.cfg ${AIRFLOW_HOME}/airflow.cfg

# Create the folder to store the batch files of the Upload Process
RUN mkdir /upload_batch
RUN chmod 777 /upload_batch

# Set the owner of the files in AIRFLOW_HOME to the user airflow
RUN chown -R airflow: ${AIRFLOW_HOME}

# Copy the entrypoint.sh from host to container (at path AIRFLOW_HOME)
COPY ./start-airflow.sh ./start-airflow.sh

# Set the entrypoint.sh file to be executable
RUN chmod +x ./start-airflow.sh

# Set the username to use
USER airflow

# Create the folder dags inside $AIRFLOW_HOME
RUN mkdir -p ${AIRFLOW_HOME}/dags

ENV PATH="${PATH}:/opt/airflow/dags"


# Expose ports (just to indicate that this container needs to map port)
EXPOSE 8080

# Execute start-airflow.sh
CMD [ "./start-airflow.sh" ]

    