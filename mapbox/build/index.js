var mobile = document.documentElement.clientWidth <= 700;
                                                                                                 
mapboxgl.accessToken = 'pk.eyJ1Ijoibm1hcmNoaTAiLCJhIjoiY2p6dTljeDhiMGRwcjNubnl2aXI0OThhYyJ9.4FdGkBJlOXMPRugyqiXrjg';
window.map = new mapboxgl.Map({
  container: "map", // container id
  style: "mapbox://styles/nmarchi0/ck0yada9s02hp1cqhizxmwmlc", 
  center: [6.525479, 3.348520], // starting position
  zoom: 1,
  maxZoom: 16.5,
  minZoom: 1,
  hash: true
});

var sidebar = document.getElementById('sidebar');

if (!mobile) {
  window.map.addControl(new mapboxgl.NavigationControl());
  sidebar.className += " pin-bottomleft";
} else {
  window.map.addControl(new mapboxgl.NavigationControl(), 'bottom-right');
}

// map.on('zoomend', function() {
//  var zoom = map.getZoom();
//  if(zoom <= 10) {
//    setSpeed(.9);
//  }
//});

function flyHandler(id, options) {
  var button = document.getElementById(id);
  if(!button) return;
  button.addEventListener('click', function() {
    map.flyTo({
      center: options.center,
      zoom: options.zoom || 10
    });
    if (options.speed) {
      setSpeed(options.speed);
    }
  });
}

flyHandler('sierra-leone', {
  center: [-13.250978, 8.480201],
  zoom: 10,
  speed: .2
});
flyHandler('nigeria', {
  center: [3.3528302631,6.4650446851],
  zoom: 10,
  speed: .2
});
flyHandler('liberia', {
  center: [-10.806036, 6.328368],
  zoom: 10,
  speed: .2
});
flyHandler('south-africa', {
  center: [18.6519186575,-34.0667541339],
  zoom: 10,
  speed: .2
});
flyHandler('kenya', {
  center: [36.7700362138,-1.318913533],
  zoom: 10,
  speed: .2
});
flyHandler('zimbabwe', {
  center: [31.12492652, -17.92837714],
  zoom: 10,
  speed: .2
});
flyHandler('tanzania', {
  center: [39.2139383738,-6.8511294828],
  zoom: 10,
  speed: .2
});
flyHandler('ghana', {
  center: [-0.2295671004,5.5419797951],
  zoom: 10,
  speed: .2
});
flyHandler('haiti', {
  center: [-72.336652, 18.538995],
  zoom: 10,
  speed: .2
});
flyHandler('brasil', {
  center: [-43.2558354349,-22.9931642826],
  zoom: 10,
  speed: .2
});
flyHandler('nepal', {
  center: [85.344876, 27.699009],
  zoom: 10,
  speed: .2
});
flyHandler('philippines', {
  center: [120.9526113007,14.6548062731],
  zoom: 10,
  speed: .2
});
flyHandler('india', {
  center: [72.84803101,19.0365929141],
  zoom: 10,
  speed: .2
});
flyHandler('pakistan', {
  center: [66.9894659945,24.9345039855],
  zoom: 10,
  speed: .2
});

var layers = ['Highly connected', 'Fully connected', 'Partially disconnected', 'Very disconnected', 'Severely disconnected'];
var colors = ['#0571b0', '#92c5de', '#f4a582', '#d6604d', '#ca0020'];

for (i = 0; i < layers.length; i++) {
  var layer = layers[i];
  var color = colors[i];
  var item = document.createElement('div');
  var key = document.createElement('span');
  key.className = 'legend-key';
  key.style.backgroundColor = color;

  var value = document.createElement('span');
  value.innerHTML = layer;
  item.appendChild(key);
  item.appendChild(value);
  legend.appendChild(item);
}
