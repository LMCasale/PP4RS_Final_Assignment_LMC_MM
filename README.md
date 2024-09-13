# PP4RS Final Assignment
## Determinants of Cosponsorship
### Automated Data Collection, Analysis, and Reporting

**Authors:** Lorenzo Maria Casale & Matteo Machiorlatti

This repository contains the final assignment for the Programming Practices for Research Students (PP4RS) course. The project demonstrates the use of Snakemake to automate data collection, analysis, and report generation. The workflow is fully integrated with Snakemake to ensure reproducibility and continuous integration.

## Table of Contents

- [Project Overview](#project-overview)
- [Setup Instructions](#setup-instructions)
- [Running the Workflow Locally](#running-the-workflow-locally)
- [Dependencies](#dependencies)

## Project Overview

This project involves:
1. *Data Collection*: A Python script collects legislative data from online sources and stores it in a CSV file.
2. *Data Analysis* & *Report Generation*: An R Markdown script processes and analyzes the collected data to generate insights, compiling an HTML report.
3. *Automation*: The entire process is managed using Snakemake.

## Setup Instructions

### Prerequisites

- *Git*: To clone the repository.
- *Miniconda or Anaconda*: To manage the environments and dependencies.
- *Rscript*: To run the analysis

If you need support installing any of those, you can check out this [guide](https://pp4rs.github.io/2024-uzh-installation-guide/).

## Running the Workflow Locally

To get started, fork this repository by clicking ```Fork``` on the Github page.


You can now clone the repository to your local machine. However, we suggest you to change your `directory`, before proceeding with cloning. The next command, is therefore optional:

```bash
cd the_directory_you_like_the_most
```

You can now clone this folder:
```bash
git clone https://github.com/yourusername/PP4RS_Final_Assignment_LMC_MM.git
```

Then, move to the folder you just clonated
```bash
cd PP4RS_Final_Assignment_LMC_MM
```
Create, then, a Snakemake-friendly conda environment

```bash
conda create -c conda-forge -c bioconda -n snakemake snakemake
```

Finally, run the code by:
```bash
conda activate snakemake
snakemake --cores all --use-conda --conda-frontend conda
```

**CAVEAT:** Reproducing the whole scrape would take too much time (i.e. days), therefore the ```.py``` checks that the files are present and complete (as in this case) and only combines them. If you want to check that the scraping works, you can either remove random rows from one of the ```.csv``` or delete a whole file.

## Dependencies

Both the ```.py``` and the ```.Rmd``` file that the ```snakemake``` will run without the need of further ado. Part of the automation, indeed, uses the two ```.yaml``` files in the ```workflow\envs``` folder to install all the modules/packages needed.

