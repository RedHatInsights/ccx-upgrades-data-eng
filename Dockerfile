FROM registry.access.redhat.com/ubi9-minimal:latest

ENV VENV=/ccx-upgrades-data-eng-venv\
    HOME=/ccx-upgrades-data-eng

WORKDIR $HOME

COPY . $HOME
ENV PATH="$VENV/bin:$PATH"
RUN microdnf install --nodocs --noplugins -y python3.11 git-core &&\
    python3.11 -m venv $VENV && \
    pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir .

# Clean up not necessary packages for runtime
# remove py if present as it is not maintained and vulnerable (https://pypi.org/project/py/)
# remove pip as it is not necessary during runtime
RUN pip uninstall -y \
    py \
    pip

RUN microdnf remove -y git-core
RUN microdnf clean all
RUN rpm -e --nodeps sqlite-libs krb5-libs libxml2 readline pam openssh openssh-clients

USER 1001

EXPOSE 8000

CMD ["uvicorn", "ccx_upgrades_data_eng.main:app", "--host=0.0.0.0", "--port=8000", "--log-config=logging.yaml"]
