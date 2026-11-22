// Tienda María: se guarda la app para abrirla rápido y sin internet. Versión: b83f2c6e41
var V="tm-b83f2c6e41";
var SHELL=["/","/manifest.webmanifest","/icon-192.png","/icon-512.png","/favicon-32.png"];
self.addEventListener("install",function(e){e.waitUntil(caches.open(V).then(function(c){return c.addAll(SHELL)}))});
self.addEventListener("message",function(e){if(e.data==="SKIP_WAITING")self.skipWaiting()});
self.addEventListener("activate",function(e){e.waitUntil(caches.keys().then(function(ks){return Promise.all(ks.filter(function(k){return k!==V}).map(function(k){return caches.delete(k)}))}).then(function(){return self.clients.claim()}))});
self.addEventListener("fetch",function(e){var r=e.request;if(r.method!=="GET")return;var u=new URL(r.url);
 if(u.origin!==location.origin||u.pathname.indexOf("/api/")===0||/\.apk$/.test(u.pathname)||u.pathname==="/sw.js")return;
 if(r.mode==="navigate"){
  var route=u.pathname;
  e.respondWith(fetch(r).then(function(res){
   if(!res.ok)return res;
   var cp=res.clone();
   return caches.open(V).then(function(c){return c.put(route,cp)}).catch(function(){}).then(function(){return res});
  }).catch(function(){return caches.match(route).then(function(cached){return cached||Response.error()})}));
  return;
 }
 e.respondWith(caches.match(r).then(function(m){return m||fetch(r).then(function(res){if(res.ok){var cp=res.clone();caches.open(V).then(function(c){c.put(r,cp)})}return res})}))});
