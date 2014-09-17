// TODO: Switch to KaTeX (replaces MathJax) when KaTeX is stable and supports
// TeX extensions like mhchem. Will increase performance.

function updateMathJax() {
  MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
}

function updatePreview() {
  if ( $("#tex-name-preview").length ) {
    var tex = $("#tex-name-preview").closest("form").find("input#name").val();
    $("#tex-name-preview").text(tex);
    updateMathJax();
  }
}

$(document).ready(function() {
  $("#tex-name-preview").closest("form").find("input#name").on('input', updatePreview);
  updatePreview();
});
