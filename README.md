# Jellyfin Media Cleanser

Inspired from [shemanaev/jellyfin-plugin-media-cleaner](https://github.com/shemanaev/jellyfin-plugin-media-cleaner), Jellyfin Media Cleanser is a python script that tries to achive simillar functionality while using the Jellyfin API, but there are some limitation to what can be achived through API.

I have Tried to keep it as Simple as i can.

## Setup 

Recomended way to use the script is with docker. Example:
```
docker run -d \
--name=jellyfin-media-cleanser \
-e JELLYFIN_HOST=https://jellyfin.domain.com \
-e JELLYFIN_API_KEY=apikey \
-e JELLYFIN_USERNAME=username \
-e SCRIPT_LOOP_TIME=1800 \
-e MOVIE_IGNORE_FAVORITE=0 \
-e MOVIE_DELETE_PLAYED=0 \
-e MOVIE_DELETE_ADDED_AFTER_N_DAYS=15 \
-e MOVIE_DELETE_LAST_PLAYED_AFTER_N_DAYS=0 \
-e SERIES_IGNORE_FAVORITE_EPISODE=0 \
-e SERIES_DELETE_PLAYED_EPISODE=0 \
-e SERIES_DELETE_ADDED_EPISODE_AFTER_N_DAYS=15 \
-e SERIES_DELETE_EPISODE_LAST_PLAYED_AFTER_N_DAYS=0 \
-e SERIES_KEEP_LAST_EPISODE=1 \
--restart unless-stopped \
docker.io/tusx/jellyfin-media-cleanser:latest
```
Above example will delete any movies and series episode that were added more than 15 days ago. see Environment Variables for further configuration

## Environment variables

| Environment variable                            | Default     | Description                                                                                    |
|-------------------------------------------------|-------------|------------------------------------------------------------------------------------------------|
| `JELLYFIN_HOST`                                 | `None`      | `Reqired` Url of the jellyfin server, do not include trailing slash `/`. `http` or  `https` is required in the link. see Examples: `https://jellyfin.domain.com`,`http://192.160.0.44:8096` |
| `JELLYFIN_API_KEY`                              | `None`      | `Reqired` Generate the API Key from jellyfin server `Dashboard -> API Keys`                    |
| `JELLYFIN_USERNAME`                             | `None`      | `Reqired` Given username will be used for checking Media Status like `IsFavorite`, `LastPlayedDate` and `Played` |
| `SCRIPT_LOOP_TIME`                              | `1800`      | 1800 represent seconds (30 min). Script will run every 1800 (30 min). This is used in `time.sleep()`, Change this according to your needs |
| `MOVIE_IGNORE_FAVORITE`                         | `0`         | Two Values accepted `0` `1`, For `1` Script will ignore Movies that are marked Favorite by the user in `JELLYFIN_USERNAME`. `0` will Delete the Movie even if was marked Favorite by user |
| `MOVIE_DELETE_PLAYED`                           | `0`         | Two Values accepted `0` `1`, For `1` Script will Delete the Movie if it is marked as `Played`. `0` will Skip Checking this, Jellyfin sets `Played` when a media is completely watched. | 
| `MOVIE_DELETE_ADDED_AFTER_N_DAYS`               | `15`        | Value represent the number of days. Script Checks how many days ago the Movie was added to Jellyfin, if it has been more days compared to set Value it will be Deleted. To Disable this Behaviour set it to `0`. Jellyfin sets `DateCreated` when New Media is added, Default Date used is `Use file creation date` chnage it to `Use date scanned into the library` for better Deletion time. Change this at `Dashboard -> Libraries -> Display` |
| `MOVIE_DELETE_LAST_PLAYED_AFTER_N_DAYS`         | `0`         | Value represent the number of days. Script Checks when was the last time the Movie was Played the user, if it has been more days compared to set Value it will be Deleted. To Disable this Behaviour set it to `0`. Jellyfin sets/updates `LastPlayedDate` whenever the user requests Playback of the media. |
| `SERIES_IGNORE_FAVORITE_EPISODE`                | `0`         | Two Values accepted `0` `1`, For `1` Script will ignore Episode that are marked Favorite by the user in `JELLYFIN_USERNAME`. `0` will Delete the Episode even if was marked Favorite by user |
| `SERIES_DELETE_PLAYED_EPISODE`                  | `0`         | Two Values accepted `0` `1`, For `1` Script will Delete the Episode if it is marked as `Played`. `0` will Skip Checking this, Jellyfin sets `Played` when a media is completely watched. |
| `SERIES_DELETE_ADDED_EPISODE_AFTER_N_DAYS`      | `15`        | Value represent the number of days. Script Checks how many days ago the Episode was added to Jellyfin, if it has been more days compared to set Value it will be Deleted. To Disable this Behaviour set it to `0`. Jellyfin sets `DateCreated` when New Media is added, Default Date used is `Use file creation date` chnage it to `Use date scanned into the library` for better Deletion time. Change this at `Dashboard -> Libraries -> Display` |
| `SERIES_DELETE_EPISODE_LAST_PLAYED_AFTER_N_DAYS`| `0`         | Value represent the number of days. Script Checks when was the last time the Episode was Played the user, if it has been more days compared to set Value it will be Deleted. To Disable this Behaviour set it to `0`. Jellyfin sets/updates `LastPlayedDate` whenever the user requests Playback of the media. |
| `SERIES_KEEP_LAST_EPISODE`                      | `1`         | Two Values accepted `0` `1`, For `1` Script will not delete the last Episode of last Season of a Series. `0` will Skip Checking this, It is benificial if you are grabing your releases with sonarr or other arr's. |


## Note

`MOVIE_DELETE_PLAYED` `MOVIE_DELETE_ADDED_AFTER_N_DAYS` `MOVIE_DELETE_LAST_PLAYED_AFTER_N_DAYS` all set to `0` will skip all Movie type Media. This will result in No Movie Deletion.

`SERIES_DELETE_PLAYED_EPISODE` `SERIES_DELETE_ADDED_EPISODE_AFTER_N_DAYS` `SERIES_DELETE_EPISODE_LAST_PLAYED_AFTER_N_DAYS` all set to `0` will skip all Series type Media. This will result in No Episode Deletion

Currently Script is Limited to `Movie` and `Series` Type Media in Jellyfin.

All the Metric used to determin deletion of any media is gathered for set user in `JELLYFIN_USERNAME`, if you want to take another users into considoration and want to delete according to there usecase then maybe run another instance with diffrent username in `JELLYFIN_USERNAME` 

Any and All Contributions are welcome and appreciated. Keep it simple

Make an issue if something is not right or want to discuss something related to Script



