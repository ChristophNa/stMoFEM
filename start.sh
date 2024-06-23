#!/bin/sh

# Run the background Python script
python app/MoFEM/runSimulation.py &

# Run the Streamlit app
streamlit run app/0_🏡_Home.py --server.port=8501 --server.address=0.0.0.0
