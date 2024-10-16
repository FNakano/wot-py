FROM python:3.7
ENV PATH_APP /app

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y tshark vim libdb5.3++-dev && \
    groupadd wireshark && \
    usermod -aG wireshark root && \
    setcap 'CAP_NET_RAW+eip CAP_NET_ADMIN+eip' /usr/bin/dumpcap && \
    chgrp wireshark /usr/bin/dumpcap && \
    chmod 750 /usr/bin/dumpcap

RUN mkdir -p ${PATH_APP}
WORKDIR ${PATH_APP}
COPY . .
RUN pip install -U .
WORKDIR ${PATH_APP}/examples/uv_sensor
RUN pip install -r requirements.txt
WORKDIR ${PATH_APP}

RUN useradd -m myuser
USER myuser
