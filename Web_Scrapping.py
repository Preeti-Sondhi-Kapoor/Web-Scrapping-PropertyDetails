from flask import Flask, render_template, request,jsonify
#from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import csv
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
#@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
#@cross_origin()
def index():
    if request.method == 'POST':
        try:
            # You can change the State, StartPageRange and EndPageRange here
            State = request.form['content'].replace(" ", "")  #"Kuala-Lumpur"
            StartPageRange = 1
            EndPageRange = 2


            datafile = "mudah1_" + State.lower() + "_page" + str(StartPageRange) + "to" + str(EndPageRange - 1) + ".csv"
            with open(datafile, 'a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                headers = "PostedDate", "PropertyName", "CategoryType", "PropertyType", "City", "State", "Furnishing",
                "BuiltUpSize", "AgeofProperty", "RentalDeposit", "NoOfBedroom", "NoOfBathroom", "NoOfParking",
                "RentalPerMth", "Facilities", "OtherFacilities", "SourceUrl"
                writer.writerow(headers)

            all_links = []
            for i in range(StartPageRange, EndPageRange):
                    firsturl = "https://www.mudah.my/" + State + "/Properties-for-rent-2002?o=" + str(i) + "&q=&so=1&th=1"
                    response = urlopen(firsturl)
                    html=response.read()
                    data = BeautifulSoup(html, 'lxml')
                    prop_urls = data.find_all("h2", {"class": "list_title"})
                    urls = prop_urls[:40]
                    for links in urls:
                        links.find_all("a")
                        for link in links:
                            try:
                                all_links.append(link.get("href"))
                            except:
                                pass
                    if 'https://www.mudah.my/honeypot.html' in all_links:
                        all_links.remove('https://www.mudah.my/honeypot.html')
            reviews = []
            for i in range(len(all_links)):
                ind_page_response = urlopen(all_links[i])
                data2 = BeautifulSoup(ind_page_response.read(), 'lxml')
                SourceUrl = all_links[i]

                prop_name = data2.find("h2", {"class": "roboto"})
                PropertyName = prop_name.text.strip()
                for i in range(len(data2.select('.params dt'))):
                    if data2.select('.params dt')[i].text == "Property Type":
                        PropertyType = data2.select('.params dd')[i].text

                if data2.find("dd", {"class": "loc_dd"}) != None:
                           City = data2.find("dd", {"class": "loc_dd"}).text.strip().split(" - ")[1]

                if data2.find("dd", {"class": "loc_dd"}) != None:
                           State = data2.find("dd", {"class": "loc_dd"}).text.strip().split(" - ")[0]

                for i in range(len(data2.select('.params dt'))):
                       if data2.select('.params dt')[i].text == "Size":
                              BuiltUpSize = data2.select('.params dd')[i].text
                              BuiltUpSize = float(BuiltUpSize.strip(' sq.ft.'))

                NoOfBedroom = ''
                for i in range(len(data2.select('.params dt'))):
                      if data2.select('.params dt')[i].text == "Bedrooms":
                            NoOfBedroom = data2.select('.params dd')[i].text
                            NoOfBedroom = int(NoOfBedroom)

                NoOfBathroom = ''
                for i in range(len(data2.select('.params dt'))):
                    if data2.select('.params dt')[i].text == "Bathroom":
                       NoOfBathroom = data2.select('.params dd')[i].text
                       NoOfBathroom = int(NoOfBathroom)

                NoOfParking = ''
                for i in range(len(data2.select('.params dt'))):
                      if data2.select('.params dt')[i].text == "Carpark":
                          NoOfParking = data2.select('.params dd')[i].text
                          NoOfParking = int(NoOfParking)

                Furnishing = ''
                for i in range(len(data2.select('.params dt'))):
                      if data2.select('.params dt')[i].text == "Furnished":
                          Furnishing = data2.select('.params dd')[i].text

                Facilities = ''
                for i in range(len(data2.select('.params dt'))):
                     if data2.select('.params dt')[i].text == "Facilities":
                          Facilities = data2.select('.params dd')[i].text

                OtherFacilities = ''
                for i in range(len(data2.select('.params dt'))):
                    if data2.select('.params dt')[i].text == "Other Facilities":
                       OtherFacilities = data2.select('.params dd')[i].text

                AgeofProperty = ''
                for i in range(len(data2.select('.params dt'))):
                    if data2.select('.params dt')[i].text == "Age of Property":
                        AgeofProperty = data2.select('.params dd')[i].text
                        AgeofProperty = int(AgeofProperty.strip(" Year(s)"))

                RentalDeposit = ''
                for i in range(len(data2.select('.params dt'))):
                    if data2.select('.params dt')[i].text == "Rental Deposit":
                        RentalDeposit = data2.select('.params dd')[i].text.strip("RM ")
                        RentalDeposit = float(RentalDeposit)

                CategoryType = ''
                CategoryType = data2.select('.highlight-title-value')[0].text

                if data2.find("dd", {"class": "dd-price"}) != None:
                   RentalPerMth = float(
                     data2.find("dd", {"class": "dd-price"}).text.strip().strip("RM").strip("(per month)").replace(" ",
                                                                                                                  ""))

                if data2.find("div", {"class": "list_time"}).text.strip().split(" ")[0] == "Today":
                    PostedDate = datetime.today().date()
                elif data2.find("div", {"class": "list_time"}).text.strip().split(" ")[0] == "Yesterday":
                    PostedDate = datetime.today().date() - timedelta(days=1)
                else:
                   PostedDate = datetime.strptime(a[:6] + " " + str(datetime.today().year), '%d %b %Y').date()

                with open(datafile, 'a', newline='', encoding='utf-8') as csv_file:
                   writer = csv.writer(csv_file)
                   writer.writerow(
                    [PostedDate, PropertyName, CategoryType, PropertyType, City, State, Furnishing, BuiltUpSize,
                     AgeofProperty, RentalDeposit, NoOfBedroom, NoOfBathroom, NoOfParking, RentalPerMth, Facilities,
                     OtherFacilities, SourceUrl])
                   mydict = {"PostedDate":PostedDate, "PropertyName":PropertyName, "CategoryType":CategoryType, "PropertyType":PropertyType, "City":City, "State":State, "Furnishing":Furnishing,"BuiltUpSize":BuiltUpSize, "AgeofProperty":AgeofProperty, "RentalDeposit":RentalDeposit, "NoOfBedroom":NoOfBedroom, "NoOfBathroom":NoOfBathroom, "NoOfParking":NoOfParking,"RentalPerMth":RentalPerMth, "Facilities":Facilities, "OtherFacilities":OtherFacilities, "SourceUrl":SourceUrl}

                   reviews.append(mydict)
            return render_template('result.html', reviews=reviews[0:(len(reviews) - 1)])
        except Exception as e:
           print('The Exception message is: ', e)
        return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    # app.run(host='127.0.0.1', port=8001, debug=True)
    app.run(debug=True)

