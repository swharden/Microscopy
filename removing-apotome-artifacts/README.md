# Removing ApoTome Artifacts with ImageJ

The [Zeiss ApoTome](http://zeiss-campus.magnet.fsu.edu/tutorials/opticalsectioning/apotome/indexflash.html) is an optical instrument which can be placed in the light path of a traditional epifluorescence microscope to reduce out-of-focus light and enhance optional sectioning. This is achieved by rapidly tilting a glass plate with a grid on it and analyzing the resulting image in real time to create an image which maximally excites and captures light at a single optical section (calculated from at least 3 raw images acquired at different tilt angles).

A poorly-calibrated ApoTome will produce imaging artifacts which appear as horizontal lines on the final image (in addition to increased collection of out-of-focus light). The ApoTome must be calibrated separately for every filter cube / lens combination. An ApoTome on a microscope with 4 filter cubes and 5 lenses must be calibrated 20 times. Calibration is a two-step process, requiring phase calibration and a grid calibration. Recommended calibration tutorials are listed here:
* [Imaging Associates - ApoTome Calibration Guide](http://www.usask.ca/biology/scopes/ApoTome%20Takeoff%20Guide%20%28calibration%29.pdf)
* [Queensland Brain Institute Microscopy - ApoTome Users Guide](http://web.qbi.uq.edu.au/microscopy/wp-content/uploads/2011/pdfs/Apotome_Guide.pdf)

Although ApoTome artifact lines can be reduced by improving calibration, images with these artifacts can be improved with ImageJ. Since the artifacts are typically horizontal lines with a regular distance between them, they are ideally isolated (and eliminated) in the frequency domain. The conversion of linear data into a frequency domain can be accomplished using the [Fast Fourier transform](https://en.wikipedia.org/wiki/Fast_Fourier_transform) (FFT), and this has [special uses for image processing when a 2D FFT is used](http://www.robots.ox.ac.uk/~az/lectures/ia/lect2.pdf). In our case we will convert the artifact-laden image to the frequency domain, identify the frequencies underlying the artifact, and perform an inverse FFT (iFFT) to create an original image with reduced artifacts.

## Reduction of Artifacts Manually
pics

## ApoTome Artifact Reduction ImageJ Macro
```java
test
```
