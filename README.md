# Freelance Gig Platform API

This is a **Freelance Gig Platform API**. It’s a Django thing with WebSockets for bidding, fake payments, and some rep scoring.

## What’s It Do?
- Bidding in real-time with WebSockets.
- Fake wallet for payments.
- Rep scores from reviews, thanks to Celery.
- API for gigs and bids.

## Stuff I Used
- Django, REST bits, Channels
- PostgreSQL, Celery, Redis
- Render (free tier pain)

## How to Run It
1. Grab it: `git clone https://github.com/yaya-soumah/freelance-platform-api.git`
2. Add `.env` with database, Redis, and secret keys.
3. Do `pip install -r requirements.txt`
4. Set up: `python manage.py migrate`
5. Run it with `./start-celery.sh` or whatever.

## Mess With It
- Check `http://localhost:8000/api/`.
- Try `POST /api/gigs/` with `{"title": "Code This", "budget": 50}`.
- WebSocket’s at `wss://localhost:8000/ws/gig/1/`.

Yaya Soumah built this. More at [github.com/yaya-soumah](https://github.com/yaya-soumah).