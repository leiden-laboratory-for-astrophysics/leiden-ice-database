var container = '#spectrum';
var margin = {top: 42, right: 10, bottom: 60, left: 60},
width = $(container).width() - margin.left - margin.right,
height = $(container).width() / 2 - margin.top - margin.bottom;
var hoverLineGroup, hoverLine, hoverHint;

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

var svg_width = width + margin.left + margin.right;
var svg_height = height + margin.top + margin.bottom;
var svg = d3.select(container)
  .append('svg')
  .attr('width', svg_width)
  .attr('height', svg_height)
  .append('g')
  .attr('transform',
  'translate(' + margin.left + ',' + margin.top + ')');

$(window).on('resize', function() {
  // TODO: Redraw spectrum?
  console.log('Redraw spectrum SVG');
});

var loader = $('#spectrum .loader')
  .css('left', width / 2 + 20 + 'px')
  .css('top', height /2 + 'px');

// Based on the temperature returns blue-red heat color
function temperatureRGB(minimum, maximum, value) {
  var x = (value - minimum) / (maximum - minimum);
  return d3.rgb(255 * x, 0, 255 * (1 - x));
}

var analogueID = $('#spectrum').attr('data-analogue-id');
var analogueAnnotations;

// Fetch all spectrum IDs belonging to analogue
d3.json('/analogue/' + analogueID + '.json', function(error, json) {
  if (error) return console.warn(error);

  analogueAnnotations = json.annotations;

  // Ask all spectra JSON using queue.js
  // https://github.com/mbostock/queue
  q = queue();
  $.each(json.spectra, function(index, value) {
    q = q.defer(d3.json, '/spectrum/' + value + '.json');
  });
  q.awaitAll(makeFigure);
});

function makeFigure(error, results) {
  if (error) return console.warn(error);

  // Set up white hover plane
  var hoverPlane = svg.append('rect')
    .attr('class', 'hover-plane')
    .attr('width', width)
    .attr('height', height)

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

  // Add extra margin in case peaks need to be annotated
  var yTopMargin = ($.isEmptyObject(analogueAnnotations) ? 0 : 0.03);
  y.domain([
    d3.min(yExtents, function(e) { return e[0]; }) + 0,
    d3.max(yExtents, function(e) { return e[1]; }) + yTopMargin
  ]).nice();

  var maxTemperature = d3.max(results, function(result) { return result.temperature });
  $.each(results, function(index, result) {
    svg.append('path')
      .attr('class', 'spectrum')
      .attr('id', 'spectrum' + index)
      .attr('d', valueline(result.data))
      .attr('stroke', temperatureRGB(0, maxTemperature, result.temperature))
      .attr('data-legend', result.temperature + ' K')
      .attr('data-index', index)
      .attr('data-legend-pos', result.temperature);
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

  // Draw Hover tools
  hoverLineGroup = svg.append('g').attr('class', 'hover-line');

  // Add the line to the group
  hoverLine = hoverLineGroup
    .append('line')
    .attr('x1', 10).attr('x2', 10)     // vertical line so same value on each
    .attr('y1', 0).attr('y2', height); // top to bottom

  // Hide it by default
  hoverLineGroup.classed('hide', true);
  svg.on('mousemove',  mousemove);
  svg.on('mouseleave', mouseleave);

  hoverHint = hoverLineGroup.append('text').attr('class', 'hover-hint');

  // Add annotations (loop through annotations Object)
  for (var property in analogueAnnotations) {
    if (analogueAnnotations.hasOwnProperty(property)) {
      var labelX = x(analogueAnnotations[property]);
      // Find highest peak at that position
      var paths = $(container).find('path.spectrum');

      // Minimum Y value because axis is reversed
      var peakY = d3.min(paths, function(spectrum) {
        var lastDelta = Infinity;
        for (var i = 0; i < spectrum.getTotalLength(); i+=4) {
          var delta = Math.abs(spectrum.getPointAtLength(i).x - labelX);
          if (delta > lastDelta) {
            // Found X point on path, now find Y peak around this point
            return d3.min(d3.range(-140, 140), function(offset) {
              return spectrum.getPointAtLength(i + offset).y;
            });
          }
          lastDelta = delta;
        }
        return console.log('Unable to find peak for label');
      });

      // Append annotation
      svg.append('text')
        .attr('class', 'annotation')
        .attr('text-anchor', 'middle')
        .attr('y', peakY - 14)
        .attr('x', labelX)
        .text(property);
    }
  }

  // Draw legend
  legend = svg.append('g')
    .attr('class', 'legend')
    .attr('transform', 'translate('+(width-80)+',40)')
    .style('font-size', '14px')
    .call(d3.legend);

  // Finish drawing figure
  loader.hide();
}

function mousemove(d, i) {
  var mouseX = Math.round(d3.mouse(this)[0]);
  var mouseY = Math.round(d3.mouse(this)[1]);
  if (mouseX > 0 && mouseY > 0 && mouseY < height) {
    hoverLineGroup.classed('hide', false);
    hoverLine.attr('x1', mouseX).attr('x2', mouseX);
    hoverHint.attr('x', mouseX+20).attr('y', mouseY);
    var wavenumber = Math.round(x.invert(mouseX));
    var absorbance = Math.round(y.invert(mouseY) * 1000) / 1000;
    hoverHint.text('(' + wavenumber + ', ' + absorbance + ')');
  }
}
function mouseleave() {
  hoverLineGroup.classed('hide', true);
}
