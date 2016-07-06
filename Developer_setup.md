# ODM2 Streaming Data Loader Developer Environment Setup

1. install [miniconda](http://repo.continuum.io/miniconda/index.html) using the appropriate setup script.
2. download the list of [requirements](https://github.com/ODM2/ODM2StreamingDataLoader/blob/master/SDLReq.yml)
3. Setup a new conda environment using python 2.7 (run from windows terminal) :
    ```
    $ conda env create -f SDLReq.yml
    
    $ source activate SDL-env
    ```
4. Step 3 will take a while, so go get something from the vending machine.
5. Download source code from [github](https://github.com/ODM2/ODM2StreamingDataLoader/archive/master.zip)
6. unzip into your users folder (or preferred working directory)
7. Test the new environment by running:
    ```
    $ python ODM2StreamingDataLoader/src/wizard/controller/frmMain.py
    ```
 

### Feedback
Comments and concenrns can be posted on our GitHib page: https://github.com/ODM2/ODM2StreamingDataLoader/issues.
