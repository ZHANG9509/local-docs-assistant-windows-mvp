# Curl examples for ingest and query

1) Ingest a PDF

curl -X POST "http://localhost:8000/ingest" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@examples/sample.pdf;type=application/pdf"

2) Query

curl -X POST "http://localhost:8000/query" -H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" -d "q=What are the key points of the document?"
