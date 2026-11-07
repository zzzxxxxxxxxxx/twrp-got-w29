FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

RUN sed -i \
        -e 's|azure.archive.ubuntu.com|archive.ubuntu.com|g' \
        /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        bc bison build-essential ccache curl flex g++-multilib gcc-multilib \
        git gnupg gperf imagemagick lib32ncurses5-dev lib32readline-dev \
        lib32z1-dev liblz4-tool libncurses5 libncurses5-dev libsdl1.2-dev \
        libssl-dev libxml2 libxml2-utils lzop pngcrush python3 python3-pip \
        rsync schedtool squashfs-tools unzip zip zlib1g-dev openjdk-11-jdk \
        zstd ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://storage.googleapis.com/git-repo-downloads/repo \
        -o /usr/local/bin/repo \
    && chmod +x /usr/local/bin/repo

RUN ln -sf /usr/bin/python3 /usr/local/bin/python

RUN groupadd -g 1000 builder \
    && useradd -m -u 1000 -g 1000 -s /bin/bash builder

USER builder
WORKDIR /work

CMD ["bash", "/project/docker/container-build.sh"]

