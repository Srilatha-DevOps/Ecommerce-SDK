FROM python:3

ADD ./message.py /
RUN pip install boto3
RUN pip install fpdf

CMD [ "python", "/message.py" ]                               