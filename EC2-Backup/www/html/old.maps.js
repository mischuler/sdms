var mongodb = require('mongodb');
var http = require('http');
var PORT = 80;

function handleRequest(request, response)
{
	reponse.end('Success');
}


var server = http.createServer(handleRequest);
server.listen(PORT, function()
{
	console.log("Listening");
});

var MongoClient = mongodb.MongoClient;

var url = 'mongodb://localhost:27017/digitalBridge';

MongoClient.connect(url, function (err, db) 
{
	if (err) 
	{
		console.log('Unable to connect to Mongo server. Error:', err);
	} 
	else 
	{
		console.log('Connected to:', url);

		var collection = db.collection('Assets');
		
		collection.find({}).toArray(function (err, result) 
		{
			if (err)
			{
				console.log(err);
			}
			else if (result.length)
			{
				console.log(result);
			}
			else
			{
				console.log("No results found");
			}
		
			db.close();
		})
		
	}
})
