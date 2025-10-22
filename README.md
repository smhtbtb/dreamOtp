# Dream Otp
A minimal Django project for OTP-based authentication via email or phone.

## Setup

```bash
git clone <repo_url>
cd dreamOtp
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```


## Run
```bash
python manage.py migrate
python manage.py runserver
```

## Endpoints
`POST /api/v1/request-otp/`
```json
{
  "identifier": "test@example.com"
}
```
`POST /api/v1/verify-otp/`
```json
{
  "identifier": "test@example.com",
  "code": "123456"
}
```
If the code verified successfully, created user will log in automatically.

## Testing
This project includes both **unit tests** (for OTP logic) and **API tests** (for the DRF endpoints).

### Run all tests

Activate the virtual environment and run:

```bash
pytest -v
```

### Test layers
| Layer | File                              | Purpose                                               |
| ----- | --------------------------------- | ----------------------------------------------------- |
| Unit  | `otp_auth/tests/test_services.py` | Tests OTP creation, expiration, and validation logic  |
| API   | `otp_auth/tests/test_api_otp.py`  | Tests DRF endpoints for requesting and verifying OTPs |

