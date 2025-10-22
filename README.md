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

