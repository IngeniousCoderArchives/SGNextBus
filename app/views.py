from flask import session, jsonify, flash, request, render_template, send_from_directory, url_for, redirect
from werkzeug.utils import secure_filename
from flask_basicauth import BasicAuth
from app import flaskapp as app
from app.request_log_adapter import RequestLogAdapter
from flask_table import Table, Col, LinkCol
from flask_httpauth import HTTPBasicAuth
import smtplib
from hashlib import md5, sha224
from werkzeug.datastructures import Authorization
from functools import wraps
import os
import ast
import requests
import re
from random import *
import passlib

app.config.update(
    SECRET_KEY=b'*dys78^7s&_0238*sj^s',
)
sitemap = "http://172.245.156.101:4996/"
#sitemap = "http://localhost:5000/" #for debug purposes









@app.route("/",methods=["GET","POST"])
def main():
  if request.method == "POST":
      return redirect(f"{sitemap}?busstop={request.form.get('bsc')}")
  if request.args.get("busstop") == None:
    table = ["Enter a bus stop code above first."]
    return render_template("base.html",home=False,tables=table,busstopcode="Undefined")
  else:
    bus_stop = request.args.get("busstop")
    url = f'http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2?BusStopCode={int(bus_stop)}'
    headers = {'AccountKey': 'censored'}
    r = requests.get(url, headers=headers)
    data_got = r.json()
    #Time to process data and show
    main_data = data_got["Services"]
    items = []
    for service in main_data:
        next_bus_data = service["NextBus"] #is a dict
        nextn_bus_data = service["NextBus2"] #is anotherdict
        try:
          item2 = Item(service["ServiceNo"],operator(service["Operator"]),next_bus_data["EstimatedArrival"].split("T")[1].split("+")[0],Veh(next_bus_data["Type"]),Load(next_bus_data["Load"]),urlmaps(next_bus_data["Latitude"],next_bus_data["Longitude"]),nextn_bus_data["EstimatedArrival"].split("T")[1].split("+")[0])
          items.append(item2)
        except:
          pass
    return render_template("base.html",home=False,busstopcode = bus_stop, table=ItemTable(items))


def urlmaps(lat, long):
    if lat == "0" or long == "0":
        return "NIL. Bus is at interchange."
    return f"http://maps.google.com/?q={lat},{long}"

def operator(op):
    if op == "SBST":
        return "SBS Transit"
    if op == "SMRT":
        return "SMRT"
    if op == "TTS":
        return "Tower Transit"
    if op == "GAS":
        return "Go Ahead"
def Load(load):
    if load == "SEA":
        return "Seats Available"
    if load == "SDA":
        return "Standing Available"
    if load == "LSD":
        return "Limited Standing"

def Veh(veh):
    if veh == "SD":
        return "Single Deck"
    if veh == "DD":
        return "Double Deck"
    if veh == "BD":
        return "Bendy"


class Item(object):
    def __init__(self, svcno, operator, nextbus, veh, load, position, nextbus2):
      self.svcno = svcno
      self.operator = operator
      self.nextbus = nextbus
      self.nextbus2 = nextbus2
      self.veh = veh
      self.load = load
      self.position = position

class ItemTable(Table):
    svcno = Col("Service Number")
    operator = Col("Operator")
    nextbus = Col("Estimated Next Bus Arrival Time")
    veh = Col ("Vehicle Type")
    load = Col("Vehicle Load")
    position = Col("Vehicle Position")
    nextbus2 = Col("Estimated Subsequent Bus Arrival Time")





    """
    # docs https://www.mytransport.sg/content/dam/datamall/datasets/LTA_DataMall_API_User_Guide.pdf
    # http://docs.python-requests.org/en/master/user/quickstart/#make-a-request
    import requests
    url = 'http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2?BusStopCode=47619'
    headers = {'AccountKey': 'n0BRYviXS/GN+If2gylTjg=='}
    r = requests.get(url, headers=headers)
    print(r.json())

    # http://maps.google.com/?q=[lat],[long]
    input("Press enter to exit.")

    """
