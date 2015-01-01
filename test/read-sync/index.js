'use strict';

var PORT   = 9000;
var http   = require('http');
var fs     = require('fs');
var server = http.createServer();

console.error('pid:', process.pid);

server
  .on('request', onRequest)
  .on('listening', onListening)
  .listen(PORT);

function readMe() {
  return fs.readFileSync(__filename, 'utf8');
}

function onRequest(req, res) {
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  var text = readMe();
  res.end(text + '\r\n');
}

function onListening() {
  console.error('HTTP server listening on port', PORT);
  console.error('curl localhost:%d', PORT);
}
