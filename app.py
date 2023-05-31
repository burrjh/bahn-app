from flask import Flask, jsonify
import pandas  as  pd
from math import radians, cos, sin, asin, sqrt

# read csv
data = pd.read_csv("data.CSV", delimiter=";", decimal=",")

# only select Fernverkehrsbahnhöfe and relevant columns
cols = ["NAME", "DS100", "Laenge", "Breite"]
df = data[data["Verkehr"]=="FV"][cols]


def haversine(longitude1, latitude1, longitude2, latitude2, metric="km"):
    """
    Calculate the haversine distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    longitude1, latitude1, longitude2, latitude2 = map(radians, [longitude1, latitude1, longitude2, latitude2])

    # haversine formula 
    dlon = longitude2 - longitude1 
    dlat = latitude2 - latitude1 
    a = sin(dlat/2)**2 + cos(latitude1) * cos(latitude2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 

    if metric=="km":
        r = 6371 # Radius of earth in kilometers
    elif metric=="miles":
        r = 3956
    else: 
        raise NotImplementedError
    
    return c * r


app = Flask(__name__)

@app.route('/api/v1/distance/<string_1>/<string_2>', methods=['GET'])
def create_response(string_1, string_2):
    """
    Function creating the response for the API
    takes two strings, which need to be the abrevations
    matching the database, then calculates the distance,
    and creates the response
    """

    # select both stations based on accronym given
    bahnhof1 = df[df["DS100"]==string_1]
    bahnhof2 = df[df["DS100"]==string_2]

    # raise exception if one input does not match
    if len(bahnhof1)+len(bahnhof2)<2:
        raise Exception

    # calculate beeline between stations via haversine formula
    distance = haversine(bahnhof1["Laenge"].item(),
                        bahnhof1["Breite"].item(),
                        bahnhof2["Laenge"].item(),
                        bahnhof2["Breite"].item())

    # define json response
    response = {
        'from': bahnhof1["NAME"].item(),
        'to': bahnhof2["NAME"].item(),
        'distance': round(distance),
        'unit': "km"
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)

