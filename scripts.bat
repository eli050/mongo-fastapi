oc create secret generic mongo-credentials \
  --from-literal=MONGODB_USERNAME=appuser \
  --from-literal=MONGODB_PASSWORD='S3curePass#123' \
  --from-literal=MONGODB_DATABASE=mydb \
  --from-literal=MONGODB_ROOT_PASSWORD='RootS3cure#123'


oc get secret mongo-credentials -o yaml

oc new-app --name=mongo --docker-image=bitnami/mongodb:7.0 -e MONGODB_ENABLE_JOURNAL=true

oc set env deployment/mongo --from=secret/mongo-credentials

oc exec -it mongo-75ccc7bcdb-c2c8l -- bash

mongosh -u root -p 'RootS3cure#123' --authenticationDatabase admin mydb --eval "db.runCommand({ ping: 1 })"


use mydb
db.createUser({
  user: "appuser",
  pwd: "S3curePass#123",
  roles: [ { role: "readWrite", db: "mydb" } ]
})

oc new-app . --name=fastapi-app

oc set env deployment/fastapi-app --from=secret/mongo-credentials
oc set env deployment/fastapi-app MONGO_HOST=mongo MONGO_PORT=27017

# 1. יצירת BuildConfig מהתיקייה (אסטרטגיית Docker)
oc new-build --name=fastapi-app --strategy=docker --binary

# 2. התחלת build מתוך הקבצים המקומיים
oc start-build fastapi-app --from-dir=. --follow

# 3. יצירת Deployment + Service מה־ImageStream
oc new-app fastapi-app

# 4. חשיפת Route (URL חיצוני)
oc expose service fastapi-app
