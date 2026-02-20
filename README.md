# Shivshakti Traders – Business Platform

Live Website:  
👉 https://shivshakti-traders.onrender.com

---

## Overview

Shivshakti Traders is a Django-based business platform combining:

- Public product catalog
- Enquiry workflows
- Internal dashboard
- REST API with JWT authentication
- Audit logging
- Production-ready deployment setup

Built as a modular Django monolith with clear app boundaries.

---

## Architecture

Apps:

- core – Public pages, sitemap, shared middleware  
- products – Product catalog & categories  
- enquiries – General & product enquiries  
- accounts – Authentication & hardened admin flow  
- dashboard – Internal business dashboard  
- api – DRF endpoints with JWT  
- auditlog – Request & signal-based logging  

---

## Tech Stack

- Django 5
- Django REST Framework
- SimpleJWT
- PostgreSQL (production)
- Cloudinary (media storage)
- Gunicorn
- WhiteNoise
- Tailwind (frontend styling)

---

## Security Highlights

- Hidden admin route
- Custom login flow
- Rate limiting
- JWT rotation & blacklist
- Secure cookies in production
- CSP middleware
- Strict security headers

---

## Deployment

Designed for cloud platforms such as Render.  
Uses split settings (development/production) and environment-based configuration.
