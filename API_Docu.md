

# Tele-Schocken API Dokumentationen

## Summery
	* GET	/api/game/<gid> 	    			Return the State of the Game (Polling)
	* POST	/api/game							Add a new Game.
	* POST	/api/game/<gid>/user/				Add a new User to a Game.
	* GET	/api/game/<gid>/user/<uid>/dice 	Roll a given number of dice     	
	*  POST /api/game/<gid>/chips			move chips from user to user or
	 										stack to user
	*



    


## GET	/api/game/<gid>
    HTTP/1.1 200 OK
    Content-Type: text/json
    
    
Move an Game ?? move : Hans bzw ID???
       
```json
"Stack" : 10,
"State" : "String",
"First_Halfe" : true,
"Move" : "Userid",
"First" : "Userid",
"Users": [{
	"id" : 11,
	"Name"  : "Hans",
	"Chips" : 2,
	"passive" : false,
	"visible" : false
	},
	{
	"id" : 11,
	"Name"  : "Hans",
	"Chips" : 2,
	"passive" : false,
	"visible" : false
	}
]
```
### Error Response:



## POST	/api/game	
### given:
{'name': 'Tim123'}

### response:
    HTTP/1.1 200 OK
    Content-Type: text/json
```json
"Link" : "tele-schocken.de/abc123",
"UUID": "abc123"
```


##  POST	/api/game/<gid>/user/
{'name': 'Tim123'}

 

## POST	/api/game/<gid>/user/<uid>/dice
```json
"dice1" : true,
"dice2" : true,
"dice3" : false,
```


    HTTP/1.1 200 OK
    Content-Type: text/json
```json
"fallen" : true,
"dice1" : 2, (Optional)
"dice2" : 3, (Optional)
"dice3" : 6, (Optional)
```


## POST	/api/game/<gid>/user/<uid>/diceturn
```json
"count" : 1 (Allowed Values 1,2)

```

    HTTP/1.1 200 OK
    Content-Type: text/json
```json
"dice1" : 2, (Optional)
"dice2" : 3, (Optional)
"dice3" : 6, (Optional)
```


## POST	/api/game/<gid>/chips 

```json
"count" : 3,
"stack" : true, (Optional)
"source" : <userid>, (Optional)
"target" : <userid>


```

	HTTP/1.1 200 OK
   	Content-Type: text/json


# Tele-Schocken Routs

## Summery
	* GET	/game/<gid> 	    			View play game
	* GET	/game							View Create new Game



Photo by Tembela Bohle from Pexels
https://www.pexels.com/photo/two-persons-holding-drinking-glasses-filled-with-beer-1089930/

