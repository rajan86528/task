# URL Shortener with Expiry and Analytics

## Description

This project is a simple URL shortener system built with Python and Flask. It allows users to:
- Shorten long URLs.
- Set expiration times for shortened URLs.
- Redirect to the original URL if it has not expired.
- Track analytics, including the number of accesses, timestamps, and IP addresses for each shortened URL.

## Features

- Generate a shortened URL for a given long URL.
- Expire shortened URLs after a user-defined time (default: 24 hours).
- Redirect to the original URL if the shortened URL is still valid.
- Retrieve access logs and analytics for a specific shortened URL.

## Technology Stack

- **Backend**: Python with Flask
- **Database**: SQLite
- **Hashing**: `hashlib` for generating short URLs

---

## Prerequisites

Make sure you have the following installed on your system:
- Python 3.8 or higher
- `pip` (Python package manager)

---

## Installation

1. **Clone the repository**:
   Clone the repository to your local machine:
   ```bash
   git clone https://github.com/rajan86528/task.git
   cd task
