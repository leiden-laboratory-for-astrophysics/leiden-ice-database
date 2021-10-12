var container = '#spectrum_nval';
var margin = {top: 42, right: 10, bottom: 60, left: 60},
width = $(container).width() - margin.left - margin.right,
height = $(container).width() / 2 - margin.top - margin.bottom;

var x = d3.scale.linear().range([width, 0]);
var y = d3.scale.linear().range([height, 0]);

var valueline = d3.svg.line()
  .x(function(d) { return x(Math.round(d[0])); })
  .y(function(d) { return y(d[1]); });

  
var svg_width = width + margin.left + margin.right;
var svg_height = height + margin.top + margin.bottom;


var svg = d3.select(container).append("svg")
    //.append("rect")
    .attr("width", svg_width)
    .attr("height", svg_height);


var loader = $('#spectrum_nval .loader')
  .css('left', width / 2 + 20 + 'px')
  .css('top', height /2 + 'px');



// Based on the temperature returns blue-red heat color
function temperatureRGB(minimum, maximum, value) {
  var x = (value - minimum) / (maximum - minimum);
  return d3.rgb(255 * x, 0, 255 * (1 - x));
}

var n_analogueID = $('#spectrum_nval').attr('data-n_analogue-id');

// Fetch all spectrum IDs belonging to analogue
d3.json('/n_analogue/' + n_analogueID + '.json', function(error, json) {
  if (error) return console.warn(error);

  // Ask all spectra JSON using queue.js
  // https://github.com/mbostock/queue
  q = queue();
  $.each(json.n_val, function(index, value) {
    q = q.defer(d3.json, '/spectrum_nval/' + value + '.json');
  });
  
  q.awaitAll(makeFigure);
});



function makeFigure(error, results) {
  if (error) return console.warn(error);
  
    // Set X and Y Axis domain
  var xExtents = results.map(function(r) {
    return d3.extent(r.data, function(d) { return d[0]; });
  });

  x.domain([
    d3.min(xExtents, function(e) { return e[0]; }),
    d3.max(xExtents, function(e) { return e[1]; })
  ]);

  var maxTemperature = d3.max(results, function(result) { return result.temperature });
  $.each(results, function(index, result) {
    svg.append('path')
      .attr('class', 'spectrum_nval')
      .attr('id', 'spectrum_nval' + index)
      .attr('d', valueline(result.data))
      .attr('stroke', temperatureRGB(0, maxTemperature, result.temperature));
  });
  

    // Finish drawing figure
  loader.hide();

}



