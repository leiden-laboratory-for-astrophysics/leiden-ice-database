var margin = {top: 42, right: 40, bottom: 60, left: 60},
width = 880 - margin.left - margin.right,
height = 620 - margin.top - margin.bottom;

var x = d3.scale.linear().range([width, 0]);
var y = d3.scale.linear().range([height, 0]);

var tickSize = -6;
var xAxisBottom = d3.svg.axis().scale(x).orient('bottom')
  .tickFormat(d3.format('g'))
  .tickSize(tickSize, 0);

var xAxisTop = d3.svg.axis().scale(x).orient('top')
  .tickValues([3, 4, 5, 6, 8, 10, 15].map(function(x) { return 10000/x; }))
  .tickFormat(function(d, i) { return 10000/d; })
  .tickSize(tickSize, 0);

var yAxisLeft = d3.svg.axis().scale(y)
  .orient('left')
  .tickSize(tickSize, 0);
var yAxisRight = d3.svg.axis().scale(y)
  .orient('right').tickFormat('')
  .tickSize(tickSize, 0);

function adjustYTextLabels(selection) {
  selection.selectAll('.tick text').attr('transform', 'translate(-2, 0)');
}
function adjustX0TextLabels(selection) {
  selection.selectAll('.tick text').attr('transform', 'translate(0, 4)');
}
function adjustX1TextLabels(selection) {
  selection.selectAll('.tick text').attr('transform', 'translate(0, -2)');
}

var valueline = d3.svg.line()
  .x(function(d) { return x(Math.round(d[0])); })
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
function temperatureRGB(minimum, maximum, value) {
  var x = (value - minimum) / (maximum - minimum);
  return d3.rgb(255 * x, 0, 255 * (1 - x));
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

  // Set X and Y Axis domain
  var xExtents = results.map(function(r) {
    return d3.extent(r.data, function(d) { return d[0]; });
  });
  var yExtents = results.map(function(r) {
    return d3.extent(r.data, function(d) { return d[1]; });
  });

  x.domain([
    d3.min(xExtents, function(e) { return e[0]; }),
    d3.max(xExtents, function(e) { return e[1]; })
  ]);
  y.domain([
    d3.min(yExtents, function(e) { return e[0]; }),
    d3.max(yExtents, function(e) { return e[1]; }) + 0.02
  ]);

  $.each(results, function(index, result) {
    svg.append('path')
      .attr('d', valueline(result.data))
      .attr('stroke', temperatureRGB(0, 135, result.temperature))
      .attr('data-legend', result.temperature + ' K');
  });

  // Add X Axes
  svg.append('g')
    .attr('class', 'x0 axis')
    .attr('transform', 'translate(0,' + height + ')')
    .call(xAxisBottom)
    .call(adjustX0TextLabels);

  svg.append('g')
    .attr('class', 'x1 axis')
    .call(xAxisTop)
    .call(adjustX1TextLabels);

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
    .attr('x', width/2 + 72)
    .attr('y', x0LabelY)
    .attr('dy', -2) // dy shifts relative Y position to simulate superscript
    .text('-1')
  svg.append('text')
    .attr('class', 'x0 label part3')
    .attr('text-anchor', 'middle')
    .attr('x', width/2 + 80)
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
    .call(yAxisLeft)
    .call(adjustYTextLabels);
  svg.append('g')
    .attr('class', 'y0 axis')
    .attr('transform', 'translate(' + width + ',0)')
    .call(yAxisRight);
  
  // Add Y Axis label
  svg.append('text')
    .attr('class', 'y label')
    .attr('transform', 'rotate(-90)')
    .attr('text-anchor', 'middle')
    .attr('y', 14 - margin.left)
    .attr('x', 0 - height / 2)
    .text('Absorbance');
  
  legend = svg.append('g')
    .attr('class', 'legend')
    .attr('transform', 'translate('+(width-110)+',60)')
    .style('font-size', '14px')
    .call(d3.legend)

  loader.hide();
}
