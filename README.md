Documentation about sportradar endpoints

base url:
``` 
stats.fn.sportradar.com
```


Fetch regions and categories availables for sport.
where id_sport are:
- 1: Fútbol
- 2: Baloncesto
- 3: Béisbol
- 4: Hockey sobre hielo
- 5: Tennis
```
/sportradar/en/Europe:Berlin/gismo/config_tree_mini/41/0/{id_sport}
```

json response:
```json
    {
        "queryUrl": "config_tree_mini/41/0/{id_sport}",
        "doc": [
            {
                "data": {
                    "name": sport_name,
                    "realcategories": [
                        {
                            "name": country_name,
                            "_id": country_id,
                            "cc": {
                                "continentid": continent_id,
                                "continent": continent_name,
                                ...
                            }
                        },
                        {
                            "name": country_name,
                            "_id": country_id
                        },
                        ...
                    ]
                },
                ...
            }
        ]
    }
```

Fech all leagues for country id:
```
/sportradar/en/Europe:Berlin/gismo/config_tree_mini/41/0/{id_sport}/{country_id}
```

json response:
```json
    {
        "queryUrl": "config_tree_mini/41/0/{id_sport}/{id_country}",
        "doc": [
            {
                "data": [
                    {
                        "name": sport_name,
                        "realcategories": [ 
                            "name": country_name,
                            "_id": country_id,
                            "tournaments": [
                                {
                                    "name": division_name,
                                    "_id": division_id,
                                    "seasonid": seasonid,
                                },
                                {
                                    "name": division_name,
                                    "_id": division_id,
                                    "seasonid": seasonid,
                                },
                                ...
                            ]
                        ],
                        ...
                    }
                ]
            } 
        ]
    }
```

Fetch all team by league id:
```
/sportradar/es/Europe:Berlin/gismo/stats_season_tables/{league_id}
``` 

json response:
```json
{
    "queryUrl": "stats_season_tables/{league_id}",
    "doc": [
        {
            "data": {
                "tables": [
                    {
                        "name": league_name,
                        "tablerows": [
                            {
                                "drawTotal": total_draw,
                                "drawHome": total_draw_home,
                                "drawAway": total_draw_away,
                                "pos": table_position,
                                "lossTotal":total_loss,
                                "lossHome": total_loss_home,
                                "lossAway": total_loss_away,
                                "winTotal": total_win,
                                "winHome": total_win_home,
                                "winAway": total_win_away,
                                "team": {
                                    "_id": team_id,
                                    "name": team_name,
                                },
                                ...
                            },
                            {
                                "drawTotal": total_draw,
                                "drawHome": total_draw_home,
                                "drawAway": total_draw_away,
                                "pos": table_position,
                                "lossTotal":total_loss,
                                "lossHome": total_loss_home,
                                "lossAway": total_loss_away,
                                "winTotal": total_win,
                                "winHome": total_win_home,
                                "winAway": total_win_away
                                "team": {
                                    "_id": team_id,
                                    "name": team_name,
                                },
                                ...
                            },
                            ...
                        ]
                    }
                ]
            }
        }
    ]
}
```

Fech season information
```
/sportradar/en/Europe:Berlin/gismo/stats_season_uniqueteamstats/{season_id}
```