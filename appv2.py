import json    # json library for parsing the json response
import os	
import requests	# requests library to make http requests

from flask import Flask 	# deploy locally 
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)
api_key = "834a9b7f16ee88ea566bfe15b38106ac"	#openweather api key


@app.route('/webhook', methods=['POST'])	# webhook call in post method
def webhook():
    req = request.get_json(silent=True, force=True)	# store the response in the req variable

    print("Request:")
   
    print(json.dumps(req, indent=4))		# convert to json format

    res = processRequest(req)			# pass through the processRequest() function
 
    res = json.dumps(res, indent=4)		
    #print(res)
    r = make_response(res)			# make response with fulfillment text
    r.headers['Content-Type'] = 'application/json'	# make it json format
    return r					# return the response


def processRequest(req):
	print ("here I am....")			# just some debug prints
	print ("starting processRequest...",req.get("queryResult").get("action"))

	action = req.get("queryResult").get("action") 	# get action from the query

	if action == "weather":				# if action is weather
		result = req.get("queryResult")		# get city parameter and pass it to the weather handler function.
		parameters = result.get("parameters")
		city_name = parameters.get("geo-city")
		res = weatherHandler(city_name)
		
	elif action == "gettime":			# if action is time call timeHandler function
		res = timeHandler()
		
	elif action == "gsheet":			# if action is google sheet
		result = req.get("queryResult")		# get name parameter from the query and pass it to sheetHandler function
		parameters = result.get("parameters")
		given_name = parameters.get("given-name")
		res = sheetHandler(given_name)

	elif action == "gesture":			# if action is gesture then call gestureHandler function
		res = gestureHandler()

	return res

def gestureHandler():
	speech = "This a responese from the gesture recognition, just a change here!!!!"  # just change the speech variable as required output. Default I kept some text 
	return {
	"fulfillmentText": speech,
	 "source": "Gesture"
	}	

def sheetHandler(given_name):
	response = requests.get("https://sheetdb.io/api/v1/rx7k724w4ek8h")		# call gsheet api  and get response , construct a response if person found or not found 
	x = response.json()								# return the speech
	speech = "I haven't found the details for the "+given_name +"in my database."
	for person in x:
		if person["Name"] == given_name:
			speech = 'Here are the details for '+ person["Name"] +' Age :'+person["Age"]+', Designation :'+person["Designation"]+', Phone number: '+person["PhoneNumber"];
			
	return {									
	"fulfillmentText": speech,
	 "source": "Google Sheets"
	}
	
	
def timeHandler():
	response = requests.get("http://worldtimeapi.org/api/timezone/Asia/Kolkata")	# call time api and parse for datetime and construct a speech response and return it
	x = response.json()
	timenow = x["datetime"]
	slicetime = timenow[11:19]
	speech = 'Now the time is : ' + slicetime;
	return {
	"fulfillmentText": speech,
	 "source": "IST"
	}

def weatherHandler(city_name):							# add the city name to the base url and get the response. pass the response to the weatherresult1  
	base_url = "http://api.openweathermap.org/data/2.5/weather?"		# function
	complete_url = base_url + "appid=" + api_key + "&q=" + city_name 
	response = requests.get(complete_url)
	x = response.json()
	ftext = weatherResult1(x)
	return ftext
 



def weatherResult1(x):
	if x["cod"] != "404": 							# if api call successfull

		# store the value of "main" 
		# key in variable y 
		y = x["main"] 							# parse through the json to get all requires params
	  
		# store the value corresponding 
		# to the "temp" key of y 
		current_temperature = y["temp"] 				# get temperaure and convert it to celcuis from kelvin, rounding to 1 decimal
		current_temperature -= 273.15
		current_temperature  = round(current_temperature,1)
		# store the value corresponding 
		# to the "pressure" key of y 
		current_pressure = y["pressure"] 				# get pressure and  rounding to 1 decimal
		current_pressure = round(current_pressure,1)
	  
		# store the value corresponding 
		# to the "humidity" key of y 
		current_humidiy = y["humidity"] 				# get humidity and  rounding to 1 decimal
		current_humidiy = round(current_humidiy,1)
	  
		# store the value of "weather" 
		# key in variable z 
		z = x["weather"] 
	  
		# store the value corresponding  
		# to the "description" key at  
		# the 0th index of z 
		weather_description = z[0]["description"]			# get weather description 
	  
		# print following values 					# construct a speech response with all the params and text
		speech = " Temperature (in celcius unit) = " + str(current_temperature) + "\n atmospheric pressure (in hPa unit) = " + str(current_pressure) +"\n humidity (in percentage) = " +str(current_humidiy) +"\n\n description = " +str(weather_description) 
	  
	else: 
		speech= " City Not Found "						

	return {
	"fulfillmentText": speech,
	 "source": "Open Weather"
	}

@app.route('/test', methods=['GET'])						# to test it working just check "localhost:5000/test"
										# you should see the response "Hello there my friend !!"
def test():
    return  "Hello there my friend !!"


@app.route('/static_reply', methods=['POST'])					# testing in dialogflow , in webhook url just keep "[public_url]/static_reply"
def static_reply():
    speech = "Hello there, this reply is from the webhook !! "			# you will see "You are awesome !! just a change here"
    string = "You are awesome !! just a change here"
    Message ="this is the message"

    my_result =  {

    "fulfillmentText": string,
     "source": string
    }

    res = json.dumps(my_result, indent=4)

    r = make_response(res)

    r.headers['Content-Type'] = 'application/json'
    return r



if __name__ == '__main__':


    port = int(os.getenv('PORT', 5000))					# set port to 5000 bcs it should be unique

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')			# run the app
