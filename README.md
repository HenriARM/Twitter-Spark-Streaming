# Twitter-Spark-Streaming
Most often mentioned users by Donald Trump on Twitter

![](./screening.gif)

## Prerequisites

* python >3.7
* npm

## How to run

0. Install python dependencies for all services
  ```bash
    pip install -r requirements.txt
  ```  
1. Run server
  ```bash
    cd server; python spark-server.py
  ```
2. Run client
  ```bash
    cd client; python spark-client.py
  ```
3. Run dashboard
  ```bash
    cd dashboard; 
    npm i;
    python app.py
  ```

How project works (Real-time, mono repo, selector, multiple conenction, another user to stream)
