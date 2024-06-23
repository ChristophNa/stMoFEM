#!/bin/sh

# Run the background Python script
python3 app/tests/hello.py &

# Run the Streamlit app
streamlit run app/tests/app.py --server.port=8501 --server.address=0.0.0.0 #> dev/null
