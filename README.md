# Vendors Demo

A Streamlit-based application for managing vendor price sheets and generating order guides.

## Features

- Add and manage vendors
- Upload price sheets (CSV format) for each vendor
- Generate combined order guides
- Interactive view with searching, filtering, and sorting capabilities
- Cloud deployment ready

## Getting Started

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit application:
```bash
streamlit run src/app.py
```

## Application Workflow

1. **Add Vendor**: Enter vendor details through a simple form
2. **Upload Price Sheet**: Select a vendor and upload their CSV price sheet
3. **Generate Order Guide**: Combine all uploaded price sheets into a single guide
4. **View Order Guide**: Interactive table with search and filter capabilities

## Requirements

- Python 3.9+
- Streamlit
- Pandas
- Streamlit-AgGrid

## Project Structure

```
vendors-demo/
├── src/
│   └── app.py          # Main application file
├── requirements.txt    # Project dependencies
├── runtime.txt        # Python version specification
└── README.md          # Project documentation
```

## Deployment

This application is configured for deployment on Streamlit Cloud. Visit the deployed version at:
[Vendors Demo App](https://streamlit.io/cloud) (URL will be updated after deployment)