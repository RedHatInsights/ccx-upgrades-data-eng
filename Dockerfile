FROM registry.access.redhat.com/ubi8-minimal:8.8-1037

ENV VENV=/ccx-upgrades-data-eng-venv\
    HOME=/ccx-upgrades-data-eng

RUN microdnf install --nodocs --noplugins -y python3.11 git-core

WORKDIR $HOME

COPY . $HOME

ENV PATH="$VENV/bin:$PATH"

RUN python -m venv $VENV
RUN pip install --verbose --no-cache-dir -U pip setuptools wheel
RUN pip install --verbose --no-cache-dir -r requirements.txt
RUN pip install .

# Clean up not necessary packages for runtime
# remove py if present as it is not maintained and vulnerable (https://pypi.org/project/py/)
# remove pip as it is not necessary during runtime
RUN pip uninstall -y \
    py \
    pip

RUN microdnf remove -y git-core openssh-clients openssh
RUN microdnf clean all

USER 1001

EXPOSE 8000

CMD ["uvicorn", "ccx_upgrades_data_eng.main:app", "--host=0.0.0.0", "--port=8000", "--log-config=logging.yaml"]
