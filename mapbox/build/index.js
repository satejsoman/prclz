
// Mobile default width
var mobile = document.documentElement.clientWidth <= 700;
                       
// Link to Mapbox                                                                          
mapboxgl.accessToken = 'pk.eyJ1Ijoibm1hcmNoaTAiLCJhIjoiY2p6dTljeDhiMGRwcjNubnl2aXI0OThhYyJ9.4FdGkBJlOXMPRugyqiXrjg';
window.map = new mapboxgl.Map({
  container: "map", // container id
  style: "mapbox://styles/nmarchi0/ck0yada9s02hp1cqhizxmwmlc", 
  center: [17.54, 8.84], // starting position  -5.96, 16.89
  zoom: 2,
  maxZoom: 16.5,
  minZoom: 1,
  hash: true
});

// Sidebase mobile adjustment
var sidebar = document.getElementById('sidebar');
if (!mobile) {
  window.map.addControl(new mapboxgl.NavigationControl());
  sidebar.className += " pin-bottomleft";
} else {
  window.map.addControl(new mapboxgl.NavigationControl(), 'bottom-right');
}

// Fly to location buttons
function flyHandler(id, options) {
  var button = document.getElementById(id);
  if(!button) return;
  button.addEventListener('click', function() {
    map.flyTo({
      center: options.center,
      zoom: options.zoom || 10,
      bearing: options.bearing,
      pitch: options.pitch
    });
    if (options.speed) {
      setSpeed(options.speed);
    }
  });
}

flyHandler('sierra-leone', {
  center: [-13.250978, 8.480201],
  zoom: 12,
  bearing: 0,
  pitch: 0,
  speed: .2
});
flyHandler('nigeria', {
  center: [3.3528302631,6.4650446851],
  zoom: 12,
  bearing: 0,
  pitch: 0,
  speed: .2
});
flyHandler('liberia', {
  center: [-10.806036, 6.328368],
  zoom: 12,
  bearing: 0,
  pitch: 0,
  speed: .2
});
flyHandler('south-africa', {
  center: [18.6519186575,-34.0667541339],
  zoom: 12,
  bearing: 0,
  pitch: 0,
  speed: .2
});
flyHandler('kenya', {
  center: [36.7700362138,-1.318913533],
  zoom: 12,
  bearing: 0,
  pitch: 0,
  speed: .2
});
flyHandler('zimbabwe', {
  center: [31.12492652, -17.92837714],
  zoom: 12,
  bearing: 0,
  pitch: 0,
  speed: .2
});
flyHandler('tanzania', {
  center: [39.2139383738,-6.8511294828],
  zoom: 12,
  bearing: 0,
  pitch: 0,
  speed: .2
});
flyHandler('ghana', {
  center: [-0.2295671004,5.5419797951],
  zoom: 12,
  bearing: 0,
  pitch: 0,
  speed: .2
});
flyHandler('haiti', {
  center: [-72.336652, 18.538995],
  zoom: 12,
  bearing: 0,
  pitch: 0,
  speed: .2
});
flyHandler('brasil', {
  center: [-43.2558354349,-22.9931642826],
  zoom: 12,
  bearing: 0,
  pitch: 0,
  speed: .2
});
flyHandler('nepal', {
  center: [85.344876, 27.699009],
  zoom: 12,
  bearing: 0,
  pitch: 0,
  speed: .2
});
flyHandler('philippines', {
  center: [120.9526113007,14.6548062731],
  zoom: 12,
  bearing: 0,
  pitch: 0,
  speed: .2
});
flyHandler('india', {
  center: [72.84803101,19.0365929141],
  zoom: 12,
  bearing: 0,
  pitch: 0,
  speed: .2
});
flyHandler('pakistan', {
  center: [66.9894659945,24.9345039855],
  zoom: 12,
  bearing: 0,
  pitch: 0,
  speed: .2
});

// Legend
var layers = ['High access', 'Moderate access', 'Low access', 'Limited access', 'Very limited access'];
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

// Interactive popups
var title = document.getElementById('location-title');
var description = document.getElementById('location-description');
var buttontext = document.getElementById('location-button');

var locations = [
{"id": 1,
  "title": "Why street access matters",
  "description": "Having a street alongside a building is something often taken for granted. Yet for over a billion people in millions of neighborhoods accessing nearby street networks is a daily challenge. In fact, limited street access is often indicative of deficits in street-dependent infrastructure like fire hydrants, drains, power lines, or underground pipes that provide clean water or sanitation.",
  "buttontext":"Continue explainer (2/9)",
  "camera": {
    center: [-72.34257, 18.52656],
    bearing: 0,
    pitch:0,
    zoom: 13.75,
    speed: .6
  }
},{"id": 2,
  "title": "How the map can help",
  "description": "The Million Neighborhoods map is a first step towards identifying under-serviced neighborhoods at the global scale and democratizing resources that can facilitate community-driven urban planning efforts. Since the map relies on OpenStreetMap some neighborhoods are less well documented than others, but as data improves so can the map.",
  "buttontext":"Continue explainer (3/9)",
  "camera": {
    center: [-72.343405, 18.524463], 
    bearing: 0,
    pitch:60,
    zoom: 16.2,
    speed:.3
  }
},{"id": 3,
  "title": "Exploring Nairobi",
  "description": "To give a real life example of the kinds of neighborhoods covered in the map, let’s take a look at Nairobi, Kenya. Like many cities, Nairobi has wealthy and middle class neighborhoods alongside some of its poorest. To illustrate how differences in socioeconomic well-being relate to street access, let’s examine two areas of the city.",
  "buttontext":"Continue explainer (4/9)",
  "camera": {
    center: [36.82287, -1.28937],
    zoom: 12.61,
    pitch: 50,
    speed:.6,
    curve: 1.8
  }
}, {
  "id": 4,
  "title": "Nairobi Central",
  "description": "Here is a very typical street grid in downtown Nairobi. Notice how every building is adjacent to a city street and can easily access it? This is what we would call a ‘High access’ city block. This pattern is most common in highly planned urban areas which are more likely to receive a broad array of city services.",
  "buttontext":"Continue explainer (5/9)",
  "camera": {
    center: [36.825969, -1.284919],
    bearing: -8.9,
    zoom: 16.5,
    speed: .4
  }
}, {
  "id": 5,
  "title": "Kibera neighborhoods",
  "description": "Now let’s visit an area with extremely limited street access. This is Kibera, an informal settlement near the city center that is home to more than 170,000 people. For residents of Kibera the lack of street access means more limited economic opprtunities along with fewer sources of clean water and sanitation, and basic services like emergnency assistance and waste disposal.",
  "buttontext":"Continue explainer (6/9)",
  "camera": {
    center: [36.794268, -1.316134],
    bearing: 25.3,
    zoom: 16,
    speed: .4
  }
}, {
  "id": 6,
  "title": "Reblocking Kibera",
  "description": "Render notional reblock routes after gradual zoom in. Explain how new tools and data make it possible to propose reblocked networks that grant more complete access.",
  "buttontext":"Continue explainer (7/9)",
  "camera": {
    center: [36.794268, -1.316134],
    bearing: 25.3,
    zoom: 16.5,
    speed: .05
  }
}, {
  "id": 7,
  "title": "Reblocking Westpoint",
  "description": "Show that we can generate notional reblock routes in other neighborhoods (the approach is scalable).",
  "buttontext":"Continue explainer (8/9)",
  "camera": {
    center: [-10.80734, 6.32522], 
    bearing: 25.3,
    zoom: 16.5,
    speed: 1,
    curve: 1.2
  }
}, {
  "id": 8,
  "title": "About the project",
  "description": "Something about data, code, history, whos involved, whats next, how to get involved, contact info",
  "buttontext":"Continue explainer (9/9)",
  "camera": {
    center: [-11.182, 7.278],
    bearing: 0,
    pitch:25,
    zoom: 7,
    curve: 1.7,
    speed: .6
  } 
}, {
  "id": 9,
  "title": "What the map shows",
  "description": "This map answers the basic question: How hard is it to get from the buildings in a block to the streets around it? As show in the legend at the bottom right, red areas contain buildings with more limited street access and blue areas contain buildings with higher levels of access. The data that underlies the map comes from OpenStreetMap, an open source GIS database crowdsourced from around the world.",
  "buttontext":"Play interactive explainer",
  "camera": {
    center: [17.54, 8.84],
    bearing: 0,
    pitch:0,
    zoom: 2,
    speed: .5
  }
}];

function debounce(func, wait, immediate) {
  var timeout;
  return function executedFunction() {
    var context = this;
    var args = arguments; 
    var later = function() {
      timeout = null;
      if (!immediate) func.apply(context, args);
    };
    var callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(context, args);
  };
};

function playback(id, index) {
  var button = document.getElementById(id);
  if(!button) return;
  button.addEventListener('click', debounce(function() {
    title.textContent = locations[index].title;
    description.textContent = locations[index].description;
    buttontext.textContent = locations[index].buttontext;
    map.flyTo(locations[index].camera);
    index = ((index + 1) === locations.length) ? 0 : index + 1;}, 1000, 500)
  );
}

title.textContent = locations[locations.length -1].title;
description.textContent = locations[locations.length - 1].description;
buttontext.textContent = locations[locations.length - 1].buttontext;


playback('play-interactive',0)

