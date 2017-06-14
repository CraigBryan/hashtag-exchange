/*
This script can use the following optional environment variables:
MONGO_HOST - the host address of the mongo server
             default: localhost
MONGO_PORT - the port of the mongo server
             default: from config file
*/

var yaml = require('js-yaml');
var fs = require('fs');
var MongoClient = require('mongodb').MongoClient;
var assert = require('assert');

var CONFIG_PATH = '/scripts/ensure-indices/config.yaml';

function runIndexing(config_path, indexingFunctions) {
  let mongoHost = null;
  let mongoPort = null;
  let mongoUser = null;
  let mongoPass = null;
  let dbName = null;
  let indexErrors = [];

  try {
    let config = yaml.safeLoad(fs.readFileSync(config_path, 'utf8'));
    mongoHost = process.env.MONGO_HOST || 'localhost';
    mongoPort = process.env.MONGO_PORT || 
                config['vms']['DIGITAL_OCEAN_MONGO_PORT'];
    mongoUser = config['users']['MONGO_DB_TWITTER_USER'];
    mongoPass = config['passwords']['MONGO_DB_TWITTER_PASSWORD'];
    dbName = config['db-constants']['HASHTAG_EXCHANGE_DB'];
  } catch (err) {
    console.log("Error reading configuration");
    console.log(err);
    process.exit(1);
  }

  let mongoUrl = `mongodb://${mongoUser}:${mongoPass}@` +
                 `${mongoHost}:${mongoPort}/${dbName}`;

  MongoClient.connect(mongoUrl, (err, conn) => {
    for (func in indexingFunctions) {
      err = func(conn);
      if (err != null) {
       indexErrors.push(err);
      }
    }
  });

  console.log(`Successfully connected to ${mongoUrl}`);
  return indexErrors;
};

// Ensures there are indices on the rawTwitterHashtags collection 
var ensureRawTwitterData = function(db) {
  console.log('Indexing the "rawTwitterHashtags" collection');

  console.log('Ensuring index on the "createdOn" field');
  db.ensureIndex(
    'rawTwitterHashtags',
    {'createdOn': 1},
    {'background': true},
    {'expireAfterSeconds': 31 * 24 * 60 * 60}, // 31 days
    function(err, indexName) {
      if (err != null) {
        return err;
      } else {
        console.log('"createdOn" index exists');
      }
    }
  );

  console.log('Finished indexing the "rawTwitterHashtags" collection');
  return null;
};

// Add more indexing functions here

let indexingFunction = [
  ensureRawTwitterData,
  // Add the indexing functions here
]
let indexErrors = runIndexing(CONFIG_PATH, indexingFunction);

if (indexErrors.length != 0) {
  console.log('Errors occurred during ensureIndex');
  console.log(indexErrors);
  process.exit(1);
};

console.log('Successfully ensured indices');
