FROM ruby@sha256:5340ab7cd6317c45a0a7e2818857b930ff61ee92ffd661dec72738e42dd2cddf

COPY gems.lock.json install.rb /opt/study/

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && ruby /opt/study/install.rb \
 && apt-get purge -y --auto-remove build-essential \
 && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 1000 runner
USER runner
WORKDIR /work
CMD ["ruby", "test.rb"]
