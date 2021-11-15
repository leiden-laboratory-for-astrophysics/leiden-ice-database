

Infrared spectrum
===============================================================

In this section we provide technical details on how to explore the IR spectrum of ices within the Leiden Ice database.

Bokeh plot of infrared spectrum
---------------------------------------------------------------
`Bokeh <https://docs.bokeh.org/en/latest/>`_ is used to provide interactive visualization of IR spectra in the Leiden Ice Database. A series of options are further detailed below:

.. figure:: /PNG_figs/Spec_view.png
    :width: 800px
    :align: center
    :height: 450px
    :alt: alternate text
    :figclass: align-center

    Infrared spectra of H\ :sub:`2`\ O ice at different temperatures.

*****
Data point information
*****

A hover dynamically shows information for each datapoint, e.g., wavenumber, wavelength and absorbance. Also, the spectrum at different temperatures are highlighted by passing the hover across them.

*****
Interactive legend
*****

Another interesting feature from Bokeh is the interactive legend. By clicking on the temperature values, the user can hide the spectra and click again to show the spectra.

*****
Toolbar
*****

The toolbar on the right side provides further options to interact with the plot. Among the options, the user can zoom-in and zoom-out one specific region of the spectrum.
Wheel zoom is also available in this plot that is centered on the cursor position. All the changes can be saved using the floppy icon or restored to the original plot with the circle icon. 

*****
Vibrational modes
*****

The annotations containing the vibrational modes are also indicated in the plot. A badge is available at the bottom of the plot to hide those annotations.


Download data
---------------------------------------------------------------
All the spectra in the database are available for download in ASCII format. Each spectrum can be downloaded separately or all together in a zip file.

.. figure:: /PNG_figs/Download.png
    :width: 500px
    :align: center
    :height: 300px
    :alt: alternate text
    :figclass: align-center

    Example of the download section for obtaining the data from the database.

