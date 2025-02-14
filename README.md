# ProbDecl-monitor-py
Python reimplementation of the Probabilistic Business Constraints Monitoring. Intended for integration into next event prediction pipelines. 

The original Java implementation can be found here: https://bitbucket.org/fmmaggi/probabilisticmonitor/
Details of the monitoring approach are described in: https://doi.org/10.1007/978-3-030-58666-9_3

Relies on the following packages: ltlf2dfa, scipy, declare4py

The package ltlf2dfa requires installing MONA:

    sudo apt install make
    sudo apt install gcc
    sudo apt-get install build-essential
    sudo apt-get install flex
    wget http://www.brics.dk/mona/download/mona-1.4-18.tar.gz
    tar -xvzf mona-1.4-18.tar.gz
    cd mona-1.4/
    ./configure --enable-static --enable-shared=no
    sudo make install-strip
    mona

