
FROM python:3.9-slim-buster
WORKDIR /app

COPY requirements.txt /tmp/requirements.txt

# COPY ./init_setup.sh .
RUN echo "[ `date` ]": "START"
RUN echo "[ `date` ]": "Creating virtual env" 
RUN python3 -m venv venv/
RUN echo "[ `date` ]": "activate venv"
RUN . venv/bin/activate
RUN echo "[ `date` ]": "installing the requirements" 
RUN python3 -m pip install -r /tmp/requirements.txt
RUN echo "[ `date` ]": "creating folders and files" 
# RUN python3 template.py
RUN echo "[ `date` ]": "END"
COPY . .
EXPOSE 5000
ENV FLASK_APP=app.py
CMD ["flask", "run", "--host", "0.0.0.0"]