# 1. Create secret with username, password and database name
oc create secret generic mongo-credentials `
  --from-literal=MONGO_INITDB_ROOT_USERNAME=appuser `
  --from-literal=MONGO_INITDB_ROOT_PASSWORD='S3curePass#123' `
  --from-literal=MONGO_INITDB_DATABASE=mydb

# 2. Create new app (deployment + imagestream + service) for MongoDB
oc new-app --docker-image=docker.io/library/mongo:7.0 --name=mongo-app


# 3. Inject environment variables from the secret into the deployment
oc set env deployment/mongo-app --from=secret/mongo-credentials

# 4. Verify pod and logs
oc get pods
oc logs deployment/mongo-app

# 5. Create a persistent volume claim for MongoDB
oc apply -f pvc.yaml

# delete the existing volume if it exists
oc set volume deployment/mongo-app `
  --remove --name=mongo-app-volume-1

# 6. Set the volume for the MongoDB deployment
oc set volume deployment/mongo-app `
  --add --name=mongo-storage `
  --mount-path=/data/db `
  --claim-name=mongo-pvc

# 7. Verify the volume is set correctly

# Administering MongoDB
mongosh -u "$MONGO_INITDB_ROOT_USERNAME" -p "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin

# Connect to MongoDB using the root user
use mydb
db.createUser({
  user: "appuser",
  pwd: "StrongAppPass123",
  roles: [ { role: "readWrite", db: "mydb" } ]
})




# FastAPI App with MongoDB
# 1. Build the FastAPI Docker image locally (tag as version 0.3)
docker build -t eligil/fastapi-app:0.7 .

# 2. Push the image to DockerHub
docker push eligil/fastapi-app:0.7

# 3. Create new app in OpenShift from DockerHub image
oc new-app eligil/fastapi-app:0.7 --name=fastapi-application

# 4. Set environment variables for MongoDB connection
oc create secret generic appuser-credentials \
  --from-literal=MONGO_USERNAME=appuser \
  --from-literal=MONGO_PASSWORD=StrongAppPass123 \
  -n eligil-dev


# 5. Inject environment variables from existing secret (mongo-credentials)
oc set env deployment/fastapi-application --from=secret/appuser-credentials

# 6. Add extra static vars (host + port)
oc set env deployment/fastapi-application `
  MONGO_HOST=mongo-app `
  MONGO_PORT=27017

# 7. Verify pods are running
oc get pods

# 8. Stream logs to verify FastAPI starts correctly
oc logs -f deployment/fastapi-application

# 9. Expose the FastAPI service to create a route
oc expose service/fastapi-application

# 10. Get the route URL to access the FastAPI app
oc get route fastapi-application




