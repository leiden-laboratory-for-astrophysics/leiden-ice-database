var container = '#spectrum_nval';
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
  .tickValues([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.5, 2.0, 3, 4, 5, 6, 8, 10, 15].map(function(x) { return 10000/x; }))
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


/*
//var zoom = d3.behavior.zoom().on("zoom", refresh_ok).scaleExtent([1, 3]);

var zoom = d3.behavior.zoom().on("zoom", refresh_old);

var svg = d3.select(container).append("svg")
    //.append("rect")
    .attr("width", svg_width)
    .attr("height", svg_height)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
    .call(zoom);


var view = svg.append("rect")
  .attr("class", "zoom")
  .attr("width", width)
  .attr("height", height)
  .call(zoom)*/


/*
//WORKING -- PAN
var zoom = d3.behavior.zoom().on("zoom", refresh_ok).scaleExtent([1, 3]);

var svg = d3.select(container).append("svg")
    //.append("rect")
    .attr("width", svg_width)
    .attr("height", svg_height)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
    .call(zoom);*/


var zoom = d3.behavior.zoom().on("zoom", refresh);

var zoomRect = true;
		

d3.select("#zoom-rect").on("change", function() {
      zoomRect = this.unchecked;
    });

var svg = d3.select(container).append("svg")
    .attr("width", svg_width)
    .attr("height", svg_height)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
    .call(zoom)
    .append("g")
     .on("mousedown", function() {
       if (!zoomRect) return;
       var e = this,
           origin = d3.mouse(e),
           rect = svg.append("rect").attr("class", "zoom");
       d3.select(container).classed("noselect", true);
       origin[0] = Math.max(0, Math.min(width, origin[0]));
       origin[1] = Math.max(0, Math.min(height, origin[1]));
       d3.select(window)
           .on("mousemove.zoomRect", function() {
             var m = d3.mouse(e);
             m[0] = Math.max(0, Math.min(width, m[0]));
             m[1] = Math.max(0, Math.min(height, m[1]));
             rect.attr("x", Math.min(origin[0], m[0]))
                  .attr("y", Math.min(origin[1], m[1]))
                  .attr("width", Math.abs(m[0] - origin[0]))
                  .attr("height", Math.abs(m[1] - origin[1]));
            })
           .on("mouseup.zoomRect", function() {
             d3.select(window).on("mousemove.zoomRect", null).on("mouseup.zoomRect", null);
             d3.select(container).classed("noselect", false);
             var m = d3.mouse(e);
             m[0] = Math.max(0, Math.min(width, m[0]));
             m[1] = Math.max(0, Math.min(height, m[1]));
             if (m[0] !== origin[0] && m[1] !== origin[1]) {
               zoom.x(x.domain([origin[0], m[0]].map(x.invert).sort()))
                   .y(y.domain([origin[1], m[1]].map(y.invert).sort()));
            }
            rect.remove();
            refresh();
          }, true);
        d3.event.stopPropagation();
     });


$(window).on('resize', function() {
  // TODO: Redraw spectrum?
  console.log('Redraw spectrum SVG');
});

var loader = $('#spectrum_nval .loader')
  .css('left', width / 2 + 20 + 'px')
  .css('top', height /2 + 'px');


// Based on the temperature returns blue-red heat color
function temperatureRGB(minimum, maximum, value) {
  var x = (value - minimum) / (maximum - minimum);
  return d3.rgb(255 * x, 0, 255 * (1 - x));
}

var n_analogueID = $('#spectrum_nval').attr('data-n_analogue-id');
var n_analogueAnnotations;

// Fetch all spectrum IDs belonging to analogue
d3.json('/n_analogue/' + n_analogueID + '.json', function(error, json) {
  if (error) return console.warn(error);

  n_analogueAnnotations = json.annotations;

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
  var yTopMargin = ($.isEmptyObject(n_analogueAnnotations) ? 0 : 0.03);
  y.domain([
    d3.min(yExtents, function(e) { return e[0]; }) + 0,
    d3.max(yExtents, function(e) { return e[1]; }) + yTopMargin
  ]).nice();

  var maxTemperature = d3.max(results, function(result) { return result.temperature });
  $.each(results, function(index, result) {
    svg.append('path')
      .attr('class', 'spectrum_nval')
      .attr('id', 'spectrum_nval' + index)
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
    .text('Wavenumbers (cm');
  svg.append('text')
    .attr('class', 'x0 label part2')
    .attr('text-anchor', 'middle')
    .attr('x', width/2 + 72)
    .attr('y', x0LabelY)
    .attr('dy', -2) // dy shifts relative Y position to simulate superscript
    .text('-1');
  svg.append('text')
    .attr('class', 'x0 label part3')
    .attr('text-anchor', 'middle')
    .attr('x', width/2 + 80)
    .attr('y', x0LabelY)
    .text(')');

  // Add top X Axis label
  svg.append('text')
    .attr('class', 'x1 label')
    .attr('text-anchor', 'middle')
    .attr('x', width/2)
    .attr('y', 14 - margin.top)
    .text('Wavelength (μm)');

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
    .text('Real refractive index');



  // Draw Hover tools
  hoverLineGroup = svg.append('g').attr('class', 'hover-line');

  //zoomGroup = svg.append('g').call(zoom);


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
  for (var property in n_analogueAnnotations) {
    if (n_analogueAnnotations.hasOwnProperty(property)) {
      var labelX = x(n_analogueAnnotations[property]);
      // Find highest peak at that position
      var paths = $(container).find('path.spectrum_nval');

      // Minimum Y value because axis is reversed
      var peakY = d3.min(paths, function(spectrum_nval) {
        var lastDelta = Infinity;
        for (var i = 0; i < spectrum_nval.getTotalLength(); i+=4) {
          var delta = Math.abs(spectrum_nval.getPointAtLength(i).x - labelX);
          if (delta > lastDelta) {
            // Found X point on path, now find Y peak around this point
            return d3.min(d3.range(-140, 140), function(offset) {
              return spectrum_nval.getPointAtLength(i + offset).y;
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



function zoomFunction(){
  // create new scale ojects based on event
  var new_xScale = d3.event.transform.rescaleX(x)
  var new_yScale = d3.event.transform.rescaleY(y)
  console.log(d3.event.transform)

  // update axes
  svg.call(xAxisBottom.scale(new_xScale));
  svg.call(yAxisLeft.scale(new_yScale));

  // update circle
  spectrum_nval.attr("transform", d3.event.transform)
};


function refresh_ok() {
  svg.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")")
}

function refresh() {
  svg.select(".x0.axis").call(xAxisBottom);
  svg.select(".y0.axis").call(yAxisLeft);
  svg.select(".x1.axis").call(xAxisTop);
  svg.select(".y1.axis").call(yAxisRight);

  var new_xScale = d3.event.transform.rescaleX(x);
  var new_yScale = d3.event.transform.rescaleY(y);

  svg.call(xAxisBottom.scale(new_xScale));
  svg.call(yAxisLeft.scale(new_yScale));

  n_analogueID
       .attr('cx', function(d) {return new_xScale(d.x)})
       .attr('cy', function(d) {return new_yScale(d.y)});
  //svg.attr("transform",d3.event.transform);
  //svg.append('g').attr("transform", "transform(" + d3.event.transform + ")" + " scale(" + d3.event.scale + ")");
}


function zoomed00() {
  // create new scale ojects based on event
      var new_xScale = d3.event.transform.rescaleX(x);
      var new_yScale = d3.event.transform.rescaleY(y);
  // update axes
      svg.call(xAxis.scale(new_xScale));
      svg.call(yAxis.scale(new_yScale));
      points.data(data)
       .attr('cx', function(d) {return new_xScale(d.x)})
       .attr('cy', function(d) {return new_yScale(d.y)});
}

