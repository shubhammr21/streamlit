#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

streamlit run Streamlit_App.py --server.port=8501 --server.address=0.0.0.0