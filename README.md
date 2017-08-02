# CTBB Pipeline

   * [What is CTBB Pipeline?](#what-is-ctbb-pipeline)
   * [Installation](#installation)
   * [Quickstart](#quickstart)
   * [What does CTBB Pipeline do?](#what-does-ctbb-pipeline-do)
   * [What does CTBB Pipeline <em>not</em> do?](#what-does-ctbb-pipeline-not-do)
   * [More information](#more-information)

## What is CTBB Pipeline?

CTBB Pipeline is GPU queuing software intended for use on multi-GPU workstations.  It was developed originally for high-through image reconstruction and quantitative imaging analysis, however is generalizable to any task that requires execution of GPU programs.

CTBB Pipeline is tightly tied to the development of the free projection [FreeCT_wFBP](http://cvib.ucla.edu/freect/) (a fork of the also free project [CTBangBang](https://github.com/captnjohnny1618/CTBangBang))

## Installation

CTBB Pipeline is installed most readily via pip3.  Download or clone the repository to your machine and run:

```
sudo pip3 install /path/to/pipeline/CTBB_Pipeline_Package/
```

*Note that some of the dependencies will require root permission to install if not already installed.*

## Quickstart

*COMING SOON* -jh 2017-08-02

## What does CTBB Pipeline do?

### Job Queuing

CTBB Pipeline is a suite of python scripts that manages execution of GPU-enabled jobs on a single machine.  The jobs can be multi-stage, and a mixture of GPU enabled steps on CPU only.  It is designed to maximize the usage of computing resources available on the machine.

### Computing at scale (sort of)

CTBB Pipeline automatically scales execution to utilize all available CUDA-enabled devices on a machine.  If you have two, three, four, eight, etc. GPUs in a given machine, it will concurrently manage and run two, four, or eight jobs on that machine, respectively.

### Metrics

CTBB Pipeline also has a script for data-mining performance metrics from the generated log files.  This is still a work in progress, but can be helpful for optimizing mulistage execution.

### Easily rerun failed jobs

Occasionally things go wrong.  Was it your computer?  Kernel panic?  Your fault?  It can be quite a challenge to track down this information.  CTBB Pipeline comes with a script to help you find jobs that failed and requeue them to easily troubleshoot what could have gone wrong.

## What does CTBB Pipeline *not* do?

### Multi GPU jobs

If program requires more than one GPU, CTBB Pipeline probably won't work.  We'll look into this as the need arises, however at present, it's almost always more easier, cheaper, and more portable to target one GPU and run jobs in parallel.

### Cluster computing

What sets CTBB Pipeline apart is its management of multiple devices within a single machine.  There are already a lot of cluster management tools (e.g. Ganglia, HTCondor, Bright, etc.).  If you need a cluster, check those out.  At present, there are no plans to extend CTBB Pipeline in this direction.

## More information

### Background

"The Pipeline" is a combination of the tools in this repository and our free (libre), open-source reconstruction projects in FreeCT.  All of the code was originally developed for the investigation of quantitative CT imaging (hence the parameters found when parsing config files and specific program calls of the queue items script).  The pipeline has already been used extensively for abstracts and multiple manuscripts are under development.  Some recent examples include:

* J Hoffman, M Wahi-Anwar , N Emaminejad , G Kim , M Brown , M McNitt-Gray. *A Fully-Automated, High-Throughput, Reconstruction and Analysis Pipeline for Quantitative Imaging in CT.* AAPM Annual Meeting. July 31-Aug 3, 2017.

* J Hoffman, G Kim, J Goldin, M Brown, M McNitt-Gray. *A Pilot Study Evaluating the Robustness of Density Mask Scoring (RA-950), a Quantitative Measure of Chronic Obstructive Pulmonary Disease, to CT Parameter Selection Using a High-Throughput, Automated, Computational Research Pipeline*. AAPM Annual Meeting. July 31-Aug 3, 2017.

* N Emaminejad, M Wahi-Anwar, J Hoffman, A Sultan, K Ruchalski, G Kim, J Goldin, M Brown, M McNitt-Gray. *Evaluation of CAD Nodule Detection Performance in Low Dose CT Lung Cancer Screening Across a Range of Dose Levels, Slice Thicknesses and Reconstruction Kernels*. AAPM Annual Meeting. July 31-Aug 3, 2017.

* T Zhao, J Hoffman, M McNitt-Gray, D Ruan. *Low-Dose CT Image Denoising Using An Optimized Wiener Filter in the BM3D Algorithm*. AAPM Annual Meeting. July 31-Aug 3, 2017.

## Contact

Comments or questions should be addressed to John at jmhoffman@mednet.ucla.edu or freect.project@gmail.com.

Any feedback is welcome and will help us further develop and improve the software!

## License

GNU GPL v3.0

Copyright 2017 John Hoffman