oneShot() {
    curl -X POST "http://0.0.0.0:5000/message" -H  "accept: application/json" -H  "X-Openpush-Key: -xgF5P3rZPkpPhjZC_B2PY5vV5Q" -H  "Content-Type: application/json" -d "{\"body\":\"Long message text goes here...\",\"priority\":\"NORMAL\",\"subject\":\"Message Subject\"}"  
}
