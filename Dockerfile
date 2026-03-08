FROM python:3.12

WORKDIR /router

COPY req.txt .

RUN pip install --no-cache-dir -r req.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]                





#base image
#creates  directory inside the container where commands will run. 

# cpoy/add are two functions which perform the same operation. 
# copy is used to copy files from host to container and add does same with extra functionalities like unzip fetch url etc..
#copies req.txt from host to container
#installs dependencies
#copies the rest of the code
#exposes the port
#runs the server