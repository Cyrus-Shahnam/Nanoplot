FROM kbase/sdkpython:3.8.0

LABEL maintainer="ac.shahnam"

# Install NanoPlot via pip
RUN pip install --upgrade pip && \
    pip install NanoPlot==1.41.0

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT ["./scripts/entrypoint.sh"]
CMD []

