import { CognitoUserPool } from "amazon-cognito-identity-js";
import config from "../config";

export async function authUser() {
  const currentUser = getCurrentUser();

  if (currentUser === null) {
    return false;
  }

  await getUserToken(currentUser);

  return true;
}

function getUserToken(currentUser) {
  return new Promise((resolve, reject) => {
    currentUser.getSession(function(err, session) {
      if (err) {
        reject(err);
        return;
      }
      resolve(session.getIdToken().getJwtToken());
    });
  });
}

function getCurrentUser() {
  const userPool = new CognitoUserPool({
    UserPoolId: config.cognito.USER_POOL_ID,
    ClientId: config.cognito.APP_CLIENT_ID
  });
  return userPool.getCurrentUser();
}

export async function searchAssets(queryString) {
    
  var AWS = require('aws-sdk');
  var lambda = new AWS.Lambda({
    accessKeyId: config.credentials.accessKeyId,
    secretAccessKey: config.credentials.secretAccessKey,
    region: config.credentials.region
  });
  var params = {
      FunctionName: "searchAssets",
      InvocationType: "RequestResponse",
      Payload: JSON.stringify(queryString)
  };
  
  console.log("Begin invokation with the following parameters...")
  console.log(params)
  
  return lambda.invoke(params).promise();
}
  
  
  


export default async function s3Upload(file, metadata) {

  var AWS = require('aws-sdk');
  
  var lastIndex = file.name.lastIndexOf(".");
  var fileName = file.name.slice(0, lastIndex).replace(/\s/g, "");
  var fileExt = file.name.slice(lastIndex, file.name.length)
  const uuidv4 = require('uuid/v4');
  var uniqueID = uuidv4();
  var uniqueName = fileName + "_" + uniqueID;
  var workID = uniqueID + "_" + fileName;
  var fullName = uniqueName + fileExt;
  var key = uniqueName + "/" + fullName;
  
 
  const s3 = new AWS.S3({
    params: {
      Bucket: config.s3.BUCKET,
    },
    accessKeyId: config.credentials.accessKeyId,
    secretAccessKey: config.credentials.secretAccessKey,
    region: config.credentials.region
  });
  
  console.log(config.credentials.accessKeyId);
  console.log(config.credentials.secretAccessKey);
  console.log(config.credentials.region);
  
  {/* Pull the audit related metadata */}
  metadata['Account'] = 'account1';
  metadata['audit_User'] = 'user1'
  metadata['audit_IP_address'] = 'TBD'
  metadata['audit_Timestamp'] = new Date().toISOString();
  metadata['audit_Action'] = 'File uploaded'
  metadata['audit_Notes'] = 'TBD'
  metadata['workID'] = workID;

  return s3
    .upload({
      Key: key,
      Body: file,
      ContentType: file.type,
      ServerSideEncryption: "AES256",
      Metadata: metadata
    })
    .promise();
}