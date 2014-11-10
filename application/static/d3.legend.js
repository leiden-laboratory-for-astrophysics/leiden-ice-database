// d3.legend.js 
// 
// 2014 - Modified by Bart Olsthoorn
// Original by: 2012 ziggy.jonsson.nyc@gmail.com
// 
// MIT license

(function() {
d3.legend = function(g) {
  g.each(function() {
    var g = d3.select(this),
        items = {},
        svg = d3.select('#spectrum'),
        legendPadding = 5;

    var lb = g.append('rect').attr('class', 'legend-box')
      .style('fill', 'white')
      .on('mouseenter', function() {
        d3.select('g.hover-line').style('opacity', 0);
      })
      .on('mouseleave', function() {
        d3.select('g.hover-line').style('opacity', 1);
      });

    var li = g.append('g').attr('class', 'legend-items')

    svg.selectAll('[data-legend]').each(function() {
        var self = d3.select(this)
        items[self.attr('data-legend')] = {
          pos : self.attr('data-legend-pos'),
          color : self.style('stroke'),
          index: self.attr('data-index')
        }
      })

    items = d3.entries(items).sort(function(a,b) { return b.value.pos-a.value.pos})

    var legendItems = li.selectAll('g.legend-item')
      .data(items)
      .enter()
      .append('g')
      .attr('class', 'legend-item')
      .attr('data-index', function(d) { return d.value.index; })
      .on('mouseenter', function() {
        var index = d3.select(this).attr('data-index');
        d3.select(this).select('text').style('font-weight', 'bold');
        d3.selectAll('path.spectrum').classed('unfocus', true);
        d3.select('path#spectrum'+index).classed('unfocus', false).classed('focus', true);
        d3.select('g.hover-line').style('opacity', 0);
      })
      .on('mouseleave', function() {
        var index = d3.select(this).attr('data-index');
        d3.select(this).select('text').style('font-weight', 'normal');
        d3.selectAll('path.spectrum').classed('unfocus', false);
        d3.select('path#spectrum'+index).classed('focus', false);
        d3.select('g.hover-line').style('opacity', 1);
      });

    legendItems
      .append('text')
      .attr('y',function(d,i) { return i+'em'})
      .attr('x','1em')
      .text(function(d) { ;return d.key})
   
    legendItems
      .append('circle')
      .attr('cy',function(d,i) { return i-0.35+'em'})
      .attr('data-name', function(d) { return d.key; })
      .attr('cx',0)
      .attr('r','0.4em')
      .style("fill",function(d) { return d.value.color})  
   
    // Reposition and resize the box
    var lbbox = li[0][0].getBBox()  
    lb.attr("x",(lbbox.x-legendPadding))
        .attr("y",(lbbox.y-legendPadding))
        .attr("height",(lbbox.height+2*legendPadding))
        .attr("width",(lbbox.width+2*legendPadding))

    legendItems
      .append('rect')
        .attr('y',function(d,i) { return i-0.8+'em'})
        .style('fill', 'none')  
        .attr('pointer-events', 'visible')
        .attr('x', 0)
        .attr('width', (lbbox.width))
        .attr('height', '1em')
  })
  return g
}
})()
