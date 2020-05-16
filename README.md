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

## How project works
  * It is a monorepository, which consists of 3 services: `Client`, `Server` and `Dashboard` .
  * `Server` is a I/O multiplexer, which fetches in real-time latest Donal Trump tweets with `Twitter API` and whenever `Client` is a ready for socket communication, sends tweets. (P.S. there could be multiple `Clients`).
  * `Client` is a Spark Streaming platform which extracts tweets, transform (find all mentions in text) batch by batch and post top 10 most mentioned users to `Dashboard`.
  * `Dashboard` is a `Flask` application, which using AJAX gets those results and generates dashboard in real-time using `Chart.js`
  

