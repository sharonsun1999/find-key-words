from django.http import HttpResponse
from django.shortcuts import render,render_to_response
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from datetime import timedelta
import types
import math
import csv
import urllib2, json
import googlemaps
import os.path
BASE = os.path.dirname(os.path.abspath(__file__))
file=open(os.path.join(BASE, "sfpd_dispatch_data_subset.csv"))

#Read the date set
#file=open('sfpd_dispatch_data_subset.csv','r')
read=csv.reader(file)
data=[]
unitType={}
#Create a seqeuence to save the data
for item in read:
	if read.line_num==1:
		continue
	data.append(item)
for item in data:
	#Convert the call time to a datetime object
	calls=(datetime.strptime(item[6][:19],'%Y-%m-%d %H:%M:%S'))
	epochs=datetime.strptime(item[6][:11]+'00:00:00','%Y-%m-%d %H:%M:%S')
	#Calculate the call time in seconds
	intervals=(calls-epochs).total_seconds()
	#Make the format of addresses readable
	location=item[15].partition('/')[0]
	if not item[16]:
		item[16]='San Francisco'
	#Map each case's call time and address to the unit type it required
	unitType[(intervals,location+', '+item[16]+', CA')]=item[27]
#Implement googlemaps API
gmaps = googlemaps.Client(key='AIzaSyC62SGhTaCnwWgfcnMsf6VJ6669bpnrz-s')

#Find the area with longest dispatch time
zipCode={}
averageTime={}
#Divide the calls into regions by zip code
for item in data:
	zipCode[item[17]]=[]
for item in data:
	zipCode[item[17]].append(item)
#Compute the time the call is received and a unit is dispatched
for region in zipCode.keys():
	total=0
	number=0
	for item in zipCode[region]:
		#Convert the time of the call being received into a datetime object
		receive=(datetime.strptime(item[6][:19],'%Y-%m-%d %H:%M:%S'))
		#Convert the time of the unit being dispatched into a datetime object
		dispatch=(datetime.strptime(item[8][:19],'%Y-%m-%d %H:%M:%S'))
		#Compute the interval between these two events in seconds
		dispTime=(dispatch-receive).total_seconds()
		#Compute the total dispatch time for the calls with this zip code
		total+=dispTime
		#Compute the number of calls with this zip code
		number+=1
	#Compute the average dispatch time for each region
	averageTime[region]=float(total/number)
#Find the region with longest dispatch time
maximum=float('-inf')
for region in averageTime.keys():
	if averageTime[region]>maximum:
		maximum=averageTime[region]
		longest=region

def findPotentialDispatch(callTime,address):
	'''
	Given an address and time, return the most likely dispatch types to be required.
	'''
	#Convert the calltime into a datetime object
	call=(datetime.strptime(callTime,'%Y-%m-%d %H:%M:%S'))
	epoch=datetime.strptime(callTime[:11]+'00:00:00','%Y-%m-%d %H:%M:%S')
	#Compute the calltime in seconds
	interval=(call-epoch).total_seconds()
	units={}
	potential={}
	sequence=[]
	#Pick out the cases with similar call time from data set
	for example in unitType.keys():
		if abs(interval-example[0])<5:
			potential[example[1]]=unitType[example]
			sequence.append(example[1])
	#Compute the distances from the input addresses to the addresses of the chosen cases
	distances=gmaps.distance_matrix(address,sequence)
	for k in range(len(sequence)):
		#Check the unit of the distances computed and pick out the addresses near the input address
		if str(distances['rows'][0]['elements'][k]['distance']['text'][-2])=='k':
			if abs(float(distances['rows'][0]['elements'][k]['distance']['text'][:-3])<5):
				#Compute the number of each unit types in the chosen cases
				if potential[sequence[k]] in units:
					units[potential[sequence[k]]]+=1
				else:
					units[potential[sequence[k]]]=1
		else:
			if potential[sequence[k]] in units:
				units[potential[sequence[k]]]+=1
			else:
				units[potential[sequence[k]]]=1
	#Compute the probability that each unit type is required
	total=sum(units.values())
	uni=''
	for unit in units.keys():
		uni+=(str(unit)+': '+str(round(100*(float(units[unit])/total),2))+'% ')
	return uni


def index(request):
	return render(request, 'index.html',{'region':longest,'interval':round(maximum,2)})

@csrf_exempt
def textpost(request):
	if request.method == "GET":
		place=request.GET['address']
		time=request.GET['date']+' '+request.GET['time']+':00'
		probility=findPotentialDispatch(time,place)
		change={'prob':probility}
		return render(request, 'index.html',change)