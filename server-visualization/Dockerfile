FROM python
RUN pip install flask flask-socketio plotly influxdb
ADD src /src
WORKDIR /src
ENTRYPOINT ["python", "main.py"]
