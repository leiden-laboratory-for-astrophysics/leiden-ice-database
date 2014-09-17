$(function() {
  var t1 = new Date().getTime();
  $.get('/spectrum/1', function(data) {
    console.log('Fetched spectrum #1 (length: ' + data.length + ')');
    var t2 = new Date().getTime();
    console.log('It took ' + (t2 - t1) + ' ms');
    $('#spectrum').html(data);
    MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
  });
});
