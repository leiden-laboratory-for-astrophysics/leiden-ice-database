var margin = {top: 42, right: 40, bottom: 60, left: 60},
width = 680 - margin.left - margin.right,
height = 420 - margin.top - margin.bottom;

var x = d3.scale.linear().range([width, 0]);
var y = d3.scale.linear().range([height, 0]);

var xAxisBottom = d3.svg.axis().scale(x).orient('bottom')
  .tickFormat(d3.format('g'));

var xAxisTop = d3.svg.axis().scale(x).orient('top')
  .tickValues([3, 4, 5, 6, 8, 10, 15].map(function(x) { return 10000/x; }))
  .tickFormat(function(d, i) { return 10000/d; });

var yAxisLeft = d3.svg.axis().scale(y)
  .orient('left');
var yAxisRight = d3.svg.axis().scale(y)
  .orient('right').tickFormat('');

var valueline = d3.svg.line()
  .x(function(d) { return x(d[0]); })
  .y(function(d) { return y(d[1]); });

var svg = d3.select('#spectrum')
  .append('svg')
  .attr('width', width + margin.left + margin.right)
  .attr('height', height + margin.top + margin.bottom)
  .append('g')
  .attr('transform', 
  'translate(' + margin.left + ',' + margin.top + ')');

var loader = $('#spectrum .loader')
  .css('left', width / 2 + 20 + 'px')
  .css('top', height /2 + 'px');

// Based on the temperature returns blue-orange-red heat color
function heat_rgb(minimum, maximum, value) {
  var halfmax = (minimum + maximum) / 2;
  var b = Math.round(Math.max(0, 255 * (1 - value / halfmax)));
  var r = 255 - b;
  var x = Math.round(Math.max(0, 255 * (value/halfmax - 1)));
  var g = (255 - b - x)/2;
  return {r: r, g: g, b: b};
}

var spectra;
var mixtureID = $('#spectrum').attr('data-mixture-id');

// Fetch all spectrum IDs belonging to mixture
d3.json('/mixture/' + mixtureID + '.json', function(error, json) {
  if (error) return console.warn(error);

  // Ask all spectra JSON using queue.js
  // https://github.com/mbostock/queue
  q = queue()
  $.each(json.spectra, function(index, value) {
    q = q.defer(d3.json, '/spectrum/' + value + '.json');
  });
  q.awaitAll(makeFigure);
});

function makeFigure(error, results) {
  if (error) return console.warn(error);
  console.log(results);
  var data = results[0].data;

  // Set X and Y Axis domain
  x.domain(d3.extent(data, function(d) { return d[0]; }));
  y.domain([
    d3.min(data, function(d) { return d[1]; }),
    d3.max(data, function(d) { return d[1]; }) + 0.04
  ]);

  $.each(results, function(index, result) {
    var color = heat_rgb(0, 135, result.temperature);
    svg.append('path').attr('d', valueline(result.data))
      .attr('stroke', d3.rgb(color.r, color.g, color.b));
  });

  // Add X Axis
  svg.append('g')
    .attr('class', 'x0 axis')
    .attr('transform', 'translate(0,' + height + ')')
    .call(xAxisBottom);

  svg.append('g')
    .attr('class', 'x1 axis')
    .call(xAxisTop);

  // Add bottom X Axis label
  // SVG baseline-shift is not supported in many major browsers
  // like Firefox, IE and mobile Safari.
  x0LabelY = height + 46
  svg.append('text')
    .attr('class', 'x0 label part1')
    .attr('text-anchor', 'middle')
    .attr('x', width/2)
    .attr('y', x0LabelY)
    .text('Wavenumbers (cm')
  svg.append('text')
    .attr('class', 'x0 label part2')
    .attr('text-anchor', 'middle')
    .attr('x', width/2 + 54)
    .attr('y', x0LabelY)
    .attr('dy', -2) // dy shifts relative Y position to simulate superscript
    .text('-1')
  svg.append('text')
    .attr('class', 'x0 label part3')
    .attr('text-anchor', 'middle')
    .attr('x', width/2 + 60)
    .attr('y', x0LabelY)
    .text(')')

  // Add top X Axis label
  svg.append('text')
    .attr('class', 'x1 label')
    .attr('text-anchor', 'middle')
    .attr('x', width/2)
    .attr('y', 14 - margin.top)
    .text('Wavelength (μm)')

  // Add Y Axis
  svg.append('g')
    .attr('class', 'y0 axis')
    .call(yAxisLeft);
  svg.append('g')
    .attr('class', 'y0 axis')
    .attr('transform', 'translate(' + width + ',0)')
    .call(yAxisRight);
  
  // Add Y Axis label
  svg.append('text')
    .attr('class', 'y label')
    .attr('transform', 'rotate(-90)')
    .attr('text-anchor', 'middle')
    .attr('y', 18 - margin.left)
    .attr('x', 0 - height / 2)
    .text('Absorbance');

  loader.hide();
}
