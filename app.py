import os
import requests
import time
import datetime

# Configuration
JELLYFIN_HOST = os.getenv("JELLYFIN_HOST")  # Jellyfin server URL, Default -> Required
JELLYFIN_API_KEY = os.getenv("JELLYFIN_API_KEY") # Use your existing Jellyfin API key, Default -> Required
JELLYFIN_AUTH_HEADER_VALUE = f'MediaBrowser Client="Python App", Device="Docker-Python", DeviceId="a41eee17-6bdf-4b69-80b5-1b5434d2ca9f", Version="1.0.0", Token="{JELLYFIN_API_KEY}"' # Authentication Header
JELLYFIN_AUTH_HEADER = {"Authorization": JELLYFIN_AUTH_HEADER_VALUE} # Combined Authentication Header into dict fo use with requests
JELLYFIN_USERNAME = os.getenv("JELLYFIN_USERNAME") # Username of the jellyfin user, Default -> Required
SCRIPT_LOOP_TIME = int(os.getenv("SCRIPT_LOOP_TIME")) # Time to wait before running the loop Again, Default -> 900 which is 15 min
SCRIPT_MONITORED_TYPES = ["Movie","Series"] # Supported Types By Script
# Movies Monitoring Settings
MOVIE_IGNORE_FAVORITE =  int(os.getenv("MOVIE_IGNORE_FAVORITE"))
MOVIE_DELETE_PLAYED = int(os.getenv("MOVIE_DELETE_PLAYED"))
MOVIE_DELETE_ADDED_AFTER_N_DAYS = int(os.getenv("MOVIE_DELETE_ADDED_AFTER_N_DAYS"))
MOVIE_DELETE_LAST_PLAYED_AFTER_N_DAYS = int(os.getenv("MOVIE_DELETE_LAST_PLAYED_AFTER_N_DAYS"))
# Series Monitoring Settings
SERIES_IGNORE_FAVORITE_EPISODE = int(os.getenv("SERIES_IGNORE_FAVORITE_EPISODE"))
SERIES_DELETE_PLAYED_EPISODE = int(os.getenv("SERIES_DELETE_PLAYED_EPISODE"))
SERIES_DELETE_ADDED_EPISODE_AFTER_N_DAYS = int(os.getenv("SERIES_DELETE_ADDED_EPISODE_AFTER_N_DAYS"))
SERIES_DELETE_EPISODE_LAST_PLAYED_AFTER_N_DAYS = int(os.getenv("SERIES_DELETE_EPISODE_LAST_PLAYED_AFTER_N_DAYS"))
SERIES_KEEP_LAST_EPISODE = int(os.getenv("SERIES_KEEP_LAST_EPISODE"))

def print_msg(type_of_msg, msg):
    print(f"[{str(type_of_msg)}] -> {str(msg)} ")
# end def

def iso_to_unix(iso_string):
    # Trim the fractional seconds to 6 digits if they are longer
    iso_string = iso_string[:18] + "Z"
    # Parse the ISO 8601 string into a datetime object 2024-11-12T07:45:59.3287034Z
    dt = datetime.datetime.strptime(iso_string, "%Y-%m-%dT%H:%M:%SZ")
    # Convert datetime object to Unix timestamp
    return int(dt.timestamp())
# end def

def check_days_passed(iso_string, days):
    # Convert the input ISO 8601 datetime to Unix time
    event_unix_time = iso_to_unix(iso_string)
    # Get the current Unix time
    current_unix_time = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    # Calculate the difference in days
    seconds_in_a_day = 86400
    elapsed_days = (current_unix_time - event_unix_time) / seconds_in_a_day
    days_difference = int(elapsed_days)
    # Check if the elapsed days are greater than or equal to the specified days
    if days_difference >= days:
        return True, days_difference - days  # Over the limit
    else:
        return False, days - days_difference  # Days left to reach the limit
# end def

def delete_item(item_id):
    result = None

    endpoint = f"/Items/{str(item_id)}"
    url = JELLYFIN_HOST + endpoint
    print_msg("DELETE RQE", f"Calling -> {str(url)}")
    response = requests.delete(url, headers=JELLYFIN_AUTH_HEADER)
    print_msg("MSG", f"Response -> {str(response.status_code)}" )
    if response.status_code == 204:
        print_msg("SUCCESS", f"{str(item_id)}, Deleted Successfully" )
        result = True
    else:
        print_msg("ERROR", f"{str(item_id)}, There was an Issue in Deleting this Item. See Response CODE" )
        
    return result
# end def

def get_user_id():
    result = None

    url = f"{JELLYFIN_HOST}/Users"
    headers = JELLYFIN_AUTH_HEADER
    print_msg("MSG", f"Calling -> {str(url)} ")
    response = requests.get(url, headers=headers)
    print_msg("MSG", f"Response -> {str(response.status_code)}" )
    users = response.json()
    if response.status_code == 200:
        print_msg("MSG", f"Authentication Sucessfull at {JELLYFIN_HOST} ")
        # Find the user by username
        for user in users:
            if user.get("Name") == JELLYFIN_USERNAME:
                result = user.get("Id")
    else:
        print_msg("Error", f"Could not Authenticate with the API Key at {JELLYFIN_HOST} ")

    return result
# end def

def get_user_libraries(user_id):
    result = None

    endpoint = f"/Users/{str(user_id)}/Items/"
    url = f"{JELLYFIN_HOST}{endpoint}"
    headers = JELLYFIN_AUTH_HEADER
    print_msg("MSG", f"Calling -> {str(url)} ")
    response = requests.get(url, headers=headers)
    print_msg("MSG", f"Response -> {str(response.status_code)}" )
    server_response = response.json()

    if response.status_code == 200:
        result = server_response

    else:
        print_msg("Error", f"{str(endpoint)}, Could not Retrieve info from Server. CODE -> {str(response.status_code)} ")
        
    return result
# end def

def get_library_items(user_id, item_id):
    result = None
    
    endpoint = f"/Users/{str(user_id)}/Items?ParentId={str(item_id)}"
    url = f"{JELLYFIN_HOST}{endpoint}"
    headers = JELLYFIN_AUTH_HEADER
    print_msg("MSG", f"Calling -> {str(url)} ")
    response = requests.get(url, headers=headers)
    print_msg("MSG", f"Response -> {str(response.status_code)}" )
    server_response = response.json()

    if response.status_code == 200:
        result = server_response

    else:
        print_msg("Error", f"{str(endpoint)}, Could not Retrieve info from Server. CODE -> {str(response.status_code)} ")
        
    return result
# end def

def delete_movie(user_id,movie_id):
    result = None
    delete_movie = None
    print_msg("MSG", f"Getting Movie Info! -> {str(movie_id)}")

    if MOVIE_DELETE_ADDED_AFTER_N_DAYS == 0 and MOVIE_DELETE_PLAYED == 0 and MOVIE_DELETE_LAST_PLAYED_AFTER_N_DAYS == 0:
        print_msg("SKIP", f"Because MOVIE_DELETE_ADDED_AFTER_N_DAYS,MOVIE_DELETE_PLAYED,MOVIE_DELETE_LAST_PLAYED_AFTER_N_DAYS is set to 0")
        return result
    
    endpoint = f"/Users/{str(user_id)}/Items/{str(movie_id)}"
    url = f"{JELLYFIN_HOST}{endpoint}"
    headers = JELLYFIN_AUTH_HEADER
    print_msg("MSG", f"Calling -> {str(url)} ")
    response = requests.get(url, headers=headers)
    print_msg("MSG", f"Response -> {str(response.status_code)}" )
    item_detail = response.json()
    # print(item_detail)
    movie_name = item_detail['Name'] + " (" + str(item_detail['ProductionYear']) + ")"
    print_msg("MSG", f"Checking Monitoring/Deletion requirements")

    # Check if Need to ignore in case if its Favorite
    if MOVIE_IGNORE_FAVORITE > 0:
        print_msg("CHECK", f"{str(movie_name)}, Checking for MOVIE_IGNORE_FAVORITE - {str(MOVIE_IGNORE_FAVORITE)}")
        if item_detail['UserData']['IsFavorite'] is True:
            print_msg("SKIP", f"{str(movie_name)}, Skipped Because it is in Users Favorite")
            return result
        else: 
            print_msg("MSG", f"{str(movie_name)}, is not in Users Favorite. Proceeding as Normal")
    else:
        print_msg("SKIP", f"{str(movie_name)}, For MOVIE_IGNORE_FAVORITE is set to 0")

    # Check for MOVIE_DELETE_ADDED_AFTER_N_DAYS
    if MOVIE_DELETE_ADDED_AFTER_N_DAYS > 0:
        print_msg("CHECK", f"{str(movie_name)}, Checking for MOVIE_DELETE_ADDED_AFTER_N_DAYS - {str(MOVIE_DELETE_ADDED_AFTER_N_DAYS)} days")
        need_delete, days_left = check_days_passed(item_detail['DateCreated'],MOVIE_DELETE_ADDED_AFTER_N_DAYS)
        if need_delete is True:
            print_msg("DELETE", f"{str(movie_name)}, Movie Needs to be deleted")
            delete_movie = "yes"
        if need_delete is False:
            print_msg("SKIP", f"{str(movie_name)}, {str(days_left)} days Left to delete this")
    else:
        print_msg("SKIP", f"{str(movie_name)}, For MOVIE_DELETE_ADDED_AFTER_N_DAYS is set to 0")


    # Check for MOVIE_DELETE_ADDED_AFTER_N_DAYS
    if MOVIE_DELETE_PLAYED > 0:
        print_msg("CHECK", f"{str(movie_name)}, Checking for MOVIE_DELETE_PLAYED - {str(MOVIE_DELETE_PLAYED)}")
        if item_detail['UserData']['Played'] is True:
            print_msg("DELETE", f"{str(movie_name)}, Movie Needs to be deleted")
            delete_movie = "yes"
        else:
            print_msg("SKIP", f"{str(movie_name)}, Played Status -> {str(item_detail['UserData']['Played'])}")
    else:
        print_msg("SKIP", f"{str(movie_name)}, For MOVIE_DELETE_PLAYED is set to 0")

    # Check for MOVIE_DELETE_LAST_PLAYED_AFTER_N_DAYS
    if MOVIE_DELETE_LAST_PLAYED_AFTER_N_DAYS > 0:
        print_msg("CHECK", f"{str(movie_name)}, Checking for MOVIE_DELETE_LAST_PLAYED_AFTER_N_DAYS - {str(MOVIE_DELETE_LAST_PLAYED_AFTER_N_DAYS)} days")
        last_played_date = item_detail.get('UserData', {}).get('LastPlayedDate')
        if last_played_date:
            need_delete, days_left = check_days_passed(item_detail['UserData']['LastPlayedDate'],MOVIE_DELETE_LAST_PLAYED_AFTER_N_DAYS)
            if need_delete is True:
                print_msg("DELETE", f"{str(movie_name)}, Movie Needs to be deleted")
                delete_movie = "yes"
            if need_delete is False:
                print_msg("SKIP", f"{str(movie_name)}, {str(days_left)} days Left to delete this")
        else:
            print_msg("SKIP", f"{str(movie_name)}, LastPlayedDate not Found")
    else:
        print_msg("SKIP", f"{str(movie_name)}, For MOVIE_DELETE_LAST_PLAYED_AFTER_N_DAYS is set to 0")

    # Finally Delete the Item if delete_movie is set to yes
    if delete_movie == "yes":
        print_msg("DELETE", f"{str(movie_name)}, Trying to Delete from Jellyfin")
        delete_the_movie = delete_item(movie_id)
# end def

def delete_series_episodes(user_id,series_id):
    result = None

    print_msg("MSG", f"Getting Series Info! -> {str(series_id)}")

    if SERIES_DELETE_PLAYED_EPISODE == 0 and SERIES_DELETE_ADDED_EPISODE_AFTER_N_DAYS == 0 and SERIES_DELETE_EPISODE_LAST_PLAYED_AFTER_N_DAYS == 0:
        print_msg("SKIP", f"Because SERIES_DELETE_PLAYED_EPISODE,SERIES_DELETE_ADDED_EPISODE_AFTER_N_DAYS,SERIES_DELETE_EPISODE_LAST_PLAYED_AFTER_N_DAYS is set to 0")
        return result
    
    endpoint = f"/Shows/{str(series_id)}/Episodes?userId={str(user_id)}&fields=DateCreated"
    url = JELLYFIN_HOST + endpoint
    print_msg("MSG", f"Calling -> {str(url)} ")
    response = requests.get(url, headers=JELLYFIN_AUTH_HEADER)
    print_msg("MSG", f"Response -> {str(response.status_code)}" )
    series_detail = response.json()
    total_episodes = len(series_detail['Items'])
    # print(Series_detail)
    episode_number = 0
    for episode in series_detail['Items']:
        delete_episode = None
        episode_number = episode_number + 1
        episode_full_name = f"{str(episode['SeriesName'])} Season {str(episode['ParentIndexNumber'])} Episode {str(episode['IndexNumber'])}"
        print_msg("MSG", f"Checking - {str(episode_full_name)}")

        # Check if this is the last episode
        if SERIES_KEEP_LAST_EPISODE > 0 and episode_number == total_episodes:
            print_msg("SKIP", f"{str(episode_full_name)} is the last episode available in this Series. SERIES_KEEP_LAST_EPISODE is set to {str(SERIES_KEEP_LAST_EPISODE)} ")
            continue

        # Check if Need to ignore in case if its Favorite
        if SERIES_IGNORE_FAVORITE_EPISODE > 0:
            print_msg("CHECK", f"{str(episode_full_name)}, Checking for SERIES_IGNORE_FAVORITE_EPISODE - {str(SERIES_IGNORE_FAVORITE_EPISODE)}")
            if episode['UserData']['IsFavorite'] is True:
                print_msg("SKIP", f"{str(episode_full_name)}, Skipped Because it is in Users Favorite")
                continue
            else: 
                print_msg("MSG", f"{str(episode_full_name)}, is not in Users Favorite. Proceeding as Normal")
        else:
            print_msg("SKIP", f"{str(episode_full_name)}, For SERIES_IGNORE_FAVORITE_EPISODE is set to 0")

        # Check for SERIES_DELETE_ADDED_EPISODE_AFTER_N_DAYS
        if SERIES_DELETE_ADDED_EPISODE_AFTER_N_DAYS > 0:
            print_msg("CHECK", f"{str(episode_full_name)}, Checking for SERIES_DELETE_ADDED_EPISODE_AFTER_N_DAYS - {str(SERIES_DELETE_ADDED_EPISODE_AFTER_N_DAYS)} days")
            need_delete, days_left = check_days_passed(episode['DateCreated'],SERIES_DELETE_ADDED_EPISODE_AFTER_N_DAYS)
            if need_delete is True:
                print_msg("DELETE", f"{str(episode_full_name)}, Needs to be deleted")
                delete_episode = "yes"
            if need_delete is False:
                print_msg("SKIP", f"{str(episode_full_name)}, {str(days_left)} days Left to delete this")
        else:
            print_msg("SKIP", f"{str(episode_full_name)}, For SERIES_DELETE_ADDED_EPISODE_AFTER_N_DAYS is set to 0")

        # Check for SERIES_DELETE_PLAYED_EPISODE
        if SERIES_DELETE_PLAYED_EPISODE > 0:
            print_msg("CHECK", f"{str(episode_full_name)}, Checking for SERIES_DELETE_PLAYED_EPISODE - {str(SERIES_DELETE_PLAYED_EPISODE)}")
            if episode['UserData']['Played'] is True:
                print_msg("DELETE", f"{str(episode_full_name)}, Needs to be deleted")
                delete_episode = "yes"
            else:
                print_msg("SKIP", f"{str(episode_full_name)}, Played Status -> {str(episode['UserData']['Played'])}")
        else:
            print_msg("SKIP", f"{str(episode_full_name)}, For SERIES_DELETE_PLAYED_EPISODE is set to 0")

        # Check for SERIES_DELETE_EPISODE_LAST_PLAYED_AFTER_N_DAYS
        if SERIES_DELETE_EPISODE_LAST_PLAYED_AFTER_N_DAYS > 0:
            print_msg("CHECK", f"{str(episode_full_name)}, Checking for SERIES_DELETE_EPISODE_LAST_PLAYED_AFTER_N_DAYS - {str(SERIES_DELETE_EPISODE_LAST_PLAYED_AFTER_N_DAYS)} days")
            last_played_date = episode.get('UserData', {}).get('LastPlayedDate')
            if last_played_date:
                need_delete, days_left = check_days_passed(episode['UserData']['LastPlayedDate'],SERIES_DELETE_EPISODE_LAST_PLAYED_AFTER_N_DAYS)
                if need_delete is True:
                    print_msg("DELETE", f"{str(episode_full_name)}, Needs to be deleted")
                    delete_episode = "yes"
                if need_delete is False:
                    print_msg("SKIP", f"{str(episode_full_name)}, {str(days_left)} days Left to delete this")
            else:
                print_msg("SKIP", f"{str(episode_full_name)}, LastPlayedDate not Found")
        else:
            print_msg("SKIP", f"{str(episode_full_name)}, For SERIES_DELETE_EPISODE_LAST_PLAYED_AFTER_N_DAYS is set to 0")

        # Finally Delete the Item if delete_episode is set to yes
        if delete_episode == "yes":
            print_msg("DELETE", f"{str(episode_full_name)}, Trying to Delete from Jellyfin")
            delete_the_episode = delete_item(episode['Id'])
# end def

def main_func():
    print_msg("START", "Python Script Starting")

    user_id = get_user_id()
    if user_id is None:
        print_msg("Error", f"Could not Obtainer User Id for User -> {str(JELLYFIN_USERNAME)}")
        print_msg("END", f"Ending Script in {str(SCRIPT_LOOP_TIME)} sec ")
        exit()
    # end if

    user_libraries = get_user_libraries(user_id)
    # print(user_libraries)

    if user_libraries is None:
        print_msg("Error", f"Could not Obtainer Users Libraries for User -> {str(JELLYFIN_USERNAME)}")
        print_msg("END", f"Ending Script in {str(SCRIPT_LOOP_TIME)} sec ")
        exit()
    # end if

    print_msg("MSG", f"Found -> {str(len(user_libraries['Items']))} Libraries for User -> {str(JELLYFIN_USERNAME)} ")
    for user_library in user_libraries['Items']:

        print_msg("MSG", f"Looking in Library -> {str(user_library['Name'])} ")
        user_library_items = get_library_items(user_id,user_library["Id"])
        print_msg("MSG", f"Found -> {str(len(user_library_items['Items']))} Items in Library -> {str(user_library['Name'])} ")
        for library_item in user_library_items['Items']:
            print_msg("MSG", f"Found -> {str(library_item['Name'])} - {str(library_item['Type'])} ")
            if library_item['Type'] in SCRIPT_MONITORED_TYPES:
                print_msg("MSG", f"{str(library_item['Name'])} - {str(library_item['Type'])} is a SCRIPT_MONITORED_TYPES")
                if library_item['Type'] == "Movie":
                    delete_movie(user_id,library_item['Id'])

                if library_item['Type'] == "Series":
                    delete_series_episodes(user_id,library_item['Id'])
                    
                
            else:
                print_msg("SKIP", f"{str(library_item['Name'])} - {str(library_item['Type'])} is NOT a SCRIPT_MONITORED_TYPES")

            print("") # Add New Line After Each Item Is checked

# end def

if __name__ == "__main__":
    while True:
        main_func()
        print("====xxxx====")
        print_msg("SLEEP", f"Loop Done, Sleeping for {str(SCRIPT_LOOP_TIME)} sec ")
        print("====xxxx====")
        time.sleep(SCRIPT_LOOP_TIME) 
    # end while

# end if
