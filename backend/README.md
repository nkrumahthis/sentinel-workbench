# Workbench Backend Service

Written in Flask

## Run locally

```bash
cd backend
python3 -m venv .venv
pip install -r requirements.txt
flask --app backend/app run -p 5001
```

## Generate more data

```bash
python cloudtrail_data_generator.py
```

Then manually merge the new data from `tmp/mock_cloudtrail.json` into `tmp/test_cloudtrail.json`.

## Test

```bash
python -m unittest tests/test*
```
