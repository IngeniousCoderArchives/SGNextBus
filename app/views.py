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
#sitemap = "http://172.245.156.101:4996/"
#sitemap = "http://localhost:5000/" #for debug purposes
sitemap = "https://ingenious-sgnextbus.herokuapp.com"




@app.route("/",methods=["GET","POST"])
def main():
  if request.method == "POST":
      if request.form.get('bsc') is not None and request.form.get("blc") is not None:
        return redirect(f"{sitemap}?busstop={request.form.get('bsc')}&busloc={request.form.get('blc')}")
      if request.form.get('bsc') is not None:
        return redirect(f"{sitemap}?busstop={request.form.get('bsc')}")
      else:
        return redirect(url_for("main"))
  if request.args.get("busstop") == None:
    table = ["Enter a bus stop code above first."]
    return render_template("base.html",home=False,tables=table,busstopcode="Undefined",codes=["Null"])
  else:
    bus_stop = request.args.get("busstop")
    url = f'http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2?BusStopCode={int(bus_stop)}'
    headers = {'AccountKey': os.environ.get("APITOKEN")}
    r = requests.get(url, headers=headers)
    data_got = r.json()
    #Time to process data and show
    main_data = data_got["Services"]
    items = []
    urls = {}
    for service in main_data:
        next_bus_data = service["NextBus"] #is a dict
        nextn_bus_data = service["NextBus2"] #is anotherdict
        try:
          item2 = Item(service["ServiceNo"],operator(service["Operator"]),next_bus_data["EstimatedArrival"].split("T")[1].split("+")[0],Veh(next_bus_data["Type"]),Load(next_bus_data["Load"]),nextn_bus_data["EstimatedArrival"].split("T")[1].split("+")[0])
          items.append(item2)
          lat = next_bus_data["Latitude"]
          long = next_bus_data["Longitude"]
          if lat == 0:
            pass
          else:
            URL = """<script src='https://maps.googleapis.com/maps/api/js?v=3.exp&key=AIzaSyD_hce37QhlyI59U2KDKiTEJMSlns47d6E'></script><div style='overflow:hidden;height:440px;width:700px;'><div id='gmap_canvas' style='height:440px;width:700px;'><div style="position:absolute; top:-70px; display:block; text-align:center; z-index:-1;"><a href="https://ukgaynews.org.uk">https://ukgaynews.org.uk</a></div></div><script type='text/javascript'>function init_map(){var myOptions = {zoom:17,center:new google.maps.LatLng("""+lat+","+long+"""),mapTypeId: google.maps.MapTypeId.ROADMAP,fullscreenControl:false,scaleControl:false,draggable:true,streetViewControl:true};map = new google.maps.Map(document.getElementById('gmap_canvas'), myOptions);marker = new google.maps.Marker({map: map,position: new google.maps.LatLng("""+lat+","+long+""")});}google.maps.event.addDomListener(window, 'load', init_map);</script><div><small><a href="https://www.embedgooglemap.co.uk">Embed Google Map</a></small></div>"""
            urls[service["ServiceNo"]] = URL
        except Exception as e:
          print(e)
          pass
    #bus locations
    if request.args.get("busloc") is None:
      return render_template("base.html",home=False,busstopcode = bus_stop, table=ItemTable(items))
    else:
      #grr now need process the embed map HAIZZZtm
      service2 = None
      for service in main_data:
        if str(service["ServiceNo"]) == str(request.args.get("busloc")):
          service2 = service
      if service2 is None:
        if request.args.get("busloc") == "":
          return render_template("base.html",home=False,busstopcode = bus_stop, table=ItemTable(items),bus2="")
        return render_template("base.html",home=False,busstopcode = bus_stop, table=ItemTable(items),bus2="Could not find location of specified service.")
      lat = service2["NextBus"]["Latitude"]
      long = service2["NextBus"]["Longitude"]
      print(lat)
      if lat == "0":
        return render_template("base.html",home=False,busstopcode = bus_stop, table=ItemTable(items),bus2="Bus is still at Interchange!")
      URL = """<script src='https://maps.googleapis.com/maps/api/js?v=3.exp&key=AIzaSyD_hce37QhlyI59U2KDKiTEJMSlns47d6E'></script><div style='overflow:hidden;height:440px;width:700px;'><div id='gmap_canvas' style='height:440px;width:700px;'><div style="position:absolute; top:-70px; display:block; text-align:center; z-index:-1;"><a href="https://ukgaynews.org.uk">https://ukgaynews.org.uk</a></div></div><script type='text/javascript'>function init_map(){var myOptions = {zoom:17,center:new google.maps.LatLng("""+lat+","+long+"""),mapTypeId: google.maps.MapTypeId.ROADMAP,fullscreenControl:false,scaleControl:false,draggable:true,streetViewControl:true};map = new google.maps.Map(document.getElementById('gmap_canvas'), myOptions);marker = new google.maps.Marker({map: map,position: new google.maps.LatLng("""+lat+","+long+""")});}google.maps.event.addDomListener(window, 'load', init_map);</script><div><small><a href="https://www.embedgooglemap.co.uk">Embed Google Map</a></small></div>"""
      return render_template("base.html",home=False,busstopcode = bus_stop, table=ItemTable(items),bus2=f"Next {service2['ServiceNo']} location",bus4=URL)

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
    def __init__(self, svcno, operator, nextbus, veh, load, nextbus2):
      self.svcno = svcno
      self.operator = operator
      self.nextbus = nextbus
      self.nextbus2 = nextbus2
      self.veh = veh
      self.load = load

class ItemTable(Table):
    svcno = Col("Service Number")
    operator = Col("Operator")
    nextbus = Col("Estimated Next Bus Arrival Time")
    veh = Col ("Vehicle Type")
    load = Col("Vehicle Load")
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


    """ MAP PLOT REFERENCE
      https://python-graph-gallery.com/310-basic-map-with-markers/
      https://matplotlib.org/basemap/users/examples.html"""
