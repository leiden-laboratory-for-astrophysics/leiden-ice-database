

Refractive index calculator
===============================================================

In this section, we provide a description of the online and offline tools for calculations of the refractive index of ices. Details that are common to both cases are presented below.

The online version of this tool is available at: `https://icedb.strw.leidenuniv.nl/Kramers_Kronig <https://icedb.strw.leidenuniv.nl/Kramers_Kronig>`_.


Absorbance spectrum file
---------------------------------------------------------------
Both online and offline tools uses the absorbance spectrum of ices as input data to calculate the real and imaginary refractive index.
This file is required to be in ASCII format with two columns. The first column contains the wavenumber and the second column contains 
the absorbance data. An example is shown in Figure 1.

.. note:: The wavenumber column must be sorted in decreasing order.

.. figure:: /PNG_figs/abs_data.png
    :width: 500px
    :align: center
    :height: 300px
    :alt: alternate text
    :figclass: align-center

    Figure 1: Example of absorbance spectrum file used as input in the refractive index calculator.




Input parameters
---------------------------------------------------------------
A few input parameters are required before starting the calculations of the real and imaginary refractive index. A description of these parameters are given below:

:Ice thickness in microns: The methodology requires the ice thickness of the ice sample in units of micrometers.
:Refractive index at 670 nm: The real refractive index of the ice at 670 nm. This value is highly dependent of the composition and structure of the ice. For example, see UV_vis_refractive_index_ for values suitable for pure H\ :sub:`2`\ O ice at different temperatures.
:Refractive index of the substrate: The real refractive index of the substrate (superficie where the gases condense to form ice) is needed in this methodology. The values for typical substrates are 1.73 for CsI, 1.54 for KBr and 2.54 for ZnSe.
:MAPE: This stands for Mean Average Percentage Error. This value is used as a convergency criteria to stop the code after several iterations. See `Calculations`_ for more details.

    


Calculations
---------------------------------------------------------------
The calculations are performed by using mostly Lambert-Beer equation and Kramers-Kronig relations. More details about these two equations can be found in `Rocha & Pilling (2014) <https://www.sciencedirect.com/science/article/pii/S1386142513015060>`_ and Rocha et al. (in prep.).

Figure 2 shows an illustrations of the steps performed in the calculations of the real and imaginary refractive index of ices.

.. figure:: /PNG_figs/nkabs.png
    :width: 500px
    :align: center
    :height: 400px
    :alt: alternate text
    :figclass: align-center

    Figure 2: Flowchart of the steps involving the calculations of the real and imaginary refractive index of ices. 


.. note:: The calculations in the online version takes around 1 minute for 5000 datapoints. For larger files, we recommend to use the offline version of the code (See `Offline code`_ ). 

Refractive index viewer
---------------------------------------------------------------
Once the calculations are performed, the online tools enables the plot visualization automatically. The viewer also used `Bokeh <https://docs.bokeh.org/en/latest/>`_ to plot the results.
An example of outputs are shown in Figure 3.

.. figure:: /PNG_figs/nk_viewer.png
    :width: 750px
    :align: center
    :height: 620px
    :alt: alternate text
    :figclass: align-center

    Figure 3: Viewer showing an example of the real and imaginary refractive index.


Downloading results
---------------------------------------------------------------
The plots can be downloaded by using the *save* tool in the `Bokeh <https://docs.bokeh.org/en/latest/>`_ toolbar. To download the files with the data, please use the green button labeled **Download the refractive index**.


Offline code
---------------------------------------------------------------
The offline code can be downloaded from the Leiden Ice Database `GitHub <https://github.com/sackler-laboratory-for-astrophysics/ice-database>`_ page. Versions for Windows and Linux/Mac are available.

.. note:: In both versions, the absorbance file must be inside the folder that contains the Python script. 

*****
Windows
***** 

To run the code in Windows is as simple as double clicking on the *.exe* files. Next, the input parameters are required before proceeding with the calculation.

*****
Linux
*****

In Linux, the user can open the *.py* file to run the offline calculations. The welcome interface is shown in Figure 4.

.. figure:: /PNG_figs/offline.png
    :width: 750px
    :align: center
    :height: 620px
    :alt: alternate text
    :figclass: align-center

    Figure 4: Terminal version of the offline tool for the refractive index calculation. 




