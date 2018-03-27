## proj_nps.py



import requests
from bs4 import BeautifulSoup
import json as json
import secrets
import plotly.plotly as py
from plotly.graph_objs import *



mapbox_access_token = ""
base_url = "https://www.nps.gov"

######################################################
############## Setting up Two classes ################
######################################################


class NationalSite():
    def __init__(self, park_type, name, desc = "", park_url= None):#park_address_complete =""  #type
        self.name = name
        self.url = park_url
        self.description = desc        
        self.type = park_type

        ## components of address
        self.address_street = ""
        self.address_city = ""
        self.address_state = ""
        self.address_zip = ""
    
    def __str__(self):
        return "{} ({}): {}, {}, {} {}".format(self.name, self.type, self.address_street, self.address_city, self.address_state, self.address_zip)



class NearbyPlace():  ##defining a class places near by a given park
    def __init__(self, name):
        self.name = name
        self.latit = ""
        self.longit = ""

    def __str__(self):
        return self.name



######################################################
################## Set up CACHING ####################
######################################################
def make_request_using_cache(unique_url):
    CACHE_FNAME = 'StatePark_dict.json' ### opening cache file
    try:
        cache_file_name = open(CACHE_FNAME, 'r')
        cache_contents_string = cache_file_name.read()
        CACHE_DICTION = json.loads(cache_contents_string)
        cache_file_name.close()
    except:
        CACHE_DICTION = {}




    if unique_url in CACHE_DICTION:
        return CACHE_DICTION[unique_url]  ##access existing data

    else: 
        resp = requests.get(unique_url)
        CACHE_DICTION[unique_url] = resp.text # only store the html
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)  ##caching full text from webpage
        fw.close() # Close the open file
        return CACHE_DICTION[unique_url]



######################################################
########### Get Sites for a Given State  #############
######################################################

# User inputs a two-letter state abbreviation. Returns a list of all National Sites (e.g., National Parks, National Heritage Sites, etc.) that are listed for the state at nps.gov


def get_sites_for_state(state_abbr):  
    global base_url

    state_CACHE = make_request_using_cache(base_url)
    #scrape nps.gov site to find a particular state 
    state_soup = BeautifulSoup(state_CACHE, "html.parser")
    content_div = state_soup.find(class_ = "dropdown-menu SearchBar-keywordSearch")
    state_li = content_div.find_all("li")
    href_string = ""
    potential_href = "/state/" + state_abbr + "/index.htm"

    for elem in state_li:
        if elem.find("a")["href"] == potential_href:
            href_string = potential_href
            state_name = elem.text
            break

    state_homepage_url = base_url + href_string 
    park_CACHE = make_request_using_cache(state_homepage_url)
    state_soup = BeautifulSoup(park_CACHE, "html.parser")
    park_div = state_soup.find(class_ = "col-md-9 col-sm-12 col-xs-12 stateCol").find_all("h3")
    NaitonalSite_lst = []
    
    #find the park name, url for each park in the state
    for elem in park_div:

        # name = elem.text.strip()
        # park_href = elem.find("a")["href"]
        # park_url = base_url + park_href
        # park_description = elem.find("p").text    
        
        # ## go to specific park's url to find park type and address
        # park_CACHE = make_request_using_cache(park_url)  
        # park_soup = BeautifulSoup(park_CACHE, "html.parser")
        # park_type = park_soup.find(class_ = "Hero-designation").text   ## find park type

        # a_national_site = NationalSite(park_type, name, park_description, park_url)

        # address = park_soup.find(class_= "adr")  ## find park address
        # a_national_site.address_street = address.find(class_="street-address").text.strip()
        # a_national_site.address_city = address.find(itemprop="addressLocality").text.strip()
        # a_national_site.address_state = address.find(itemprop="addressRegion").text.strip()
        # a_national_site.address_zip = address.find(itemprop="postalCode").text.strip()

        # a_national_site.state_name = state_name
        # NaitonalSite_lst.append(a_national_site)

        try: 
            name = elem.text.strip()
            park_href = elem.find("a")["href"]
            park_url = base_url + park_href

            # try:
            #     park_description = elem.find("p").text  
            # except:
            #     pass  
            
            ## go to specific park's url to find park type and address
            park_CACHE = make_request_using_cache(park_url)  
            park_soup = BeautifulSoup(park_CACHE, "html.parser")
            park_type = park_soup.find(class_ = "Hero-designation").text   ## find park type

            a_national_site = NationalSite(park_type, name, park_url)
            # park_description,

            address = park_soup.find(class_= "adr")  ## find park address
            a_national_site.address_street = address.find(class_="street-address").text.strip()
            a_national_site.address_city = address.find(itemprop="addressLocality").text.strip()
            a_national_site.address_state = address.find(itemprop="addressRegion").text.strip()
            a_national_site.address_zip = address.find(itemprop="postalCode").text.strip()

            a_national_site.state_name = state_name
            NaitonalSite_lst.append(a_national_site)
        except:
            pass

    return(NaitonalSite_lst)


def get_state_name(state_abbr):
    global base_url

    state_CACHE = make_request_using_cache(base_url)
    #scrape nps.gov site to find a particular state 
    state_soup = BeautifulSoup(state_CACHE, "html.parser")
    content_div = state_soup.find(class_ = "dropdown-menu SearchBar-keywordSearch")
    state_li = content_div.find_all("li")
    
    count = False
    # while count == False:    ---> this is something i can do later

    href_string = ""
    potential_href = "/state/" + state_abbr + "/index.htm"

    #confirm this is a legit url/the state abbreviation was entered correctly
    for elem in state_li:
        if elem.find("a")["href"] == potential_href:
            href_string = potential_href
            state_name = elem.text  

    if href_string != "":
        return state_name

######################################################
############# Get Places Nearby a Site  ##############
######################################################

## Must return the list of NearbyPlaces for the specifite NationalSite
## param: a NationalSite object
## returns: a list of NearbyPlaces within 10km of the given site
##  if the site is not found by a Google Places search, this should return an empty list

### for site in Nationalcite_list:
        #put cite into google places API and return list

def get_nearby_places_for_site(a_national_site): ##is going to be an object
    googleAPIkey = secrets.google_places_key

##get the gps info
    google_LocationURL = "https://maps.googleapis.com/maps/api/place/textsearch/json?query={}&tyepe={}&key={}".format(a_national_site.name, a_national_site.type, googleAPIkey)

    location_results = make_request_using_cache(unique_url = google_LocationURL)
    loaded_location_results = json.loads(location_results)
    results_lst = []

    try:
        site_latit = loaded_location_results["results"][0]["geometry"]["location"]["lat"]
        site_longit = loaded_location_results["results"][0]["geometry"]["location"]["lng"]


### get nearby places
        google_NearbyPlacesURL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={}, {}&radius=10000&key={}".format(site_latit, site_longit, googleAPIkey)
        nearby_results = make_request_using_cache(google_NearbyPlacesURL)
        loaded_nearby_results = json.loads(nearby_results)
     
        for resulting_nearby_place in loaded_nearby_results["results"]:
           # try:  ## ---> can get rid of this
            place_name = resulting_nearby_place["name"]
            nearby_place = NearbyPlace(place_name)
            nearby_place.lat = resulting_nearby_place["geometry"]["location"]["lat"]
            nearby_place.lng = resulting_nearby_place["geometry"]["location"]["lng"]
            results_lst.append(nearby_place)
    except:
        pass    
    return results_lst




######################################################
############## Plot Sites for a State ################
######################################################


## Must plot all of the NationalSites listed for the state on nps.gov
## Note that some NationalSites might actually be located outside the state.
## If any NationalSites are not found by the Google Places API they should
##  be ignored.
## param: the 2-letter state abbreviation
## 
def plot_sites_for_state(state_abbr):  # get list of NationalSite instances in the state. returns: nothing. side effects: launches a plotly page in the web browser
    googleAPIkey = secrets.google_places_key

    state_park_lst = get_sites_for_state(state_abbr)

    lat_vals = []
    lon_vals = []
    text_vals = []


    for park in state_park_lst:
        google_LocationURL = "https://maps.googleapis.com/maps/api/place/textsearch/json?query={}&tyepe={}&key={}".format(park.name, park.type, googleAPIkey)

        location_results = make_request_using_cache(google_LocationURL)
        loaded_location_results = json.loads(location_results)

        try:  #check the lat and long available on google API
            park_lat = loaded_location_results["results"][0]["geometry"]["location"]["lat"]
            park_long = loaded_location_results["results"][0]["geometry"]["location"]["lng"]
            lat_vals.append(park_lat)
            lon_vals.append(park_long)
            text_vals.append(state_park_lst.name)
        except:
            pass
            ## could add something better to say here

    trace1 = dict(
        type = 'scattergeo',
        locationmode = 'USA-states',
        lon = lon_vals,
        lat = lat_vals,
        text = text_vals,
        mode = 'markers',
        marker = dict(
            size = 20,
            symbol = 'star',
            color = 'green'
        ))

    data = [trace1]

    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    for str_v in lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in lon_vals:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon))
    padding = max_range * .10
    lat_axis = [min_lat - padding, max_lat + padding]
    lon_axis = [min_lon - padding, max_lon + padding]

    layout = dict(
        geo = dict(
            scope='usa',
            projection=dict( type='albers usa' ),
            showland = True,
            landcolor = "rgb(250, 250, 250)",
            subunitcolor = "rgb(100, 217, 217)",
            countrycolor = "rgb(217, 100, 217)",
            lataxis = {'range': lat_axis},
            lonaxis = {'range': lon_axis},
            center = {'lat': center_lat, 'lon': center_lon },
            countrywidth = 3,
            subunitwidth = 3
        ),
    )

    fig = dict(data=data, layout=layout)
    py.plot(fig, validate=False, filename='national park sites')




######################################################
##############   Plot Nearby Places   ################
######################################################

## Must plot up to 20 of the NearbyPlaces found using the Google Places API
## param: the NationalSite around which to search
## returns: nothing
## side effects: launches a plotly page in the web browser
def plot_nearby_for_site(site_object):

    googleAPIkey = secrets.google_places_key

    google_NearbyPlacesURL = "https://maps.googleapis.com/maps/api/place/textsearch/json?query={}&tyepe={}&key={}".format(site_object.name, site_object.type, googleAPIkey)

    resulting_nearby_place = make_request_using_cache(google_NearbyPlacesURL)
    loaded_nearby_results = json.loads(resulting_nearby_place)

    park_lat_vals = []
    park_lng_vals = []
    park_text_vals = []

    try: 
        park_lat_vals.append(loaded_nearby_results["results"][0]["geometry"]["location"]["lat"])
        park_lng_vals.append(loaded_nearby_results["results"][0]["geometry"]["location"]["lng"])
        park_text_vals.append(site_object.name)

        nearby_places = get_nearby_places_for_site(site_object)
        
        place_lat_vals = []
        place_lng_vals = []
        place_text_vals = []

        for place in nearby_places:
            place_lat_vals.append(place.lat)
            place_lng_vals.append(place.lng)
            place_text_vals.append(place.name)


        National_Site = dict(
                type = 'scattergeo',
                locationmode = 'USA-states',
                lon = park_lng_vals,
                lat = park_lat_vals,
                text = park_text_vals,
                mode = 'markers',
                marker = dict(
                    size = 20,
                    symbol = 'star',
                    color = 'green'
                ))

        Nearby_Places = dict(
                type = 'scattergeo',
                locationmode = 'USA-states',
                lon = place_lng_vals,
                lat = place_lat_vals,
                text = place_text_vals,
                mode = 'markers',
                marker = dict(
                    size = 8,
                    symbol = 'circle',
                    color = 'blue'
                ))

        data = [National_Site, Nearby_Places]

        min_lat = 10000
        max_lat = -10000
        min_lon = 10000
        max_lon = -10000

        for str_v in place_lat_vals:
            v = float(str_v)
            if v < min_lat:
                min_lat = v
            if v > max_lat:
                max_lat = v
        for str_v in place_lng_vals:
            v = float(str_v)
            if v < min_lon:
                min_lon = v
            if v > max_lon:
                max_lon = v

        center_lat = (max_lat+min_lat) / 2
        center_lon = (max_lon+min_lon) / 2

        max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon))
        padding = max_range * .10
        lat_axis = [min_lat - padding, max_lat + padding]
        lon_axis = [min_lon - padding, max_lon + padding]

        layout = dict(
                geo = dict(
                    scope='usa',
                    projection=dict( type='albers usa' ),
                    showland = True,
                    landcolor = "rgb(250, 250, 250)",
                    subunitcolor = "rgb(100, 217, 217)",
                    countrycolor = "rgb(217, 100, 217)",
                    lataxis = {'range': lat_axis},
                    lonaxis = {'range': lon_axis},
                    center = {'lat': center_lat, 'lon': center_lon },
                    countrywidth = 3,
                    subunitwidth = 3
                ),
            )

        fig = dict(data=data, layout=layout)
        py.plot(fig, validate=False, filename='national sites and nearby places')

    except:
        pass
            ## could add something better to say here


######################################################
############   Implement Interactivity  ##############
######################################################

def prompt():
    user_input = input("\nEnter command (or 'help' for options) ")
    return user_input.lower()

def help_command():
    print(       ''' 
        list <stateabbr>
           available anytime
           lists all National Sites in a state
           valid inputs: a two-letter state abbreviation
        nearby <result_number>
           available only if there is an active result set
           lists all Places nearby a given result
           valid inputs: an integer 1-len(result_set_size)
        map <result number> 
           available only if there is an active result set
           displays the current results on a map
        exit
           exits the program
        help
           lists available commands (these instructions)

           ''')

def list_command(state_abbr): ## if user types list, will list all national site in the state
    state_name = get_state_name(state_abbr)
    print("National Sites in: " + state_name + "\n")
    state_site_list = get_sites_for_state(state_abbr)
    num = 1
    for state_site in state_site_list:
        number = str(num)
        state_site = str(state_site)
        print(number + " " + state_site)
        num += 1
    print("\n\n")
    return(state_site_list)


def nearby_command(state_site): 
    nearby_places_lst = get_nearby_places_for_site(state_site)
    if nearby_places_lst == []:
        print("No places listed near {}! Try another site.\n".format(state_site.name))
    else:
        print("Places near {}:\n".format(state_site.name))
        num = 1
        for nearby_place in nearby_places_lst:
            print(num, nearby_place)
            num += 1
        print("\n\n")
        return nearby_places_lst


def map_command(state_site):
    nearby_places_lst = get_nearby_places_for_site(state_site)
    if nearby_places_lst == []:
        print("Unable to generate a map for {}! Try another site.\n".format(state_site.name))
    else:
        plot_nearby_for_site(state_site)



#########################################
######## Execute the Program ############
#########################################


if __name__ == "__main__":
    
    user_input = prompt()
    site_list = []

    while user_input != "exit":
        if "help" in user_input:
            help_command()

        elif "list" in user_input:
            if len(user_input) > 5:
                try:
                    state_abbr = user_input[5:7]
                    site_list = list_command(state_abbr)
                except:
                    print("Invalid state abbreviation!\n")
            else:
                print("Please include a valid two-letter state abbreviation!\n")

        elif len(site_list) > 1:
            if "nearby" in user_input:
                user_integer_string = user_input[7:]
                user_integer = int(user_integer_string) - 1            
                try:
                    # nearby_command(search_site[user_integer])
                    nearby_command(site_list[user_integer])

                except:
                    print("Invalid! Please enter a number between 1 and the length of the National Site result set.")
            else:
                if "map" in user_input:
                    user_integer_string = user_input[4:]
                    user_integer = int(user_integer_string) - 1
                    try:
                        map_command(site_list[user_integer])
                    except:
                        print("Invalid command! Please choose a result number to select a site.")


        else:
            print("Please try the 'list' command first like: list <two-letter state abbreviation>\n")

        user_input = prompt()


